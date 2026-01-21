"""
Embedding Service - Generate Vector Embeddings for Activities

Creates semantic embeddings for workout descriptions to enable similarity search.
"""

from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import logging

from src.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings from activity data"""

    def __init__(self):
        """Initialize the embedding model"""
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        self.model = SentenceTransformer(settings.embedding_model)
        logger.info("Embedding model loaded successfully")

    def create_activity_text(self, activity: Dict[str, Any]) -> str:
        """
        Convert activity dictionary to text representation for embedding.

        Args:
            activity: Dictionary containing activity data

        Returns:
            Text representation of the activity
        """
        parts = []

        # Add exercise name
        if activity.get("exercise"):
            parts.append(f"Exercise: {activity['exercise']}")

        # Add sets and reps
        if activity.get("sets"):
            parts.append(f"{activity['sets']} sets")
        if activity.get("reps"):
            parts.append(f"{activity['reps']} reps")

        # Add weight
        if activity.get("weight") and activity.get("unit"):
            parts.append(f"{activity['weight']} {activity['unit']}")

        # Add duration
        if activity.get("duration"):
            parts.append(f"{activity['duration']} minutes")

        # Add notes
        if activity.get("notes"):
            parts.append(f"Notes: {activity['notes']}")

        # Add date context
        if activity.get("date"):
            parts.append(f"Date: {activity['date']}")

        return " | ".join(parts)

    def generate_embedding(self, activity: Dict[str, Any]) -> List[float]:
        """
        Generate embedding vector for an activity.

        Args:
            activity: Dictionary containing activity data

        Returns:
            List of floats representing the embedding vector
        """
        try:
            text = self.create_activity_text(activity)
            logger.debug(f"Generating embedding for: {text}")

            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True)

            # Convert to list for JSON serialization
            embedding_list = embedding.tolist()

            logger.debug(f"Generated {len(embedding_list)}-dimensional embedding")
            return embedding_list

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.

        Args:
            query: Natural language search query

        Returns:
            List of floats representing the query embedding
        """
        try:
            logger.debug(f"Generating query embedding for: {query}")
            embedding = self.model.encode(query, convert_to_numpy=True)
            return embedding.tolist()

        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise

    def generate_batch_embeddings(self, activities: List[Dict[str, Any]]) -> List[List[float]]:
        """
        Generate embeddings for multiple activities in batch (more efficient).

        Args:
            activities: List of activity dictionaries

        Returns:
            List of embedding vectors
        """
        try:
            texts = [self.create_activity_text(activity) for activity in activities]
            logger.info(f"Generating embeddings for {len(texts)} activities")

            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)

            return [emb.tolist() for emb in embeddings]

        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
