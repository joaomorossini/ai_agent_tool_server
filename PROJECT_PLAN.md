# DONE

## Initial Setup

- [x] Deploy VM on Azure
- [x] Install Docker and Docker Compose on VM
- [x] Deploy Dify on VM with Docker Compose
- [x] Deploy Evolution API on a separate VM
- [x] Build and test basic FastAPI server locally
- [x] Deploy FastAPI server along with Postgres on VM using Docker Compose
- [x] Simplify environment configuration by consolidating to a single .env file

## Features and Routes

- /list-tables
  - [x] Create route
  - [x] Test route locally
  - [x] Add route to FastAPI server
  - [x] Test route on server
- /sql_query_tool
  - [x] Create route

# TO DO

## Critical Issues to Fix

1. Server Connectivity Issues

   - [ ] Fix server not responding to HTTP requests
   - [ ] Investigate if this is related to:
     - Network/port configuration
     - Docker network setup
     - FastAPI configuration
   - [ ] Add proper error handling and logging
   - Success Criteria:
     - All endpoints respond to requests
     - Proper error messages are returned
     - Logs show detailed information about requests and responses

2. Database Connection
   - [ ] Verify database connection settings
   - [ ] Test database connectivity
   - [ ] Add database health check
   - Success Criteria:
     - Database connection is stable
     - Queries execute successfully
     - Connection errors are properly handled and logged

## Route-Specific Tasks

1. /sql_query_tool

   - [ ] Test route locally
   - [ ] Add route to FastAPI server
   - [ ] Test route on server
   - Success Criteria:
     - Can execute SELECT queries
     - Can execute INSERT/UPDATE/DELETE queries
     - Proper error handling for invalid queries
     - Results are properly formatted

2. /scheduler
   - [ ] Create route
   - [ ] Test route locally
   - [ ] Add route to FastAPI server
   - [ ] Test route on server

## Documentation Updates Needed

1. API Documentation

   - [ ] Document all endpoints with examples
   - [ ] Add error scenarios and handling
   - [ ] Include curl examples for testing

2. Deployment Documentation
   - [ ] Update deployment instructions
   - [ ] Document environment setup
   - [ ] Add troubleshooting guide
