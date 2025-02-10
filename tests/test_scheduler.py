"""
Tests for the scheduler functionality.
"""
import uuid
from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from app.models.scheduler_models import (
    JobType, JobStatus, ExecutionStatus,
    ScheduledJob, JobParameters
)

def test_create_one_time_job(client: TestClient):
    """Test creating a one-time job."""
    job_data = {
        "name": "Test One-time Job",
        "type": JobType.ONE_TIME.value,
        "schedule": {
            "run_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
            "timezone": "UTC"
        },
        "parameters": {
            "action": "test_action",
            "params": {"test": "value"}
        }
    }
    
    response = client.post("/scheduler/jobs", json=job_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["job"]["name"] == job_data["name"]
    assert data["job"]["type"] == job_data["type"]
    assert data["job"]["status"] == JobStatus.PENDING.value
    assert "id" in data["job"]

def test_create_interval_job(client: TestClient):
    """Test creating an interval job."""
    job_data = {
        "name": "Test Interval Job",
        "type": JobType.INTERVAL.value,
        "schedule": {
            "interval_seconds": 3600,
            "start_at": datetime.now(timezone.utc).isoformat(),
            "end_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "timezone": "UTC"
        },
        "parameters": {
            "action": "test_action",
            "params": {"test": "value"}
        }
    }
    
    response = client.post("/scheduler/jobs", json=job_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["job"]["name"] == job_data["name"]
    assert data["job"]["type"] == job_data["type"]
    assert data["job"]["status"] == JobStatus.PENDING.value

def test_create_cron_job(client: TestClient):
    """Test creating a cron job."""
    job_data = {
        "name": "Test Cron Job",
        "type": JobType.CRON.value,
        "schedule": {
            "expression": "0 * * * *",
            "timezone": "UTC"
        },
        "parameters": {
            "action": "test_action",
            "params": {"test": "value"}
        }
    }
    
    response = client.post("/scheduler/jobs", json=job_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["job"]["name"] == job_data["name"]
    assert data["job"]["type"] == job_data["type"]
    assert data["job"]["status"] == JobStatus.PENDING.value

def test_list_jobs(client: TestClient):
    """Test listing jobs."""
    # Create a job first
    job_data = {
        "name": "Test List Job",
        "type": JobType.ONE_TIME.value,
        "schedule": {
            "run_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
            "timezone": "UTC"
        },
        "parameters": {
            "action": "test_action",
            "params": {"test": "value"}
        }
    }
    
    client.post("/scheduler/jobs", json=job_data)
    
    # List jobs
    response = client.get("/scheduler/jobs")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data["jobs"], list)
    assert len(data["jobs"]) > 0
    assert "total" in data

def test_get_job(client: TestClient):
    """Test getting a specific job."""
    # Create a job first
    job_data = {
        "name": "Test Get Job",
        "type": JobType.ONE_TIME.value,
        "schedule": {
            "run_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
            "timezone": "UTC"
        },
        "parameters": {
            "action": "test_action",
            "params": {"test": "value"}
        }
    }
    
    create_response = client.post("/scheduler/jobs", json=job_data)
    job_id = create_response.json()["job"]["id"]
    
    # Get the job
    response = client.get(f"/scheduler/jobs/{job_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["job"]["id"] == job_id
    assert data["job"]["name"] == job_data["name"]

def test_cancel_job(client: TestClient):
    """Test cancelling a job."""
    # Create a job first
    job_data = {
        "name": "Test Cancel Job",
        "type": JobType.ONE_TIME.value,
        "schedule": {
            "run_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
            "timezone": "UTC"
        },
        "parameters": {
            "action": "test_action",
            "params": {"test": "value"}
        }
    }
    
    create_response = client.post("/scheduler/jobs", json=job_data)
    job_id = create_response.json()["job"]["id"]
    
    # Cancel the job
    response = client.delete(f"/scheduler/jobs/{job_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["job"]["id"] == job_id
    assert data["job"]["status"] == JobStatus.CANCELLED.value

def test_get_job_executions(client: TestClient):
    """Test getting job executions."""
    # Create a job first
    job_data = {
        "name": "Test Executions Job",
        "type": JobType.ONE_TIME.value,
        "schedule": {
            "run_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
            "timezone": "UTC"
        },
        "parameters": {
            "action": "test_action",
            "params": {"test": "value"}
        }
    }
    
    create_response = client.post("/scheduler/jobs", json=job_data)
    job_id = create_response.json()["job"]["id"]
    
    # Get executions
    response = client.get(f"/scheduler/jobs/{job_id}/executions")
    assert response.status_code == 200
    
    data = response.json()
    assert "executions" in data
    assert "total" in data

def test_invalid_job_creation(client: TestClient):
    """Test creating a job with invalid data."""
    # Missing required fields
    job_data = {
        "name": "Invalid Job"
    }
    
    response = client.post("/scheduler/jobs", json=job_data)
    assert response.status_code == 422  # Validation error

def test_get_nonexistent_job(client: TestClient):
    """Test getting a job that doesn't exist."""
    random_id = str(uuid.uuid4())
    response = client.get(f"/scheduler/jobs/{random_id}")
    assert response.status_code == 404

def test_cancel_completed_job(client: TestClient):
    """Test attempting to cancel a completed job."""
    # Create a job first
    job_data = {
        "name": "Test Complete Job",
        "type": JobType.ONE_TIME.value,
        "schedule": {
            "run_at": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
            "timezone": "UTC"
        },
        "parameters": {
            "action": "test_action",
            "params": {"test": "value"}
        }
    }
    
    create_response = client.post("/scheduler/jobs", json=job_data)
    job_id = create_response.json()["job"]["id"]
    
    # Try to cancel the job
    response = client.delete(f"/scheduler/jobs/{job_id}")
    assert response.status_code in [400, 404]  # Either not found or can't cancel 
