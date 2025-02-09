# Project Lessons

## Environment and Configuration Management

1. **Simplicity Over Environment-Specific Configurations**

   - Having multiple environment files (dev, prod, etc.) can lead to unnecessary complexity
   - For smaller projects, a single `.env` file in the root directory is often sufficient
   - Benefits of this approach:
     - Easier to maintain and track changes
     - Reduced risk of environment-specific bugs
     - Simpler deployment process
     - Clearer documentation

2. **Deployment Strategy**
   - Keep deployment scripts simple and focused
   - Minimize the number of configuration files that need to be managed
   - Use environment variables for configuration that might change between environments
   - Document deployment prerequisites and steps clearly

## Best Practices Learned

1. **Configuration Management**

   - Store all environment variables in a single `.env` file
   - Use `.env.example` to document required variables without exposing sensitive values
   - Keep configuration close to where it's used (root directory for project-wide config)

2. **Project Structure**
   - Regularly review and remove unused files and configurations
   - Keep deployment-related files (docker-compose, scripts) simple and well-documented
   - Document the reasoning behind structural decisions

## Testing and Debugging

1. **Systematic Testing Approach**

   - Test each endpoint individually with simple requests first
   - Check server logs immediately when requests fail
   - Use curl commands for initial API testing
   - Document all test cases and their expected outcomes
   - Start with local tests before testing deployed endpoints
   - Use parameterized tests to avoid code duplication
   - Focus on testing real use cases, not theoretical edge cases
   - Question if a test is still relevant before fixing it

2. **Avoiding Overcomplication**

   - Always question if we're solving the right problem
   - Consider the actual users (AI agents) and their behavior
   - Let framework features (like Pydantic validation) do their job
   - Remove unused code and features promptly
   - Don't spend time optimizing code that isn't used
   - Remember that simpler code is usually more robust
   - Focus on the higher-level goals rather than individual errors

3. **Debugging Best Practices**

   - Start with health check endpoints to verify basic connectivity
   - Check logs at multiple levels (application, docker, database)
   - Test network connectivity and configuration
   - Document all issues found and their resolution process
   - Take a step back when debugging to see the bigger picture
   - Question if the bug is a symptom of a larger design issue

## Error Handling and Reliability

1. **Timeout Management**

   - Implement timeouts at the route level for better control
   - Use environment variables for configurable timeout values
   - Return user-friendly messages on timeout
   - Log timeout occurrences for monitoring
   - Handle both client and server-side timeouts

2. **Logging Strategy**

   - Log the beginning and end of important operations
   - Include relevant data in logs (counts, operation types)
   - Mask sensitive information (credentials, personal data)
   - Use appropriate log levels (INFO for operations, ERROR for issues)
   - Add request IDs for tracing

3. **Graceful Error Handling**

   - Return user-friendly error messages
   - Log detailed error information for debugging
   - Use appropriate HTTP status codes
   - Handle both expected and unexpected errors
   - Distinguish between client errors (4xx) and server errors (5xx)

4. **HTTP Status Codes**

   - Use framework-provided status codes when possible (e.g., Pydantic's 422 for validation errors)
   - 400 (Bad Request) for client errors that we explicitly handle
   - 422 (Unprocessable Entity) for request validation failures
   - 500 (Internal Server Error) for unexpected server-side errors
   - Document expected status codes in tests and API documentation

5. **Validation Strategy**

   - Leverage framework validation (e.g., Pydantic) as the first line of defense
   - Add custom validation only when framework validation is insufficient
   - Keep validation logic close to the data models
   - Document validation rules in both code and tests

6. **Port Configuration**
   - Keep port numbers consistent across all configurations
   - Document port mappings in README and deployment files
   - Use environment variables for flexible port configuration
   - Test both local and deployed port configurations

## Testing Strategy

1. **Test Data Management**

   - Use fixtures for consistent test data setup
   - Clean up test data after each test run
   - Isolate test database from production
   - Use transactions to roll back changes
   - Verify data state before and after tests

2. **Test Organization**

   - Group related tests into classes
   - Use descriptive test names
   - Document test purpose and expectations
   - Handle expected failures gracefully
   - Test both success and error cases

3. **Test Environment**

   - Keep test environment as close to production as possible
   - Use environment variables for configuration
   - Document test prerequisites
   - Provide setup and teardown instructions
   - Include example test data

4. **Test Environment Setup**
   - Ensure all required services (database, API server) are running before tests
   - Use consistent port numbers across development and testing
   - Document service dependencies and startup sequence
   - Provide clear error messages when services are not available

## Error Handling Improvements

1. **Timeout Handling**

   - Use HTTP 408 status code for timeout errors
   - Consistent timeout handling across all routes
   - Clear timeout error messages for clients

2. **SQL Error Categories**

   - Separate handling for syntax errors (ProgrammingError)
   - Distinct handling for runtime errors (SQLAlchemyError)
   - Appropriate status codes for different error types

3. **Testing Improvements**
   - Comprehensive error scenario coverage
   - Consistent error response format
   - Proper timeout testing
   - Database fixture cleanup

## FastAPI External URL Configuration

When deploying FastAPI applications that need to be accessed externally:

1. **Server URL Configuration**

   - Use `servers=[{"url": SERVER_URL}]` in FastAPI initialization instead of `root_path`
   - This ensures OpenAPI documentation uses the correct external URL
   - Set `SERVER_URL` to the actual external IP/domain where the service will be accessed

2. **CORS Considerations**

   - Configure CORS middleware to allow access from the external URL
   - For development, `allow_origins=["*"]` is acceptable
   - For production, restrict to specific domains
   - CORS is particularly important for Swagger UI/ReDoc to work correctly

3. **Documentation URLs**

   - Always use the external URL in API documentation links
   - Ensure consistency between the server URL and documentation endpoints
   - Test documentation access from both internal and external networks

4. **Environment Variables**
   - Use `FASTAPI_BASE_URL` for overriding the default server URL
   - Keep port configuration consistent across all references
   - Document all URL-related environment variables clearly
