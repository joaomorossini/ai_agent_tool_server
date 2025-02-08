from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from datetime import datetime
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

# Configure logger
log_dir = os.getenv("LOG_DIR", "logs")
os.makedirs(log_dir, exist_ok=True)
logger.add(
    f"{log_dir}/tool_server_{datetime.now().strftime('%Y%m%d')}.log",
    rotation="500 MB",
    level=os.getenv("LOG_LEVEL", "INFO")
)

# Get environment variables with defaults
PORT = int(os.getenv("FASTAPI_PORT", os.getenv("PORT", "8000")))
HOST = os.getenv("HOST", "0.0.0.0")
SERVER_URL = os.getenv("FASTAPI_BASE_URL", os.getenv("SERVER_URL", f"http://{HOST}:{PORT}"))

# Initialize FastAPI app with OpenAPI 3.1.1 compatibility
app = FastAPI(
    title="AI Tool Server",
    description="API server for AI agent tools",
    version="1.0.0",
    openapi_version="3.1.1",
    root_path=SERVER_URL,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint to verify the server status.
    
    Returns:
        dict: A dictionary containing the server status and current timestamp
    """
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/")
async def root() -> dict:
    """
    Root endpoint providing basic server information.
    
    Returns:
        dict: A welcome message
    """
    return {"message": "Welcome to the AI Tool Server"}

# Import and include routers
from .routes import list_tables_tool
app.include_router(list_tables_tool.router, prefix="/api", tags=["list_tables_tool"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=True
    ) 
