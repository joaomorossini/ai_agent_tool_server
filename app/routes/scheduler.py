"""
FastAPI router for scheduler endpoints.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.models.scheduler_models import (
    ScheduledJob, JobExecution, JobType, JobStatus,
    OneTimeSchedule, IntervalSchedule, CronSchedule, JobParameters
)
from app.services.scheduler_service import SchedulerService
from app.utils.decorators import with_timeout

router = APIRouter(prefix="/scheduler", tags=["scheduler"])

# Response Models
class JobResponse(BaseModel):
    """Response model for job operations."""
    job: ScheduledJob
    message: str

class JobListResponse(BaseModel):
    """Response model for job list operations."""
    jobs: List[ScheduledJob]
    total: int
    message: str

class ExecutionListResponse(BaseModel):
    """Response model for job execution list operations."""
    executions: List[JobExecution]
    total: int
    message: str

# Service instance
scheduler_service = SchedulerService()

# Register test handler
async def test_handler(message: str = "Hello, World!") -> dict:
    """Test handler that just returns the input message."""
    return {"message": message}

scheduler_service.register_handler("test", test_handler)

@router.on_event("startup")
async def startup_event():
    """Start the scheduler service when the application starts."""
    await scheduler_service.start()

@router.on_event("shutdown")
async def shutdown_event():
    """Stop the scheduler service when the application shuts down."""
    await scheduler_service.stop()

@router.post("/jobs", response_model=JobResponse)
@with_timeout
async def create_job(job: ScheduledJob) -> JobResponse:
    """
    Create a new scheduled job.
    
    Args:
        job: Job configuration including schedule and parameters
    
    Returns:
        Created job details
    
    Raises:
        HTTPException: If job creation fails
    """
    try:
        created_job = await scheduler_service.create_job(job)
        return JobResponse(
            job=created_job,
            message="Job created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")

@router.get("/jobs", response_model=JobListResponse)
@with_timeout
async def list_jobs(
    status: Optional[JobStatus] = None,
    job_type: Optional[JobType] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
) -> JobListResponse:
    """
    List scheduled jobs with optional filtering.
    
    Args:
        status: Filter by job status
        job_type: Filter by job type
        limit: Maximum number of jobs to return
        offset: Number of jobs to skip
    
    Returns:
        List of jobs matching the criteria
    
    Raises:
        HTTPException: If job listing fails
    """
    try:
        jobs = await scheduler_service.list_jobs(
            status=status,
            job_type=job_type,
            limit=limit,
            offset=offset
        )
        return JobListResponse(
            jobs=jobs,
            total=len(jobs),
            message="Jobs retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")

@router.get("/jobs/{job_id}", response_model=JobResponse)
@with_timeout
async def get_job(job_id: UUID) -> JobResponse:
    """
    Get details of a specific job.
    
    Args:
        job_id: ID of the job to retrieve
    
    Returns:
        Job details
    
    Raises:
        HTTPException: If job is not found or retrieval fails
    """
    try:
        job = await scheduler_service.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return JobResponse(
            job=job,
            message="Job retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job: {str(e)}")

@router.delete("/jobs/{job_id}", response_model=JobResponse)
@with_timeout
async def cancel_job(job_id: UUID) -> JobResponse:
    """
    Cancel a scheduled job.
    
    Args:
        job_id: ID of the job to cancel
    
    Returns:
        Cancelled job details
    
    Raises:
        HTTPException: If job is not found or cancellation fails
    """
    try:
        # First get the job to ensure it exists
        job = await scheduler_service.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Try to cancel the job
        success = await scheduler_service.cancel_job(job_id)
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Job could not be cancelled (already completed or cancelled)"
            )
        
        # Get updated job details
        updated_job = await scheduler_service.get_job(job_id)
        return JobResponse(
            job=updated_job,
            message="Job cancelled successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel job: {str(e)}")

@router.get("/jobs/{job_id}/executions", response_model=ExecutionListResponse)
@with_timeout
async def get_job_executions(
    job_id: UUID,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
) -> ExecutionListResponse:
    """
    Get execution history for a specific job.
    
    Args:
        job_id: ID of the job to get executions for
        limit: Maximum number of executions to return
        offset: Number of executions to skip
    
    Returns:
        List of job executions
    
    Raises:
        HTTPException: If job is not found or retrieval fails
    """
    try:
        # First verify the job exists
        job = await scheduler_service.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        executions = await scheduler_service.get_job_executions(
            job_id=job_id,
            limit=limit,
            offset=offset
        )
        
        return ExecutionListResponse(
            executions=executions,
            total=len(executions),
            message="Job executions retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job executions: {str(e)}"
        ) 
