"""
AI Gym & Activity Memory System - Main Application Entry Point

This module initializes the FastAPI application and configures all routes,
middleware, and startup/shutdown events.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.api.routes import activities, queries

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Gym & Activity Memory System",
    description="AI-powered conversational system to log gym workouts and daily activities using natural language",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(activities.router, prefix="/api/v1", tags=["Activities"])
app.include_router(queries.router, prefix="/api/v1", tags=["Queries"])


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "AI Gym & Activity Memory System API",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "log_activity": "POST /api/v1/activities/log",
            "get_activities": "GET /api/v1/activities/all",
            "get_stats": "GET /api/v1/activities/stats",
            "search": "POST /api/v1/queries/search",
            "search_by_exercise": "GET /api/v1/queries/by-exercise/{exercise}",
            "search_by_date": "GET /api/v1/queries/by-date",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup"""
    logger.info("🚀 AI Gym & Activity Memory System starting up...")
    logger.info("✅ Services will be initialized on first request")
    logger.info("📚 API documentation available at /docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("👋 AI Gym & Activity Memory System shutting down...")
