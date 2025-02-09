# START NOW

## Documentation Updates Needed

1. Tests

- [ ] Create a test file which tests all routes both locally and on the server

2. API Documentation

   - [ ] Document all endpoints with examples
   - [ ] Add error scenarios and handling
   - [ ] Include curl examples for testing
   - [ ] Document timeout behavior

3. Deployment Documentation
   - [ ] Update deployment instructions
   - [ ] Document environment setup
   - [ ] Add troubleshooting guide
   - [ ] Document port mappings and network configuration

---

# BACKLOG

## New Features

1. /scheduler
   - [ ] Review reference flask and tool implementation at "/Users/morossini/Projects/ai_agent_tool_server/example_implementations/"
   - [ ] Reuse Flask independent implementation
   - [ ] Convert Flask implementation to FastAPI
   - [ ] Add route to FastAPI server
   - [ ] Test route locally
   - [ ] Add route to FastAPI server
   - [ ] Test route on server
   - Success Criteria:
     - Implements timeout handling
     - Has comprehensive logging
     - Handles errors gracefully
     - Has clear documentation

---

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
  - [x] Test route locally
  - [x] Add route to FastAPI server
  - [x] Test route on server
  - [x] Add timeout handling
  - [x] Improve error handling and logging

## Improvements

- [x] Fix server connectivity issues
- [x] Add timeout decorator for all routes
- [x] Enhance logging across all routes
- [x] Verify database connection
- [x] Test all endpoints successfully
