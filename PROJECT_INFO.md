# Project Description

This is a FastAPI server that exposes OpenAPI compatible endpoints to be used as tools by autonomous AI agents. It is designed to run on a Linux VM running Ubuntu, and to be highly extensible, scalable and robust.

## Important Instructions

- At every stage, make sure to update the project files:
  -- PROJECT_PLAN.md with the latest tasks and their status
  -- PROJECT_INFO.md (this file) with the latest information about the project
  -- README.md with the latest project description and instructions
- Constantly ask yourself:
  -- What am I trying to accomplish right now?
  -- How do I know I'm on the right track?
  -- Should I take a step back and rethink my approach to overcome the current challenge?
  -- How do I measure and confirm progress?

## Requirements

- Automated test suites for all routes and classes
- Extensive logging and observability with descriptive error messages
- Graceful handling of errors
- Async support
- Comprehensive documentation and type hinting
- Route descriptions in terms of their utility from the perspective of the AI agent
- Easy deploy with Docker Compose, including Postgres for tools that require persistence
- Dependency and environment management with Poetry
- A scheduler route, to allow AI agents to plan and schedule future task execution

## Deployment

### Azure VM Specifications

- **IP**: 20.80.96.49
- **SSH Access** : Use custom shell command "dify_azure_vm". Should work on zsh and bash
- **VM Size**: Standard B4as v2 (4 vcpus, 16 GiB memory)
- **OS Image**: Ubuntu Server 24.04 LTS - Gen2
- **VM Architecture**: x64
- **Enable Hibernation**: No
- **Authentication Type**: SSH Public Key
  - **Username**: morossini
  - **SSH Key Format**: RSA
  - **Key Pair Name**: dify-vm_ssh-key
- **Public Inbound Ports**: HTTPS, HTTP, SSH

### Concurrent Services

These are running on the same machine.

#### Dify.ai

Dify is a framework for building AI agents. It is a collection of services that work together to provide a complete AI agent development and deployment environment.

SERVICE IMAGE PORTS
nginx nginx:latest 80/tcp, 443/tcp
api langgenius/dify-api:0.15.3 5001/tcp
worker langgenius/dify-api:0.15.3 5001/tcp
web langgenius/dify-web:0.15.3 3000/tcp
weaviate semitechnologies/weaviate:1.19.0 -
redis redis:6-alpine 6379/tcp
database postgres:15-alpine 5432/tcp
sandbox langgenius/dify-sandbox:0.2.10 -
ssrf_proxy ubuntu/squid:latest 3128/tcp

## Additional Info

### Evolution API

Note: This is a non-official WhatsAPp API running on a different VM. It offers simple APIs for allowing the agents to communicate using whatsapp

#### Env Variables

EVOLUTION_API_KEY="[your-api-key]"
EVOLUTION_API_URL="https://wpp-prod.cogmo.com.br"
EVOLUTION_API_INSTANCE="Cogmo_Secretary_Joao"

---

## Routes

Routes must be placed inside app/routes AND imported and included in the app, as shown in the example below.

```python
# File: app/main.py
# Import and include routers
app.include_router(list_tables_tool.router, tags=["list_tables_tool"])
```

### Scheduler

#### /clickup_task_scheduler

This route creates and updates scheduled jobs based on ClickUp task status changes. It is meant to allow humans and agents to collaborate on a shared task list.
The current implementation has been made in Flask, which is why it's been placed under "references/flask_scheduler".

#### /general_task_scheduler

To be developed. All tasks (or 'jobs')

# Scheduler Implementation Handover

## Project Overview

The scheduler is a FastAPI-based service that handles job scheduling with three types of jobs:

- One-time jobs
- Interval-based jobs
- Cron jobs

## Current Status

The project has the following components implemented:

1. Database schema and migrations
2. Pydantic models for jobs and executions
3. Basic API structure with FastAPI router
4. Test framework setup

## Next Steps

1. **Complete SchedulerService Implementation**

   - Focus on the core scheduling logic in `app/services/scheduler_service.py`
   - Implement job execution tracking
   - Add proper error handling and logging
   - Test each job type thoroughly

2. **Finish API Endpoints**

   - Complete the CRUD operations in `app/routes/scheduler.py`
   - Ensure proper validation and error handling
   - Add appropriate status codes and responses

3. **Testing**
   - Add unit tests for the service layer
   - Add integration tests for the API endpoints
   - Focus on the happy path first, then add error cases

## Important Files

1. `app/models/scheduler_models.py`: Contains all Pydantic models
2. `app/services/scheduler_service.py`: Core scheduling logic (needs completion)
3. `app/routes/scheduler.py`: API endpoints (needs completion)
4. `tests/test_scheduler.py`: Basic tests (needs expansion)

## Development Guidelines

1. **Keep It Simple**

   - Focus on getting the basic functionality working first
   - Don't worry about optimization until needed
   - Use FastAPI's built-in features when possible

2. **Testing Approach**

   - Use transaction-based test isolation
   - Test one feature at a time
   - Clean up test data properly

3. **Error Handling**
   - Use appropriate HTTP status codes
   - Return clear error messages
   - Log errors with context

## Database Schema

Two main tables:

1. `scheduled_jobs`: Stores job definitions and status
2. `job_executions`: Tracks job execution history

See `app/database/migrations/001_create_scheduler_tables.sql` for details.

## Getting Started

1. Set up the development environment:

   ```bash
   # Start the database
   docker-compose -f app/docker/docker-compose.yml up -d fastapi_tool_db

   # Install dependencies
   pip install -e .

   # Run migrations
   python app/database/migrations/run_migrations.py

   # Start the server
   uvicorn app.main:app --reload --port 8000
   ```

2. Run tests:
   ```bash
   pytest tests/test_scheduler.py -v
   ```

## Need Help?

1. Check the project documentation in:

   - PROJECT_PLAN.md
   - PROJECT_LESSONS.md
   - README.md

2. Key design decisions are documented in the code comments

3. Test cases provide good examples of expected behavior
