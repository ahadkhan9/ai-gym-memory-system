"""
Query API Routes

Endpoints for searching and querying past activities.
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
import logging

from src.models.schemas import MemoryQueryRequest, MemoryQueryResponse, MemoryQueryResult, ActivityResult
from src.services.gemini_service import GeminiService
from src.services.embedding_service import EmbeddingService
from src.services.memory_service import MemoryService
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
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


@router.post("/queries/search", response_model=MemoryQueryResponse)
async def search_activities(request: MemoryQueryRequest):
    """
    Search for past activities using natural language.

    Example:
        POST /api/v1/queries/search
        {
            "query": "What did I train last Tuesday?",
            "limit": 10,
            "similarity_threshold": 0.7
        }
    """
    try:
        logger.info(f"Processing query: {request.query}")

        # Get services
        gemini_service, embedding_service, memory_service = get_services()

        # Process query to extract intent and filters
        query_intent = gemini_service.process_query(request.query)

        # Perform semantic search
        results = memory_service.search_similar(
            query=query_intent.get("semantic_query", request.query),
            top_k=request.limit,
            similarity_threshold=request.similarity_threshold
        )

        # Group results by date
        grouped_results = {}
        for activity in results:
            date = activity.get("date", "Unknown")
            if date not in grouped_results:
                grouped_results[date] = []
            grouped_results[date].append(activity)

        # Format response
        query_results = []
        for date, activities in grouped_results.items():
            activity_results = [
                ActivityResult(
                    exercise=act.get("exercise", "Unknown"),
                    sets=act.get("sets"),
                    reps=act.get("reps"),
                    weight=act.get("weight"),
                    unit=act.get("unit"),
                    duration=act.get("duration"),
                    notes=act.get("notes")
                )
                for act in activities
            ]

            # Use the highest similarity score for the group
            max_similarity = max(act.get("similarity_score", 0) for act in activities)

            query_results.append(
                MemoryQueryResult(
                    date=datetime.fromisoformat(date) if date != "Unknown" else datetime.now(),
                    activities=activity_results,
                    similarity_score=max_similarity
                )
            )

        # Sort by date (most recent first)
        query_results.sort(key=lambda x: x.date, reverse=True)

        return MemoryQueryResponse(
            query=request.query,
            results=query_results,
            total_results=len(results)
        )

    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")


@router.get("/queries/by-exercise/{exercise_name}")
async def search_by_exercise(exercise_name: str):
    """
    Search for activities by exercise name.

    Args:
        exercise_name: Name of the exercise to search for
    """
    try:
        _, _, memory_service = get_services()

        results = memory_service.search_by_exercise(exercise_name)

        return {
            "exercise": exercise_name,
            "total": len(results),
            "activities": results
        }

    except Exception as e:
        logger.error(f"Error searching by exercise: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to search by exercise: {str(e)}")


@router.get("/queries/by-date")
async def search_by_date(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Search for activities within a date range.

    Args:
        start_date: Start date (YYYY-MM-DD format)
        end_date: End date (YYYY-MM-DD format)
    """
    try:
        _, _, memory_service = get_services()

        results = memory_service.search_by_date_range(
            start_date=start_date,
            end_date=end_date
        )

        return {
            "start_date": start_date,
            "end_date": end_date,
            "total": len(results),
            "activities": results
        }

    except Exception as e:
        logger.error(f"Error searching by date: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to search by date: {str(e)}")
