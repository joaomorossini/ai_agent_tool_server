-- Migration: Insert Test Data for Scheduler
-- Description: Adds sample jobs and executions for testing

-- Insert sample one-time job
INSERT INTO scheduled_jobs (
    name,
    type,
    status,
    schedule,
    parameters,
    next_run_time
) VALUES (
    'test_one_time_job',
    'one-time',
    'pending',
    '{"run_at": "2024-02-10T15:00:00Z"}'::jsonb,
    '{"action": "test_action", "parameters": {"test": true}}'::jsonb,
    '2024-02-10T15:00:00Z'
);

-- Insert sample interval job
INSERT INTO scheduled_jobs (
    name,
    type,
    status,
    schedule,
    parameters,
    next_run_time
) VALUES (
    'test_interval_job',
    'interval',
    'active',
    '{
        "interval": "1 hour",
        "start_date": "2024-02-09",
        "start_time": "08:00:00",
        "end_date": "2024-12-31"
    }'::jsonb,
    '{"action": "test_interval_action", "parameters": {"interval_test": true}}'::jsonb,
    '2024-02-09T09:00:00Z'
);

-- Insert sample cron job
INSERT INTO scheduled_jobs (
    name,
    type,
    status,
    schedule,
    parameters,
    next_run_time
) VALUES (
    'test_cron_job',
    'cron',
    'active',
    '{
        "day_of_week": "MON-FRI",
        "hour": "17",
        "minute": "0"
    }'::jsonb,
    '{"action": "test_cron_action", "parameters": {"cron_test": true}}'::jsonb,
    '2024-02-09T17:00:00Z'
);

-- Insert sample executions
INSERT INTO job_executions (
    job_id,
    status,
    started_at,
    completed_at,
    result
) VALUES (
    (SELECT id FROM scheduled_jobs WHERE name = 'test_interval_job'),
    'completed',
    '2024-02-09T08:00:00Z',
    '2024-02-09T08:01:23Z',
    '{"success": true, "processed_items": 42}'::jsonb
);

INSERT INTO job_executions (
    job_id,
    status,
    started_at,
    completed_at,
    error
) VALUES (
    (SELECT id FROM scheduled_jobs WHERE name = 'test_interval_job'),
    'failed',
    '2024-02-09T09:00:00Z',
    '2024-02-09T09:00:05Z',
    'Connection timeout after 5 seconds'
); 
