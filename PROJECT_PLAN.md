# START NOW

- [ ] Update PROJECT_LESSONS.md with lessons learned:
  1. Focus on real use cases, not theoretical edge cases
  2. Let framework features (like Pydantic validation) do their job
  3. Remove unused code promptly
  4. Question if a test is still relevant before fixing it
  5. Take a step back when debugging to see the bigger picture
  6. Use framework-provided status codes when available
  7. Keep port configurations consistent and well-documented
  8. Ensure all services are running before running tests
  9. Use parameterized tests to avoid code duplication

1. /scheduler

   - [ ] Review reference flask and tool implementation at "/Users/morossini/Projects/ai_agent_tool_server/example_implementations/"
   - [ ] Reuse Flask independent implementation
   - [ ] Convert Flask implementation to FastAPI
   - [ ] Add route to FastAPI server
   - [ ] Test route locally
   - [ ] Add route to FastAPI server
   - [ ] Test route on server

   Success Criteria:

   - Functional
     - Scheduled tasks are executed correctly at the specified time
   - Robustness
     - Implements timeout handling
     - Has comprehensive logging
     - Handles errors gracefully
     - Has clear documentation

---

# BACKLOG

## New Features

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

## Documentation Updates Needed

1. Tests

   - [x] Create a test file which tests all routes both locally and on the server
   - [x] Run tests and identify issues
   - [x] Fix failing tests:
     - [x] Remove test_list_tables: Route was only for testing and is no longer needed
     - [x] Fix test_sql_query_tool_error_handling: Updated to use correct HTTP status codes
     - [x] Fix port configuration: Updated from 8001 to 8000 to match server setup
   - [x] Add test instructions to README
   - [x] Document test environment setup requirements

2. API Documentation

   - [x] Document all endpoints with examples
   - [x] Add error scenarios and handling
   - [x] Include curl examples for testing
   - [x] Document timeout behavior
   - [x] Document HTTP status codes and their meanings

3. Deployment Documentation
   - [x] Update deployment instructions
   - [x] Document environment setup
   - [x] Add troubleshooting guide
   - [x] Document port mappings and network configuration

## Test Improvements

1. Database Test Setup

   - [x] Verify test database connection
   - [x] Ensure test tables are created correctly
   - [x] Add database cleanup between tests
   - Success Criteria:
     - [x] All database-related tests pass
     - [x] Test data is properly isolated
     - [x] No leftover test data between runs

2. Error Handling
   - [x] Simplify error handling to focus on real use cases
   - [x] Remove unnecessary validation (rely on Pydantic)
   - [x] Update status codes to match framework standards
   - Success Criteria:
     - [x] Correct HTTP status codes for all error cases
     - [x] Clear error messages
     - [x] Proper error logging

## Final Steps

1. [x] Run all tests again to verify fixes
2. [x] Add test instructions to README
3. [x] Document recent changes in PROJECT_LESSONS.md
4. [ ] Update Pydantic validators to V2 style
