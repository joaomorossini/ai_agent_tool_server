"""
Pydantic models for the scheduler service.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from croniter import croniter

class JobType(str, Enum):
    """Type of scheduled job."""
    ONE_TIME = "one-time"
    INTERVAL = "interval"
    CRON = "cron"

class JobStatus(str, Enum):
    """Status of a scheduled job."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ExecutionStatus(str, Enum):
    """Status of a job execution."""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Schedule(BaseModel):
    """Base schedule configuration."""
    timezone: str = Field(default="UTC")

class OneTimeSchedule(Schedule):
    """Schedule configuration for one-time jobs."""
    run_at: datetime = Field(..., description="When to run the job")

class IntervalSchedule(Schedule):
    """Schedule configuration for interval-based jobs."""
    interval_seconds: int = Field(..., gt=0, description="Interval in seconds")
    start_at: datetime = Field(..., description="When to start running the job")
    end_at: Optional[datetime] = Field(None, description="When to stop running the job")

    @field_validator("end_at")
    @classmethod
    def validate_end_at(cls, v: Optional[datetime], info: ValidationInfo) -> Optional[datetime]:
        """Validate end_at is after start_at if provided."""
        if v and info.data.get("start_at") and v <= info.data["start_at"]:
            raise ValueError("end_at must be after start_at")
        return v

class CronSchedule(Schedule):
    """Schedule configuration for cron-based jobs."""
    expression: str = Field(..., description="Cron expression")

    @field_validator("expression")
    @classmethod
    def validate_expression(cls, v: str) -> str:
        """Validate cron expression."""
        if not croniter.is_valid(v):
            raise ValueError("Invalid cron expression")
        return v

class JobParameters(BaseModel):
    """Parameters for job execution."""
    action: str = Field(..., description="Action to execute")
    params: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")

class ScheduledJob(BaseModel):
    """Model for a scheduled job."""
    id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=255)
    type: JobType
    status: JobStatus = JobStatus.PENDING
    schedule: Dict[str, Any] = Field(..., description="Schedule configuration")
    parameters: JobParameters
    next_run_time: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("schedule")
    @classmethod
    def validate_schedule(cls, v: Dict[str, Any], info: ValidationInfo) -> Dict[str, Any]:
        """Validate schedule matches job type."""
        job_type = info.data.get("type")
        if not job_type:
            return v

        try:
            if job_type == JobType.ONE_TIME:
                OneTimeSchedule(**v)
            elif job_type == JobType.INTERVAL:
                IntervalSchedule(**v)
            elif job_type == JobType.CRON:
                CronSchedule(**v)
        except ValueError as e:
            raise ValueError(f"Invalid schedule for job type {job_type}: {str(e)}")
        
        return v

class JobExecution(BaseModel):
    """Model for job execution records."""
    id: Optional[UUID] = None
    job_id: UUID
    status: ExecutionStatus = ExecutionStatus.RUNNING
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None 
