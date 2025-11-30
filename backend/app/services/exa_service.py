"""
Exa Service - Advanced web search and research using Exa AI.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from exa_py import Exa
from app.core.config import settings

logger = logging.getLogger(__name__)


class ExaService:
    """Service for interacting with Exa AI API for advanced search and research."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Exa service with API key.

        Args:
            api_key: Exa API key. If not provided, uses settings.EXA_API_KEY
        """
        self.api_key = api_key or settings.EXA_API_KEY
        self.exa = None
        if self.api_key:
            self._initialize_client()

    def _initialize_client(self):
        """Initialize Exa API client."""
        try:
            self.exa = Exa(api_key=self.api_key)
            logger.info("Exa API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Exa API client: {str(e)}")
            raise

    def search_trending(
        self,
        query: str,
        num_results: int = 10,
        use_autoprompt: bool = True
    ) -> Dict[str, Any]:
        """
        Search for trending content on a topic.

        Args:
            query: Search query or topic
            num_results: Number of results to return (1-100, default: 10)
            use_autoprompt: Whether to use Exa's autoprompt feature for better results

        Returns:
            Dict containing search results and metadata

        Raises:
            Exception: If API request fails or authentication error
        """
        if not self.api_key:
            return {
                "success": False,
                "query": query,
                "error": "API key not configured",
                "message": "Exa API key is not set. Please configure EXA_API_KEY in settings.",
                "results": [],
                "count": 0,
                "num_results": num_results,
                "timestamp": datetime.utcnow().isoformat()
            }

        if not self.exa:
            self._initialize_client()

        try:
            logger.info(f"Searching Exa for trending content: '{query}', num_results: {num_results}")

            # Validate num_results
            num_results = max(1, min(num_results, 100))

            # Execute search with contents
            search_response = self.exa.search_and_contents(
                query=query,
                num_results=num_results,
                text={"max_characters": 500}  # Get text summary
            )

            # Parse results
            results = []
            for item in search_response.results:
                result_data = {
                    'id': item.id,
                    'title': item.title,
                    'url': item.url,
                    'author': item.author if hasattr(item, 'author') else None,
                    'published_date': item.published_date if hasattr(item, 'published_date') else None,
                    'score': item.score if hasattr(item, 'score') else None,
                    'text': item.text if hasattr(item, 'text') else None,
                    'highlights': item.highlights if hasattr(item, 'highlights') else None,
                }
                results.append(result_data)

            response = {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results),
                "num_results": num_results,
                "autoprompt_string": search_response.autoprompt_string if hasattr(search_response, 'autoprompt_string') else None,
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Successfully fetched {len(results)} results from Exa")
            return response

        except Exception as e:
            error_message = str(e)
            logger.error(f"Exa API error: {error_message}")

            # Handle specific error cases
            if 'api key' in error_message.lower() or 'unauthorized' in error_message.lower():
                return {
                    "success": False,
                    "query": query,
                    "error": "Authentication failed",
                    "message": "Invalid Exa API key. Please check your API key configuration.",
                    "results": [],
                    "count": 0,
                    "num_results": num_results,
                    "timestamp": datetime.utcnow().isoformat()
                }
            elif 'rate limit' in error_message.lower():
                return {
                    "success": False,
                    "query": query,
                    "error": "Rate limit exceeded",
                    "message": "Exa API rate limit exceeded. Please try again later.",
                    "results": [],
                    "count": 0,
                    "num_results": num_results,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "query": query,
                    "error": "API request failed",
                    "message": error_message,
                    "results": [],
                    "count": 0,
                    "num_results": num_results,
                    "timestamp": datetime.utcnow().isoformat()
                }

    def deep_research(
        self,
        topic: str,
        num_results: int = 5
    ) -> Dict[str, Any]:
        """
        Perform deep research on a topic with detailed content.

        Args:
            topic: Research topic
            num_results: Number of results to return (1-50, default: 5)

        Returns:
            Dict containing detailed research results and metadata

        Raises:
            Exception: If API request fails or authentication error
        """
        if not self.api_key:
            return {
                "success": False,
                "topic": topic,
                "error": "API key not configured",
                "message": "Exa API key is not set. Please configure EXA_API_KEY in settings.",
                "results": [],
                "count": 0,
                "num_results": num_results,
                "timestamp": datetime.utcnow().isoformat()
            }

        if not self.exa:
            self._initialize_client()

        try:
            logger.info(f"Performing deep research on: '{topic}', num_results: {num_results}")

            # Validate num_results
            num_results = max(1, min(num_results, 50))

            # Execute search with full contents
            search_response = self.exa.search_and_contents(
                query=topic,
                num_results=num_results,
                text={"max_characters": 2000},  # Get more detailed text
                summary=True  # Get AI-generated summary
            )

            # Parse results with detailed information
            results = []
            for item in search_response.results:
                result_data = {
                    'id': item.id,
                    'title': item.title,
                    'url': item.url,
                    'author': item.author if hasattr(item, 'author') else None,
                    'published_date': item.published_date if hasattr(item, 'published_date') else None,
                    'score': item.score if hasattr(item, 'score') else None,
                    'text': item.text if hasattr(item, 'text') else None,
                    'highlights': item.highlights if hasattr(item, 'highlights') else None,
                    'summary': item.summary if hasattr(item, 'summary') else None,
                }
                results.append(result_data)

            response = {
                "success": True,
                "topic": topic,
                "results": results,
                "count": len(results),
                "num_results": num_results,
                "autoprompt_string": search_response.autoprompt_string if hasattr(search_response, 'autoprompt_string') else None,
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Successfully completed deep research with {len(results)} results")
            return response

        except Exception as e:
            error_message = str(e)
            logger.error(f"Exa deep research error: {error_message}")

            # Handle specific error cases
            if 'api key' in error_message.lower() or 'unauthorized' in error_message.lower():
                return {
                    "success": False,
                    "topic": topic,
                    "error": "Authentication failed",
                    "message": "Invalid Exa API key. Please check your API key configuration.",
                    "results": [],
                    "count": 0,
                    "num_results": num_results,
                    "timestamp": datetime.utcnow().isoformat()
                }
            elif 'rate limit' in error_message.lower():
                return {
                    "success": False,
                    "topic": topic,
                    "error": "Rate limit exceeded",
                    "message": "Exa API rate limit exceeded. Please try again later.",
                    "results": [],
                    "count": 0,
                    "num_results": num_results,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "topic": topic,
                    "error": "API request failed",
                    "message": error_message,
                    "results": [],
                    "count": 0,
                    "num_results": num_results,
                    "timestamp": datetime.utcnow().isoformat()
                }


# Global instance
exa_service = ExaService()
