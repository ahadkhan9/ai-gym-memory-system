"""
Pydantic Models for Request/Response Schemas

This module defines all data models used for API requests and responses,
ensuring type safety and automatic validation.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ActivityLogRequest(BaseModel):
    """Request model for logging a new activity via natural language"""
    message: str = Field(
        ...,
        description="Natural language description of the activity",
        examples=["I did 3 sets of bench press with 185 lbs today"]
    )


class ParsedActivity(BaseModel):
    """Parsed activity data extracted from natural language"""
    exercise: str = Field(..., description="Exercise name")
    sets: Optional[int] = Field(None, description="Number of sets")
    reps: Optional[int] = Field(None, description="Number of repetitions")
    weight: Optional[float] = Field(None, description="Weight amount")
    unit: Optional[str] = Field(None, description="Weight unit (lbs, kg)")
    duration: Optional[int] = Field(None, description="Duration in minutes")
    date: datetime = Field(default_factory=datetime.now, description="Activity date")
    notes: Optional[str] = Field(None, description="Additional notes")


class ActivityLogResponse(BaseModel):
    """Response model for activity logging"""
    activity_id: str = Field(..., description="Unique activity identifier")
    parsed_data: ParsedActivity
    message: str = Field(..., description="Success message")


class MemoryQueryRequest(BaseModel):
    """Request model for querying past activities"""
    query: str = Field(
        ...,
        description="Natural language query about past activities",
        examples=["What did I train last Tuesday?", "Show me my chest workouts"]
    )
    limit: int = Field(10, description="Maximum number of results", ge=1, le=50)
    similarity_threshold: float = Field(
        0.7,
        description="Minimum similarity score (0-1)",
        ge=0.0,
        le=1.0
    )


class ActivityResult(BaseModel):
    """Individual activity in query results"""
    exercise: str
    sets: Optional[int]
    reps: Optional[int]
    weight: Optional[float]
    unit: Optional[str]
    duration: Optional[int]
    notes: Optional[str]


class MemoryQueryResult(BaseModel):
    """Single result from memory query"""
    date: datetime
    activities: List[ActivityResult]
    similarity_score: float = Field(..., description="Relevance score (0-1)")


class MemoryQueryResponse(BaseModel):
    """Response model for memory queries"""
    query: str
    results: List[MemoryQueryResult]
    total_results: int = Field(..., description="Total number of results found")


class WorkoutStats(BaseModel):
    """Statistics about workout history"""
    total_workouts: int
    total_exercises: int
    most_frequent_exercise: Optional[str]
    avg_weekly_workouts: float
    last_workout_date: Optional[datetime]
