from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import logging
import os
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import route modules
from src.api.routes.sensors import router as sensors_router
from src.api.routes.threats import router as threats_router
from src.api.routes.analytics import router as analytics_router
from src.api.routes.admin import router as admin_router
from src.api.models import HealthResponse
from src.api.database import get_db, check_db_connection, check_redis_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO if os.getenv("DEBUG", "False").lower() == "true" else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="AgriDefender API",
    description="API for agricultural biological threat detection and monitoring system",
    version="0.1.0",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from different modules
app.include_router(sensors_router, prefix="/api/v1/sensors", tags=["sensors"])
app.include_router(threats_router, prefix="/api/v1/threats", tags=["threats"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])

@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """
    Health check endpoint to verify the API is operational.
    Returns status information about the API and its dependencies.
    """
    db_status = "ok" if check_db_connection() else "error"
    redis_status = "ok" if check_redis_connection() else "error"
    
    return {
        "status": "healthy" if db_status == "ok" and redis_status == "ok" else "degraded",
        "version": "0.1.0",
        "environment": os.getenv("ENV", "development"),
        "db_connection": db_status,
        "redis_connection": redis_status
    }

@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint that provides information about the API.
    """
    return {
        "message": "Welcome to the AgriDefender API - Crop Defense Monitoring System",
        "version": "0.1.0",
        "documentation_url": "/docs",
        "description": "API for agricultural biological threat detection and monitoring"
    }

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="AgriDefender API",
        version="0.1.0",
        description="API for agricultural biological threat detection and monitoring system",
        routes=app.routes,
    )
    
    # Add custom documentation components
    openapi_schema["info"]["x-logo"] = {
        "url": "https://example.com/logo.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)

