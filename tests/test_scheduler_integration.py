"""
Integration tests for the scheduler implementation.
"""
import asyncio
from datetime import datetime, timedelta
import os
from typing import AsyncGenerator, Dict, Any
import uuid
import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from app.models.scheduler_models import (
    ScheduledJob, JobExecution, JobType, JobStatus, ExecutionStatus,
    OneTimeSchedule, IntervalSchedule, CronSchedule, JobParameters
)
from app.services.scheduler_service import SchedulerService
from app.routes.scheduler import router
from app.database import get_db_connection

# Test data
TEST_JOB_NAME = f"test_job_{uuid.uuid4()}"

@pytest.fixture
def app() -> FastAPI:
    """Create a test FastAPI application."""
    app = FastAPI()
    app.include_router(router)
    return app

@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def scheduler_service() -> AsyncGenerator[SchedulerService, None]:
    """Create and start a test scheduler service."""
    service = SchedulerService(default_timeout=5)
    
    # Register a test handler
    async def test_handler(**kwargs):
        await asyncio.sleep(0.1)  # Simulate some work
        return {"result": "success", **kwargs}
    
    service.register_handler("test_action", test_handler)
    
    await service.start()
    yield service
    await service.stop()

@pytest.fixture
def one_time_job() -> Dict[str, Any]:
    """Create a test one-time job."""
    return {
        "name": TEST_JOB_NAME,
        "type": "one-time",
        "schedule": {
            "run_at": (datetime.utcnow() + timedelta(seconds=2)).isoformat()
        },
        "parameters": {
            "action": "test_action",
            "parameters": {"test": True}
        }
    }

@pytest.fixture
def interval_job() -> Dict[str, Any]:
    """Create a test interval job."""
    return {
        "name": f"{TEST_JOB_NAME}_interval",
        "type": "interval",
        "schedule": {
            "interval": "5 seconds",
            "start_date": datetime.utcnow().isoformat(),
            "end_date": (datetime.utcnow() + timedelta(seconds=10)).isoformat()
        },
        "parameters": {
            "action": "test_action",
            "parameters": {"test": True}
        }
    }

async def cleanup_test_jobs():
    """Clean up test jobs from the database."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            # Delete test jobs and their executions
            await cur.execute(
                "DELETE FROM job_executions WHERE job_id IN "
                "(SELECT id FROM scheduled_jobs WHERE name LIKE 'test_job_%')"
            )
            await cur.execute(
                "DELETE FROM scheduled_jobs WHERE name LIKE 'test_job_%'"
            )

@pytest.fixture(autouse=True)
async def setup_cleanup():
    """Setup and cleanup for each test."""
    await cleanup_test_jobs()
    yield
    await cleanup_test_jobs()

# Database Integration Tests
@pytest.mark.asyncio
async def test_job_persistence(scheduler_service: SchedulerService, one_time_job: Dict[str, Any]):
    """Test that jobs are correctly persisted in the database."""
    # Create a job
    job = ScheduledJob(**one_time_job)
    created_job = await scheduler_service.create_job(job)
    
    # Verify it exists in the database
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT * FROM scheduled_jobs WHERE id = %s",
                (created_job.id,)
            )
            result = await cur.fetchone()
            assert result is not None
            assert result[1] == job.name  # name
            assert result[2] == job.type.value  # type

@pytest.mark.asyncio
async def test_job_execution_tracking(
    scheduler_service: SchedulerService,
    one_time_job: Dict[str, Any]
):
    """Test that job executions are correctly tracked."""
    # Create and start a job that will run soon
    job = ScheduledJob(**one_time_job)
    created_job = await scheduler_service.create_job(job)
    
    # Wait for the job to execute
    await asyncio.sleep(3)
    
    # Check execution records
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT * FROM job_executions WHERE job_id = %s",
                (created_job.id,)
            )
            result = await cur.fetchone()
            assert result is not None
            assert result[2] == ExecutionStatus.COMPLETED.value  # status

@pytest.mark.asyncio
async def test_interval_job_multiple_executions(
    scheduler_service: SchedulerService,
    interval_job: Dict[str, Any]
):
    """Test that interval jobs execute multiple times."""
    # Create and start an interval job
    job = ScheduledJob(**interval_job)
    created_job = await scheduler_service.create_job(job)
    
    # Wait for multiple executions
    await asyncio.sleep(7)
    
    # Check execution records
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT COUNT(*) FROM job_executions WHERE job_id = %s",
                (created_job.id,)
            )
            count = await cur.fetchone()
            assert count[0] > 1  # Should have multiple executions

@pytest.mark.asyncio
async def test_job_cancellation_persistence(
    scheduler_service: SchedulerService,
    interval_job: Dict[str, Any]
):
    """Test that job cancellation is correctly persisted."""
    # Create an interval job
    job = ScheduledJob(**interval_job)
    created_job = await scheduler_service.create_job(job)
    
    # Wait for first execution
    await asyncio.sleep(2)
    
    # Cancel the job
    await scheduler_service.cancel_job(created_job.id)
    
    # Verify job status in database
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT status FROM scheduled_jobs WHERE id = %s",
                (created_job.id,)
            )
            result = await cur.fetchone()
            assert result[0] == JobStatus.CANCELLED.value

# API Integration Tests
@pytest.mark.asyncio
async def test_create_and_execute_job_api(
    client: AsyncClient,
    one_time_job: Dict[str, Any]
):
    """Test job creation and execution through the API."""
    # Create job
    response = await client.post("/scheduler/jobs", json=one_time_job)
    assert response.status_code == 200
    job_id = response.json()["job"]["id"]
    
    # Wait for execution
    await asyncio.sleep(3)
    
    # Check execution history
    response = await client.get(f"/scheduler/jobs/{job_id}/executions")
    assert response.status_code == 200
    executions = response.json()["executions"]
    assert len(executions) > 0
    assert executions[0]["status"] == ExecutionStatus.COMPLETED.value

@pytest.mark.asyncio
async def test_job_lifecycle_api(
    client: AsyncClient,
    interval_job: Dict[str, Any]
):
    """Test complete job lifecycle through the API."""
    # Create job
    response = await client.post("/scheduler/jobs", json=interval_job)
    assert response.status_code == 200
    job_id = response.json()["job"]["id"]
    
    # Wait for some executions
    await asyncio.sleep(7)
    
    # Get job details
    response = await client.get(f"/scheduler/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["job"]["status"] == JobStatus.ACTIVE.value
    
    # Cancel job
    response = await client.delete(f"/scheduler/jobs/{job_id}")
    assert response.status_code == 200
    
    # Verify job is cancelled
    response = await client.get(f"/scheduler/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["job"]["status"] == JobStatus.CANCELLED.value
    
    # Check execution history
    response = await client.get(f"/scheduler/jobs/{job_id}/executions")
    assert response.status_code == 200
    executions = response.json()["executions"]
    assert len(executions) > 0

@pytest.mark.asyncio
async def test_concurrent_job_execution(
    client: AsyncClient,
    one_time_job: Dict[str, Any]
):
    """Test that multiple jobs can execute concurrently."""
    # Create multiple jobs
    job_ids = []
    for i in range(3):
        job = one_time_job.copy()
        job["name"] = f"{TEST_JOB_NAME}_{i}"
        response = await client.post("/scheduler/jobs", json=job)
        assert response.status_code == 200
        job_ids.append(response.json()["job"]["id"])
    
    # Wait for executions
    await asyncio.sleep(3)
    
    # Verify all jobs executed
    for job_id in job_ids:
        response = await client.get(f"/scheduler/jobs/{job_id}/executions")
        assert response.status_code == 200
        executions = response.json()["executions"]
        assert len(executions) > 0
        assert executions[0]["status"] == ExecutionStatus.COMPLETED.value

@pytest.mark.asyncio
async def test_error_handling_integration(client: AsyncClient):
    """Test error handling in real database operations."""
    # Try to get non-existent job
    non_existent_id = uuid.uuid4()
    response = await client.get(f"/scheduler/jobs/{non_existent_id}")
    assert response.status_code == 404
    
    # Try to create job with invalid schedule
    invalid_job = {
        "name": TEST_JOB_NAME,
        "type": "interval",
        "schedule": {
            "interval": "invalid"
        },
        "parameters": {
            "action": "test_action",
            "parameters": {}
        }
    }
    response = await client.post("/scheduler/jobs", json=invalid_job)
    assert response.status_code == 422  # Validation error
    
    # Try to cancel non-existent job
    response = await client.delete(f"/scheduler/jobs/{non_existent_id}")
    assert response.status_code == 404 
