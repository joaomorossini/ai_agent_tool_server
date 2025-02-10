"""
Service for managing scheduled jobs.
"""
from datetime import datetime, timedelta, timezone
import json
import logging
from typing import List, Optional, Dict, Any, AsyncGenerator
from uuid import UUID
import asyncio
import asyncpg
from asyncpg.pool import Pool
from croniter import croniter
from dateutil.parser import parse as parse_datetime
from dateutil.relativedelta import relativedelta
from functools import wraps
from contextlib import asynccontextmanager

from app.models.scheduler_models import (
    ScheduledJob, JobExecution, JobType, JobStatus, ExecutionStatus,
    OneTimeSchedule, IntervalSchedule, CronSchedule, JobParameters
)
from app.database import get_db_connection

# Configure logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def with_timeout(timeout_seconds: int = 300):
    """Decorator to add timeout to async functions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                logger.error(
                    f"Function {func.__name__} timed out after {timeout_seconds} seconds"
                )
                raise TimeoutError(
                    f"Operation timed out after {timeout_seconds} seconds"
                )
        return wrapper
    return decorator

class SchedulerService:
    """Service for managing scheduled jobs."""

    def __init__(self, default_timeout: int = 300, db_pool: Optional[Pool] = None):
        """Initialize the scheduler service."""
        self._running = False
        self._jobs: Dict[UUID, asyncio.Task] = {}
        self._scheduler_task: Optional[asyncio.Task] = None
        self._job_handlers: Dict[str, callable] = {}
        self._default_timeout = default_timeout
        self._db_pool = db_pool
        logger.info("Initialized SchedulerService with default timeout: %d seconds",
                   default_timeout)

    @asynccontextmanager
    async def _get_db_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get a database connection."""
        if self._db_pool:
            async with self._db_pool.acquire() as conn:
                yield conn
        else:
            async with get_db_connection() as conn:
                yield conn

    def register_handler(self, action: str, handler: callable, timeout: Optional[int] = None) -> None:
        """Register a handler for a specific job action."""
        if timeout is None:
            timeout = self._default_timeout
        
        @with_timeout(timeout)
        async def wrapped_handler(*args, **kwargs):
            return await handler(*args, **kwargs)
        
        self._job_handlers[action] = wrapped_handler
        logger.info("Registered handler for action '%s' with timeout %d seconds",
                   action, timeout)

    @with_timeout(5)  # Short timeout for startup
    async def start(self) -> None:
        """Start the scheduler service."""
        if self._running:
            logger.warning("Attempted to start already running scheduler service")
            return

        self._running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("Scheduler service started")

    @with_timeout(30)  # Longer timeout for shutdown
    async def stop(self) -> None:
        """Stop the scheduler service."""
        if not self._running:
            logger.warning("Attempted to stop already stopped scheduler service")
            return

        logger.info("Stopping scheduler service...")
        self._running = False
        
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
            self._scheduler_task = None

        # Cancel all running jobs
        job_count = len(self._jobs)
        if job_count > 0:
            logger.info("Cancelling %d running jobs...", job_count)
            for job_id, task in self._jobs.items():
                logger.debug("Cancelling job %s", job_id)
                task.cancel()
            await asyncio.gather(*self._jobs.values(), return_exceptions=True)
            self._jobs.clear()
        
        logger.info("Scheduler service stopped successfully")

    async def _scheduler_loop(self) -> None:
        """Main scheduler loop that checks for and executes due jobs."""
        logger.info("Starting scheduler loop")
        while self._running:
            try:
                await self._check_and_execute_jobs()
            except Exception as e:
                logger.error("Error in scheduler loop: %s", str(e), exc_info=True)
            await asyncio.sleep(1)  # Check every second
        logger.info("Scheduler loop ended")

    @with_timeout(10)  # Reasonable timeout for job checking
    async def _check_and_execute_jobs(self) -> None:
        """Check for jobs that are due and execute them."""
        async with self._get_db_connection() as conn:
            # Get all active jobs that are due
            query = """
                SELECT * FROM jobs
                WHERE status = $1
                AND next_run_time <= CURRENT_TIMESTAMP
                FOR UPDATE SKIP LOCKED
            """
            rows = await conn.fetch(query, JobStatus.ACTIVE.value)

            for row in rows:
                job = self._row_to_job(row)
                if job.id not in self._jobs:
                    logger.info("Starting execution of job %s (%s)", job.id, job.name)
                    self._jobs[job.id] = asyncio.create_task(
                        self._execute_job(job)
                    )
                else:
                    logger.debug("Job %s is already running", job.id)

    async def _execute_job(self, job: ScheduledJob) -> None:
        """Execute a job and update its status."""
        try:
            # Get handler for job action
            handler = self._job_handlers.get(job.parameters.action)
            if not handler:
                logger.error(f"No handler found for action: {job.parameters.action}")
                return

            # Execute handler with job parameters
            result = await handler(job.parameters.params)

            # Create execution record
            execution = JobExecution(
                job_id=job.id,
                status=ExecutionStatus.COMPLETED,
                result=result,  # Store result directly as a dict
                started_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc),
            )
            await self._create_execution_record(execution)

            # Update job status and next run time
            now = datetime.now(timezone.utc)
            async with self._get_db_connection() as conn:
                if job.type == JobType.ONE_TIME:
                    # One-time jobs are marked as completed after execution
                    await conn.execute(
                        """
                        UPDATE jobs 
                        SET status = $1, next_run_time = NULL, last_run_at = $2, updated_at = $2
                        WHERE id = $3
                        """,
                        JobStatus.COMPLETED.value,
                        now,
                        job.id,
                    )
                else:
                    # Calculate next run time for recurring jobs
                    next_run = None
                    if job.type == JobType.INTERVAL:
                        schedule = IntervalSchedule(**job.schedule)
                        next_run = now + timedelta(seconds=schedule.interval_seconds)
                    elif job.type == JobType.CRON:
                        schedule = CronSchedule(**job.schedule)
                        next_run = croniter(schedule.expression, now).get_next(datetime)

                    # Update last run time and next run time
                    await conn.execute(
                        """
                        UPDATE jobs 
                        SET last_run_at = $1, next_run_time = $2, updated_at = $1
                        WHERE id = $3
                        """,
                        now,
                        next_run,
                        job.id,
                    )

        except Exception as e:
            logger.error(f"Error executing job {job.id}: {e}")
            # Create failed execution record
            execution = JobExecution(
                job_id=job.id,
                status=ExecutionStatus.FAILED,
                error=str(e),
                started_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc),
            )
            await self._create_execution_record(execution)

        finally:
            # Clean up the job from running jobs dict
            if job.id in self._jobs:
                del self._jobs[job.id]

    async def create_job(self, job: ScheduledJob) -> ScheduledJob:
        """Create a new scheduled job."""
        # Validate job handler exists
        if job.parameters.action not in self._job_handlers:
            raise ValueError(f"No handler registered for action: {job.parameters.action}")

        # For one-time jobs, calculate next_run_time from schedule
        if job.type == JobType.ONE_TIME:
            schedule = OneTimeSchedule(**job.schedule)
            job.next_run_time = schedule.run_at

        # Set job status to ACTIVE
        job.status = JobStatus.ACTIVE

        # Insert job into database
        async with self._get_db_connection() as conn:
            query = """
                INSERT INTO jobs (
                    name, type, status, schedule, parameters, next_run_time
                ) VALUES (
                    $1, $2, $3, $4, $5, $6
                )
                RETURNING id, created_at, updated_at
            """
            row = await conn.fetchrow(
                query,
                job.name,
                job.type.value,
                job.status.value,
                json.dumps(job.schedule),
                json.dumps(job.parameters.model_dump()),  # Using model_dump instead of dict
                job.next_run_time
            )

            job.id = row["id"]
            job.created_at = row["created_at"]
            job.updated_at = row["updated_at"]

            return job

    async def get_job(self, job_id: UUID) -> Optional[ScheduledJob]:
        """Get a job by ID."""
        async with self._get_db_connection() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM jobs WHERE id = $1",
                job_id
            )
            return self._row_to_job(row) if row else None

    async def list_jobs(self) -> List[ScheduledJob]:
        """List all jobs."""
        async with self._get_db_connection() as conn:
            rows = await conn.fetch("SELECT * FROM jobs")
            return [self._row_to_job(row) for row in rows]

    async def cancel_job(self, job_id: UUID) -> bool:
        """Cancel a job."""
        async with self._get_db_connection() as conn:
            result = await conn.execute(
                """
                UPDATE jobs 
                SET status = $1, updated_at = CURRENT_TIMESTAMP
                WHERE id = $2 AND status != $3
                """,
                JobStatus.CANCELLED.value,
                job_id,
                JobStatus.COMPLETED.value
            )
            return result == "UPDATE 1"

    async def get_job_executions(self, job_id: UUID) -> List[JobExecution]:
        """Get execution history for a job."""
        async with self._get_db_connection() as conn:
            rows = await conn.fetch(
                "SELECT * FROM job_executions WHERE job_id = $1 ORDER BY created_at DESC",
                job_id
            )
            return [self._row_to_execution(row) for row in rows]

    async def _create_execution_record(self, execution: JobExecution) -> None:
        """Create a job execution record."""
        async with self._get_db_connection() as conn:
            await conn.execute(
                """
                INSERT INTO job_executions (
                    job_id, status, started_at, completed_at, error, result
                ) VALUES (
                    $1, $2, $3, $4, $5, $6
                )
                """,
                execution.job_id,
                execution.status.value,
                execution.started_at,
                execution.completed_at,
                execution.error,
                json.dumps(execution.result) if execution.result is not None else None  # Convert dict to JSON for storage
            )

    def _row_to_job(self, row: Dict[str, Any]) -> ScheduledJob:
        """Convert a database row to a ScheduledJob model."""
        # Parse parameters from JSON
        parameters_dict = json.loads(row["parameters"])
        schedule_dict = json.loads(row["schedule"])
        job_type = JobType(row["type"])

        # Create the appropriate schedule based on job type
        if job_type == JobType.ONE_TIME:
            schedule = OneTimeSchedule(**schedule_dict)
        elif job_type == JobType.INTERVAL:
            schedule = IntervalSchedule(**schedule_dict)
        else:  # job_type == JobType.CRON
            schedule = CronSchedule(**schedule_dict)

        return ScheduledJob(
            id=row["id"],
            name=row["name"],
            type=job_type,
            status=JobStatus(row["status"]),
            schedule=schedule.model_dump(),
            parameters=JobParameters(**parameters_dict),
            next_run_time=row["next_run_time"],
            last_run_at=row.get("last_run_at"),  # Use get() to handle NULL values
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _row_to_execution(self, row: Dict[str, Any]) -> JobExecution:
        """Convert a database row to a JobExecution model."""
        return JobExecution(
            id=row["id"],
            job_id=row["job_id"],
            status=ExecutionStatus(row["status"]),
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            error=row["error"],
            result=json.loads(row["result"]) if row["result"] else None  # Convert JSON string to dict if not None
        ) 
