# AI Tool Server

A FastAPI-based server for AI agent tools with OpenAPI 3.1.1 specification support.

## Features

- OpenAPI 3.1.1 compatibility
- API Key authentication
- Async operations support
- Extensive logging
- Easy extensibility through FastAPI routers

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

   # Verify API health
   curl http://localhost:8001/health

   # Test database connection
   curl http://localhost:8001/list_tables
   ```

### Port Mappings

- FastAPI Server: 8001 (host) -> 8000 (container)
- PostgreSQL: 5434 (host) -> 5432 (container)

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
