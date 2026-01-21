"""
Activity Logging API Routes

Endpoints for logging new workouts and activities.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from src.models.schemas import ActivityLogRequest, ActivityLogResponse, ParsedActivity
from src.services.gemini_service import GeminiService
from src.services.embedding_service import EmbeddingService
from src.services.memory_service import MemoryService

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services (in production, use dependency injection)
_gemini_service = None
_embedding_service = None
_memory_service = None


def get_services():
    """Initialize services on first request"""
    global _gemini_service, _embedding_service, _memory_service

    if _gemini_service is None:
        _gemini_service = GeminiService()
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    if _memory_service is None:
        _memory_service = MemoryService(_embedding_service)

    return _gemini_service, _embedding_service, _memory_service


@router.post("/activities/log", response_model=ActivityLogResponse)
async def log_activity(request: ActivityLogRequest):
    """
    Log a new workout or activity using natural language.

    Example:
        POST /api/v1/activities/log
        {
            "message": "I did 3 sets of bench press with 185 lbs today"
        }
    """
    try:
        logger.info(f"Logging activity: {request.message}")

        # Get services
        gemini_service, embedding_service, memory_service = get_services()

        # Extract structured data from natural language
        parsed_data = gemini_service.extract_activity(request.message)

        # Store activity with embedding
        activity_id = memory_service.store_activity(parsed_data)

        # Prepare response
        parsed_activity = ParsedActivity(**parsed_data)

        return ActivityLogResponse(
            activity_id=activity_id,
            parsed_data=parsed_activity,
            message=f"Successfully logged {parsed_data.get('exercise', 'activity')}!"
        )

    except Exception as e:
        logger.error(f"Error logging activity: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to log activity: {str(e)}")


@router.get("/activities/all")
async def get_all_activities(limit: int = 50):
    """
    Get all logged activities.

    Args:
        limit: Maximum number of activities to return (default: 50)
    """
    try:
        _, _, memory_service = get_services()

        activities = memory_service.get_all_activities(limit=limit)

        return {
            "total": len(activities),
            "activities": activities
        }

    except Exception as e:
        logger.error(f"Error retrieving activities: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve activities: {str(e)}")


@router.get("/activities/stats")
async def get_statistics():
    """
    Get workout statistics.

    Returns statistics about logged workouts including total count,
    most frequent exercises, and exercise breakdown.
    """
    try:
        _, _, memory_service = get_services()

        stats = memory_service.get_statistics()

        return stats

    except Exception as e:
        logger.error(f"Error calculating statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to calculate statistics: {str(e)}")
