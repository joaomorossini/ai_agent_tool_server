# AI Tool Server

A FastAPI-based server that exposes OpenAPI compatible endpoints to be used as tools by autonomous AI agents.

## Features

- OpenAPI 3.1.1 specification support
- Automatic API documentation
- Extensive logging and error handling
- Request timeout management
- PostgreSQL database integration
- Docker deployment support

## Quick Start

1. Clone the repository
2. Copy `.env.example` to `.env` and update the values
3. Start the services:
   ```bash
   docker-compose -f app/docker/docker-compose.yml up -d
   ```
4. Visit http://localhost:8001/docs for interactive API documentation

## API Documentation

### Health Check

**Endpoint**: `GET /health`

Check the server's health status.

```bash
curl http://localhost:8001/health
```

**Response**:

```json
{
  "status": "healthy",
  "timestamp": "2025-02-09T17:15:42.569315",
  "version": "1.0.0"
}
```

### SQL Query Tool

**Endpoint**: `POST /sql_query_tool`

Execute SQL queries on the database.

#### SELECT Queries

```bash
curl -X POST http://localhost:8001/sql_query_tool \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM table_name"}'
```

**Response**:

```json
{
  "results": [
    { "column1": "value1", "column2": "value2" },
    { "column1": "value3", "column2": "value4" }
  ]
}
```

#### INSERT/UPDATE/DELETE Queries

```bash
curl -X POST http://localhost:8001/sql_query_tool \
  -H "Content-Type: application/json" \
  -d '{"query": "INSERT INTO table_name (column1) VALUES ('value')"}'
```

**Response**:

```json
{
  "message": "Query executed successfully",
  "rows_affected": 1
}
```

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of requests:

1. **400 Bad Request**

   - Invalid SQL syntax
   - Other client-side errors

2. **500 Internal Server Error**

   - Database connection errors
   - Query execution errors
   - Other server-side issues

3. **Timeouts**
   For operations exceeding the timeout limit (default: 10 seconds):
   ```json
   {
     "warning": "Operation timed out after 10 seconds",
     "message": "The request was processed but took longer than expected. Please try again or contact support if this persists."
   }
   ```

## Environment Variables

| Variable        | Description                  | Default |
| --------------- | ---------------------------- | ------- |
| FASTAPI_API_KEY | API key for authentication   | -       |
| DATABASE_URI    | PostgreSQL connection string | -       |
| TIMEOUT         | Operation timeout in seconds | 10      |
| LOG_LEVEL       | Logging level                | INFO    |
| FASTAPI_PORT    | Server port                  | 8000    |
| HOST            | Server host                  | 0.0.0.0 |

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/test_routes.py -v
```

### Local Development

1. Start the database:

   ```bash
   docker-compose -f app/docker/docker-compose.yml up -d fastapi_tool_db
   ```

2. Run the server in development mode:
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

## Deployment

1. Update `.env` with production values
2. Deploy using the provided script:
   ```bash
   ./scripts/deploy.sh
   ```

### Port Mappings

- FastAPI Server: 8001 (host) -> 8000 (container)
- PostgreSQL: 5434 (host) -> 5432 (container)

## Troubleshooting

1. **Connection Issues**

   - Check container logs: `docker logs fastapi_tool_server`
   - Ensure database is healthy: `docker logs fastapi_tool_db`

2. **Database Issues**

   - Verify DATABASE_URI is correct
   - Check database logs
   - Try connecting directly:
     ```bash
     psql postgresql://ai_tool_user:ai_tool_password_123@localhost:5434/ai_tool_db
     ```

3. **Timeout Issues**
   - Adjust TIMEOUT environment variable
   - Check slow queries
   - Monitor database performance
