"""
AI Gym & Activity Memory System - Main Application Entry Point

This module initializes the FastAPI application and configures all routes,
middleware, and startup/shutdown events.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "AI Gym & Activity Memory System API",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}

# TODO: Import and include API routes
# from src.api.routes import activities, queries
# app.include_router(activities.router, prefix="/api/v1", tags=["activities"])
# app.include_router(queries.router, prefix="/api/v1", tags=["queries"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup"""
    # TODO: Initialize database connections
    # TODO: Initialize ChromaDB client
    # TODO: Load embedding model
    pass

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    # TODO: Close database connections
    # TODO: Close ChromaDB client
    pass
