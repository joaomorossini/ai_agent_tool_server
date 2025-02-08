# AI Tool Server

A FastAPI-based server for AI agent tools with OpenAPI 3.1.1 specification support.

## Features

- OpenAPI 3.1.1 compatibility
- API Key authentication
- Async operations support
- Extensive logging
- Easy extensibility through FastAPI routers

## Architecture

### Project Structure

```
ai_tool_server/
├── app/
│   ├── docker/         # Docker configuration files
│   ├── routes/         # API route handlers
│   ├── models/         # Pydantic models and database schemas
│   ├── core/           # Core functionality and configurations
│   └── utils/          # Utility functions and helpers
├── tests/              # Test suite
└── example_implementations/ # Reference implementations
```

### Design Principles

1. **Modularity**: Each route is a separate module, making it easy to add or remove functionality
2. **Dependency Injection**: FastAPI's dependency system is used for clean service integration
3. **Type Safety**: Full type hinting throughout the codebase
4. **Configuration Management**: Environment-based configuration using `.env` files
5. **API Documentation**: Auto-generated OpenAPI documentation

### Adding New Features

1. Create a new route module in `app/routes/`
2. Define your Pydantic models in `app/models/`
3. Implement the route logic following existing patterns
4. Register the route in `app/main.py`
5. Add tests in `tests/`

## Local Development

```zsh
python -m uvicorn app.main:app --reload
```

## Docker Deployment

### Prerequisites

- Docker and Docker Compose installed
- PostgreSQL client (optional, for direct DB access)
- Access to the deployment server

### Environment Setup

1. Create a `.env` file in the project root with the following variables:

   ```env
   # Server Configuration
   FASTAPI_API_KEY=your_api_key
   HOST=0.0.0.0
   FASTAPI_PORT=8000
   FASTAPI_BASE_URL=your_server_url  # e.g., https://api.example.com

   # Database Configuration
   DATABASE_URI=postgresql://ai_tool_user:ai_tool_password_123@fastapi_tool_db:5432/ai_tool_db
   ```

### Deployment Steps

1. Build and start the services:

   ```bash
   docker-compose -f app/docker/docker-compose.yml up -d --build
   ```

2. Verify deployment:

   ```bash
   # Check running containers
   docker ps

   # Verify API health (replace {SERVER_URL} with your deployment URL)
   curl https://{SERVER_URL}/health

   # Test database connection
   curl https://{SERVER_URL}/list_tables
   ```

### Port Mappings

- FastAPI Server: 8001 (host) -> 8000 (container)
- PostgreSQL: 5434 (host) -> 5432 (container)

### API Documentation

- Swagger UI: `https://{SERVER_URL}/docs`
- ReDoc: `https://{SERVER_URL}/redoc`
- OpenAPI JSON: `https://{SERVER_URL}/openapi.json`

### Troubleshooting

If services don't start properly:

1. Check logs:

   ```bash
   docker-compose -f app/docker/docker-compose.yml logs
   ```

2. Clean up and restart:

   ```bash
   # Stop services and remove volumes
   docker-compose -f app/docker/docker-compose.yml down -v

   # Remove all containers (if needed)
   docker rm -f $(docker ps -aq)

   # Clean up volumes
   docker volume prune -f

   # Rebuild and start
   docker-compose -f app/docker/docker-compose.yml up -d --build
   ```

## Lessons Learned

1. **Docker Deployment**

   - Use absolute paths in `docker-compose.yml` context for remote deployment
   - Ensure unique container and network names to avoid conflicts
   - Implement proper health checks for dependent services
   - Use unique and consistent volume names

2. **Configuration Management**

   - Keep sensitive data in `.env` files
   - Use different environment files for different deployment environments
   - Validate environment variables at startup

3. **Database Management**
   - Use initialization scripts for database setup
   - Implement proper migration strategies
   - Regular backup procedures

## Areas for Improvement

### Implemented

- [x] Proper environment variable validation
- [x] Database health checks
- [x] API documentation endpoints

### TODO

- [ ] Implement database migrations using Alembic
- [ ] Add CI/CD pipeline configuration
- [ ] Implement automated backup strategy for PostgreSQL
- [ ] Add rate limiting for API endpoints
- [ ] Implement proper logging rotation
- [ ] Add monitoring and metrics collection
- [ ] Implement caching layer
- [ ] Add integration tests
- [ ] Implement proper error handling middleware
- [ ] Add request validation middleware
