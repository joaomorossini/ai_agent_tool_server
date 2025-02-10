-- Migration: Create Scheduler Tables
-- Description: Creates the initial tables for the job scheduler

-- Create enum types for job status
DO $$ BEGIN
    CREATE TYPE job_type AS ENUM ('one-time', 'interval', 'cron');
    CREATE TYPE job_status AS ENUM ('pending', 'active', 'completed', 'failed', 'cancelled');
    CREATE TYPE execution_status AS ENUM ('running', 'completed', 'failed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create scheduled_jobs table
CREATE TABLE IF NOT EXISTS scheduled_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type job_type NOT NULL,
    status job_status NOT NULL DEFAULT 'pending',
    schedule JSONB NOT NULL,
    parameters JSONB NOT NULL,
    next_run_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create job_executions table
CREATE TABLE IF NOT EXISTS job_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES scheduled_jobs(id) ON DELETE CASCADE,
    status execution_status NOT NULL DEFAULT 'running',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    error TEXT,
    result JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_jobs_status ON scheduled_jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_next_run ON scheduled_jobs(next_run_time);
CREATE INDEX IF NOT EXISTS idx_jobs_type ON scheduled_jobs(type);
CREATE INDEX IF NOT EXISTS idx_executions_job_id ON job_executions(job_id);
CREATE INDEX IF NOT EXISTS idx_executions_status ON job_executions(status);
CREATE INDEX IF NOT EXISTS idx_executions_started_at ON job_executions(started_at);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for scheduled_jobs
DROP TRIGGER IF EXISTS update_jobs_updated_at ON scheduled_jobs;
CREATE TRIGGER update_jobs_updated_at
    BEFORE UPDATE ON scheduled_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments
COMMENT ON TABLE scheduled_jobs IS 'Stores scheduled job definitions and their current status';
COMMENT ON TABLE job_executions IS 'Stores the execution history of scheduled jobs';
COMMENT ON COLUMN scheduled_jobs.schedule IS 'JSON configuration for job schedule (interval or cron)';
COMMENT ON COLUMN scheduled_jobs.parameters IS 'JSON parameters required for job execution';
COMMENT ON COLUMN job_executions.result IS 'JSON result data from job execution'; 
