from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from datetime import datetime
import os
from dotenv import load_dotenv
from typing import Optional
import uuid

# Load environment variables
load_dotenv()

# Validate required environment variables
required_env_vars = [
    "FASTAPI_API_KEY",
    "DATABASE_URI"
]

missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Configure logger
log_dir = os.getenv("LOG_DIR", "logs")
os.makedirs(log_dir, exist_ok=True)
logger.add(
    f"{log_dir}/tool_server_{datetime.now().strftime('%Y%m%d')}.log",
    rotation="500 MB",
    retention="30 days",
    compression="zip",
    level=os.getenv("LOG_LEVEL", "INFO")
)

# Get environment variables with defaults
PORT = int(os.getenv("FASTAPI_PORT_LOCAL", os.getenv("PORT", "8000")))
HOST = os.getenv("HOST", "0.0.0.0")
SERVER_URL = os.getenv("FASTAPI_BASE_URL", f"http://20.80.96.49:{PORT}")

# Initialize FastAPI app with OpenAPI 3.1.1 compatibility
app = FastAPI(
    title="AI Tool Server",
    description="API server for AI agent tools",
    version="1.0.0",
    openapi_version="3.1.1",
    servers=[{"url": SERVER_URL}],  # This ensures OpenAPI docs use the correct server URL
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you might want to restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request tracking middleware
@app.middleware("http")
async def add_request_tracking(request: Request, call_next):
    request_id = str(uuid.uuid4())
    logger.bind(request_id=request_id).info(
        f"Request started: {request.method} {request.url.path}"
    )
    
    start_time = datetime.now()
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    
    logger.bind(request_id=request_id).info(
        f"Request completed: {request.method} {request.url.path} "
        f"- Status: {response.status_code} - Time: {process_time:.3f}s"
    )
    
    response.headers["X-Request-ID"] = request_id
    return response

@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint to verify the server status.
    
    Returns:
        dict: A dictionary containing the server status and current timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": app.version
    }

@app.get("/")
async def root() -> dict:
    """
    Root endpoint providing basic server information.
    
    Returns:
        dict: A welcome message and API documentation links
    """
    return {
        "message": "Welcome to the AI Tool Server",
        "documentation": {
            "swagger": f"{SERVER_URL}/docs",
            "redoc": f"{SERVER_URL}/redoc",
            "openapi": f"{SERVER_URL}/openapi.json"
        }
    }

# Import and include routers
from .routes import sql_query_router
app.include_router(sql_query_router, tags=["sql_query_tool"])

from app.routes import scheduler
app.include_router(scheduler.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=True
    ) 
