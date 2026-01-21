"""
Memory Service - Storage and Retrieval of Activities

Manages both structured storage (in-memory for now) and vector storage for semantic search.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import logging
import numpy as np

from src.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class MemoryService:
    """Service for storing and retrieving workout activities"""

    def __init__(self, embedding_service: EmbeddingService):
        """
        Initialize memory service.

        Args:
            embedding_service: Service for generating embeddings
        """
        self.embedding_service = embedding_service

        # In-memory storage (replace with PostgreSQL + ChromaDB in production)
        self.activities: List[Dict[str, Any]] = []
        self.embeddings: List[List[float]] = []

        logger.info("Memory service initialized")

    def store_activity(self, activity_data: Dict[str, Any]) -> str:
        """
        Store a new activity with its embedding.

        Args:
            activity_data: Dictionary containing activity information

        Returns:
            Activity ID (UUID)
        """
        try:
            # Generate unique ID
            activity_id = str(uuid.uuid4())

            # Add metadata
            activity = {
                "id": activity_id,
                "created_at": datetime.now().isoformat(),
                **activity_data
            }

            # Generate embedding
            embedding = self.embedding_service.generate_embedding(activity)

            # Store in memory
            self.activities.append(activity)
            self.embeddings.append(embedding)

            logger.info(f"Stored activity {activity_id}: {activity.get('exercise')}")
            return activity_id

        except Exception as e:
            logger.error(f"Error storing activity: {e}")
            raise

    def search_similar(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Search for activities similar to the query using semantic similarity.

        Args:
            query: Natural language search query
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score (0-1)

        Returns:
            List of activities sorted by similarity
        """
        try:
            if not self.activities:
                logger.info("No activities stored yet")
                return []

            # Generate query embedding
            query_embedding = self.embedding_service.generate_query_embedding(query)

            # Calculate cosine similarity with all stored embeddings
            similarities = []
            for idx, activity_embedding in enumerate(self.embeddings):
                similarity = self._cosine_similarity(query_embedding, activity_embedding)
                similarities.append((idx, similarity))

            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)

            # Filter by threshold and get top-k
            results = []
            for idx, similarity in similarities[:top_k]:
                if similarity >= similarity_threshold:
                    activity = self.activities[idx].copy()
                    activity["similarity_score"] = float(similarity)
                    results.append(activity)

            logger.info(f"Found {len(results)} similar activities for query: '{query}'")
            return results

        except Exception as e:
            logger.error(f"Error searching activities: {e}")
            raise

    def search_by_date_range(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search activities within a date range.

        Args:
            start_date: Start date (YYYY-MM-DD) or None
            end_date: End date (YYYY-MM-DD) or None

        Returns:
            List of activities within the date range
        """
        try:
            results = []

            for activity in self.activities:
                activity_date = activity.get("date")
                if not activity_date:
                    continue

                # Check date range
                in_range = True
                if start_date and activity_date < start_date:
                    in_range = False
                if end_date and activity_date > end_date:
                    in_range = False

                if in_range:
                    results.append(activity)

            # Sort by date (descending)
            results.sort(key=lambda x: x.get("date", ""), reverse=True)

            logger.info(f"Found {len(results)} activities in date range")
            return results

        except Exception as e:
            logger.error(f"Error searching by date range: {e}")
            raise

    def search_by_exercise(self, exercise_name: str) -> List[Dict[str, Any]]:
        """
        Search activities by exercise name.

        Args:
            exercise_name: Exercise name to search for

        Returns:
            List of matching activities
        """
        try:
            results = [
                activity for activity in self.activities
                if activity.get("exercise", "").lower() == exercise_name.lower()
            ]

            results.sort(key=lambda x: x.get("date", ""), reverse=True)

            logger.info(f"Found {len(results)} activities for exercise: {exercise_name}")
            return results

        except Exception as e:
            logger.error(f"Error searching by exercise: {e}")
            raise

    def get_all_activities(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get all activities, sorted by date (most recent first).

        Args:
            limit: Maximum number of activities to return

        Returns:
            List of activities
        """
        try:
            sorted_activities = sorted(
                self.activities,
                key=lambda x: x.get("created_at", ""),
                reverse=True
            )

            return sorted_activities[:limit]

        except Exception as e:
            logger.error(f"Error getting all activities: {e}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored activities.

        Returns:
            Dictionary containing statistics
        """
        try:
            if not self.activities:
                return {
                    "total_workouts": 0,
                    "total_exercises": 0,
                    "most_frequent_exercise": None
                }

            # Count exercises
            exercise_counts = {}
            for activity in self.activities:
                exercise = activity.get("exercise")
                if exercise:
                    exercise_counts[exercise] = exercise_counts.get(exercise, 0) + 1

            most_frequent = max(exercise_counts.items(), key=lambda x: x[1])[0] if exercise_counts else None

            # Get date of last workout
            last_workout_date = max(
                (a.get("date") for a in self.activities if a.get("date")),
                default=None
            )

            return {
                "total_workouts": len(self.activities),
                "total_exercises": len(set(a.get("exercise") for a in self.activities if a.get("exercise"))),
                "most_frequent_exercise": most_frequent,
                "last_workout_date": last_workout_date,
                "exercise_breakdown": exercise_counts
            }

        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            raise

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Similarity score (0-1)
        """
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)

        dot_product = np.dot(vec1_np, vec2_np)
        norm_product = np.linalg.norm(vec1_np) * np.linalg.norm(vec2_np)

        if norm_product == 0:
            return 0.0

        return float(dot_product / norm_product)
