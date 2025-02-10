"""
Unit tests for the scheduler service.
"""
import asyncio
from datetime import datetime, timedelta, timezone
import pytest
import pytest_asyncio
from uuid import UUID
from typing import AsyncGenerator

from app.models.scheduler_models import (
    ScheduledJob, JobType, JobStatus, ExecutionStatus,
    OneTimeSchedule, JobParameters
)
from app.services.scheduler_service import SchedulerService
from asyncpg.pool import Pool

@pytest_asyncio.fixture
async def scheduler(db_pool: Pool) -> AsyncGenerator[SchedulerService, None]:
    """Get a scheduler service instance."""
    scheduler = SchedulerService(db_pool=db_pool)
    
    # Register test handler
    async def test_handler(params: dict):
        return params
    scheduler.register_handler("test", test_handler)
    
    await scheduler.start()
    try:
        yield scheduler
    finally:
        await scheduler.stop()

@pytest.fixture
def one_time_job():
    """Fixture for a one-time job."""
    return ScheduledJob(
        name="Test One-time Job",
        type=JobType.ONE_TIME,
        schedule={
            "run_at": (datetime.now(timezone.utc) + timedelta(seconds=2)).isoformat(),
            "timezone": "UTC"
        },
        parameters=JobParameters(
            action="test",
            params={"message": "test message"}
        )
    )

@pytest.mark.asyncio
async def test_create_one_time_job(scheduler: SchedulerService, one_time_job: ScheduledJob):
    """Test creating a one-time job."""
    # Create job
    job = await scheduler.create_job(one_time_job)
    
    # Verify job was created correctly
    assert job.id is not None
    assert job.status == JobStatus.ACTIVE
    assert job.type == JobType.ONE_TIME
    assert job.next_run_time is not None

    # Get job and verify
    fetched_job = await scheduler.get_job(job.id)
    assert fetched_job is not None
    assert fetched_job.id == job.id
    assert fetched_job.status == JobStatus.ACTIVE

@pytest.mark.asyncio
async def test_one_time_job_execution(scheduler: SchedulerService, one_time_job: ScheduledJob):
    """Test that a one-time job executes successfully."""
    # Create job
    job = await scheduler.create_job(one_time_job)
    
    # Wait for execution (scheduled 2 seconds in the future)
    await asyncio.sleep(3)
    
    # Get job and verify it's completed
    executed_job = await scheduler.get_job(job.id)
    assert executed_job is not None
    assert executed_job.status == JobStatus.COMPLETED
    
    # Check execution history
    executions = await scheduler.get_job_executions(job.id)
    assert len(executions) == 1
    assert executions[0].status == ExecutionStatus.COMPLETED
    assert executions[0].result == {"message": "test message"}

@pytest.mark.asyncio
async def test_one_time_job_no_next_run(scheduler: SchedulerService, one_time_job: ScheduledJob):
    """Test that a one-time job has no next run after execution."""
    # Create and execute job
    job = await scheduler.create_job(one_time_job)
    await asyncio.sleep(3)
    
    # Get job and verify no next run
    executed_job = await scheduler.get_job(job.id)
    assert executed_job.next_run_time is None

@pytest.mark.asyncio
async def test_cancel_one_time_job(scheduler: SchedulerService, one_time_job: ScheduledJob):
    """Test cancelling a one-time job."""
    # Create job
    job = await scheduler.create_job(one_time_job)
    
    # Cancel job
    cancelled = await scheduler.cancel_job(job.id)
    assert cancelled is True
    
    # Verify job is cancelled
    cancelled_job = await scheduler.get_job(job.id)
    assert cancelled_job.status == JobStatus.CANCELLED
    
    # Wait and verify it didn't execute
    await asyncio.sleep(3)
    executions = await scheduler.get_job_executions(job.id)
    assert len(executions) == 0

@pytest.mark.asyncio
async def test_one_time_job_invalid_handler(scheduler: SchedulerService, one_time_job: ScheduledJob):
    """Test that a job with an invalid handler fails appropriately."""
    # Modify job to use non-existent handler
    one_time_job.parameters.action = "nonexistent"
    
    # Attempt to create job
    with pytest.raises(ValueError, match="No handler registered for action"):
        await scheduler.create_job(one_time_job)

@pytest.mark.asyncio
async def test_one_time_job_past_date(scheduler: SchedulerService, one_time_job: ScheduledJob):
    """Test creating a one-time job with a past date."""
    # Set run_at to past date
    one_time_job.schedule["run_at"] = (
        datetime.now(timezone.utc) - timedelta(minutes=5)
    ).isoformat()
    
    # Create job - should execute immediately
    job = await scheduler.create_job(one_time_job)
    
    # Wait for execution (up to 3 seconds)
    for _ in range(3):
        await asyncio.sleep(1)
        executed_job = await scheduler.get_job(job.id)
        if executed_job.status == JobStatus.COMPLETED:
            break
    
    # Verify job executed
    assert executed_job.status == JobStatus.COMPLETED
    
    # Check execution
    executions = await scheduler.get_job_executions(job.id)
    assert len(executions) == 1
    assert executions[0].status == ExecutionStatus.COMPLETED 
