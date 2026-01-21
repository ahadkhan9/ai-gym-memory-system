"""
Gemini Service - Intent Extraction from Natural Language

Uses OpenAI-compatible API to extract structured workout data from natural language.
"""

from openai import OpenAI
from typing import Dict, Any, Optional
from datetime import datetime
import json
import logging

from src.core.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Gemini Flash via OpenAI-compatible API"""

    def __init__(self):
        """Initialize OpenAI client with custom base URL"""
        self.client = OpenAI(
            base_url=settings.gemini_base_url,
            api_key=settings.gemini_api_key
        )
        self.model = settings.gemini_model

    def extract_activity(self, message: str) -> Dict[str, Any]:
        """
        Extract structured activity data from natural language message.

        Args:
            message: Natural language description of workout/activity

        Returns:
            Dictionary containing parsed activity data

        Example:
            Input: "I did 3 sets of bench press with 185 lbs today"
            Output: {
                "exercise": "bench press",
                "sets": 3,
                "weight": 185,
                "unit": "lbs",
                "date": "2026-01-21"
            }
        """
        try:
            # Construct prompt for intent extraction
            system_prompt = """You are an expert fitness tracker assistant.
Extract workout information from user messages into structured JSON format.

Rules:
1. Extract: exercise name, sets, reps, weight, unit (lbs/kg), duration (minutes), notes
2. If information is missing, use null
3. Infer date from context ("today", "yesterday", "last Tuesday")
4. Return ONLY valid JSON, no extra text
5. Exercise names should be lowercase

Output format:
{
    "exercise": "string",
    "sets": integer or null,
    "reps": integer or null,
    "weight": float or null,
    "unit": "lbs" or "kg" or null,
    "duration": integer or null,
    "notes": "string" or null,
    "date": "YYYY-MM-DD"
}"""

            user_prompt = f"Extract workout data from this message: '{message}'"

            # Call Gemini API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Low temperature for consistent extraction
                max_tokens=200
            )

            # Parse response
            content = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            # Parse JSON
            parsed_data = json.loads(content)

            # Ensure date is set to today if not specified
            if not parsed_data.get("date"):
                parsed_data["date"] = datetime.now().strftime("%Y-%m-%d")

            logger.info(f"Successfully extracted activity: {parsed_data}")
            return parsed_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Response content: {content}")
            # Return basic structure with raw message
            return {
                "exercise": "unknown",
                "notes": message,
                "date": datetime.now().strftime("%Y-%m-%d")
            }

        except Exception as e:
            logger.error(f"Error extracting activity: {e}")
            raise

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process natural language query to extract search intent and filters.

        Args:
            query: Natural language query like "What did I train last Tuesday?"

        Returns:
            Dictionary containing query intent and filters

        Example:
            Input: "What did I train last Tuesday?"
            Output: {
                "intent": "search",
                "exercise_filter": null,
                "date_filter": "2026-01-14",
                "muscle_group": null
            }
        """
        try:
            system_prompt = """You are a fitness tracker query assistant.
Extract search intent and filters from natural language queries.

Rules:
1. Determine intent: "search", "stats", "comparison"
2. Extract temporal filters (dates, ranges)
3. Extract categorical filters (exercise type, muscle group)
4. Return ONLY valid JSON

Output format:
{
    "intent": "search" | "stats" | "comparison",
    "exercise_filter": "string" or null,
    "date_filter": "YYYY-MM-DD" or null,
    "date_range_start": "YYYY-MM-DD" or null,
    "date_range_end": "YYYY-MM-DD" or null,
    "muscle_group": "string" or null,
    "semantic_query": "simplified search query"
}"""

            user_prompt = f"Extract search intent from: '{query}'"

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )

            content = response.choices[0].message.content.strip()

            # Remove markdown code blocks
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            parsed_query = json.loads(content)
            logger.info(f"Processed query: {parsed_query}")
            return parsed_query

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            # Fallback: return basic search intent
            return {
                "intent": "search",
                "semantic_query": query
            }
