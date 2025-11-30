"""
YouTube Service - Fetch trending videos and video data.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.core.config import settings

logger = logging.getLogger(__name__)


class YouTubeService:
    """Service for interacting with YouTube Data API v3."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize YouTube service with API key.

        Args:
            api_key: YouTube Data API v3 key. If not provided, uses settings.YOUTUBE_API_KEY or GOOGLE_API_KEY
        """
        self.api_key = api_key or settings.YOUTUBE_API_KEY or settings.GOOGLE_API_KEY
        self.youtube = None
        if self.api_key:
            self._initialize_client()

    def _initialize_client(self):
        """Initialize YouTube API client."""
        try:
            self.youtube = build(
                'youtube',
                'v3',
                developerKey=self.api_key,
                cache_discovery=False
            )
            logger.info("YouTube API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize YouTube API client: {str(e)}")
            raise

    def get_trending_videos(
        self,
        country: str = 'US',
        category: Optional[str] = None,
        max_results: int = 20
    ) -> Dict[str, Any]:
        """
        Get trending videos for a specific country and category.

        Args:
            country: ISO 3166-1 alpha-2 country code (e.g., 'US', 'BR', 'GB')
            category: Video category ID (optional). Examples:
                     '0' - Film & Animation, '10' - Music, '20' - Gaming,
                     '22' - People & Blogs, '23' - Comedy, '24' - Entertainment,
                     '25' - News & Politics, '26' - Howto & Style, '27' - Education,
                     '28' - Science & Technology
            max_results: Number of videos to return (1-50, default: 20)

        Returns:
            Dict containing trending videos and metadata

        Raises:
            Exception: If API request fails or authentication error
        """
        if not self.api_key:
            return {
                "success": False,
                "country": country,
                "category": category,
                "error": "API key not configured",
                "message": "YouTube API key is not set. Please configure YOUTUBE_API_KEY in settings.",
                "videos": [],
                "count": 0,
                "max_results": max_results,
                "timestamp": datetime.utcnow().isoformat()
            }

        if not self.youtube:
            self._initialize_client()

        try:
            logger.info(f"Fetching trending videos for country: {country}, category: {category}")

            # Validate max_results
            max_results = max(1, min(max_results, 50))

            # Build request parameters
            request_params = {
                'part': 'snippet,contentDetails,statistics',
                'chart': 'mostPopular',
                'regionCode': country,
                'maxResults': max_results
            }

            if category:
                request_params['videoCategoryId'] = str(category)

            # Execute API request
            request = self.youtube.videos().list(**request_params)
            response = request.execute()

            # Parse video data
            videos = []
            for item in response.get('items', []):
                snippet = item.get('snippet', {})
                statistics = item.get('statistics', {})
                content_details = item.get('contentDetails', {})

                video_data = {
                    'video_id': item.get('id'),
                    'title': snippet.get('title'),
                    'description': snippet.get('description', '')[:500],  # Truncate long descriptions
                    'channel': {
                        'id': snippet.get('channelId'),
                        'title': snippet.get('channelTitle')
                    },
                    'thumbnail': {
                        'default': snippet.get('thumbnails', {}).get('default', {}).get('url'),
                        'medium': snippet.get('thumbnails', {}).get('medium', {}).get('url'),
                        'high': snippet.get('thumbnails', {}).get('high', {}).get('url'),
                        'standard': snippet.get('thumbnails', {}).get('standard', {}).get('url'),
                        'maxres': snippet.get('thumbnails', {}).get('maxres', {}).get('url')
                    },
                    'published_at': snippet.get('publishedAt'),
                    'category_id': snippet.get('categoryId'),
                    'tags': snippet.get('tags', [])[:10],  # Limit tags
                    'duration': content_details.get('duration'),
                    'statistics': {
                        'view_count': int(statistics.get('viewCount', 0)),
                        'like_count': int(statistics.get('likeCount', 0)),
                        'comment_count': int(statistics.get('commentCount', 0))
                    },
                    'url': f"https://www.youtube.com/watch?v={item.get('id')}"
                }

                videos.append(video_data)

            result = {
                "success": True,
                "country": country,
                "category": category,
                "videos": videos,
                "count": len(videos),
                "max_results": max_results,
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Successfully fetched {len(videos)} trending videos")
            return result

        except HttpError as e:
            error_reason = e.error_details[0].get('reason', 'unknown') if e.error_details else 'unknown'
            error_message = str(e)

            logger.error(f"YouTube API error: {error_message}")

            # Handle specific error cases
            if e.resp.status == 403:
                if 'quotaExceeded' in error_reason:
                    return {
                        "success": False,
                        "country": country,
                        "category": category,
                        "error": "Quota exceeded",
                        "message": "YouTube API quota has been exceeded. Please try again later.",
                        "videos": [],
                        "count": 0,
                        "max_results": max_results,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "country": country,
                        "category": category,
                        "error": "Authentication failed",
                        "message": "Invalid or restricted API key. Please check your YouTube API key configuration.",
                        "videos": [],
                        "count": 0,
                        "max_results": max_results,
                        "timestamp": datetime.utcnow().isoformat()
                    }
            elif e.resp.status == 400:
                return {
                    "success": False,
                    "country": country,
                    "category": category,
                    "error": "Invalid request",
                    "message": f"Invalid request parameters: {error_reason}",
                    "videos": [],
                    "count": 0,
                    "max_results": max_results,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "country": country,
                    "category": category,
                    "error": "API request failed",
                    "message": error_message,
                    "videos": [],
                    "count": 0,
                    "max_results": max_results,
                    "timestamp": datetime.utcnow().isoformat()
                }

        except Exception as e:
            logger.error(f"Unexpected error fetching trending videos: {str(e)}")
            return {
                "success": False,
                "country": country,
                "category": category,
                "error": "Internal error",
                "message": str(e),
                "videos": [],
                "count": 0,
                "max_results": max_results,
                "timestamp": datetime.utcnow().isoformat()
            }


    def search_videos(
        self,
        query: str,
        country: str = 'US',
        max_results: int = 10,
        order: str = 'relevance'
    ) -> Dict[str, Any]:
        """
        Search videos by keyword.

        Args:
            query: Search query/keyword
            country: ISO 3166-1 alpha-2 country code (e.g., 'US', 'BR')
            max_results: Number of videos to return (1-50, default: 10)
            order: Sort order - 'relevance', 'date', 'viewCount', 'rating'

        Returns:
            Dict containing search results and metadata
        """
        if not self.api_key:
            return {
                "success": False,
                "query": query,
                "error": "API key not configured",
                "message": "YouTube API key is not set. Please configure GOOGLE_API_KEY in secrets.",
                "videos": [],
                "count": 0,
                "max_results": max_results,
                "timestamp": datetime.utcnow().isoformat()
            }

        if not self.youtube:
            self._initialize_client()

        try:
            logger.info(f"Searching YouTube for: {query}")

            max_results = max(1, min(max_results, 50))

            search_request = self.youtube.search().list(
                part='snippet',
                q=query,
                type='video',
                regionCode=country,
                maxResults=max_results,
                order=order
            )
            search_response = search_request.execute()

            video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
            
            if not video_ids:
                return {
                    "success": True,
                    "query": query,
                    "videos": [],
                    "count": 0,
                    "max_results": max_results,
                    "timestamp": datetime.utcnow().isoformat()
                }

            videos_request = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=','.join(video_ids)
            )
            videos_response = videos_request.execute()

            videos = []
            for item in videos_response.get('items', []):
                snippet = item.get('snippet', {})
                statistics = item.get('statistics', {})
                content_details = item.get('contentDetails', {})

                video_data = {
                    'video_id': item.get('id'),
                    'title': snippet.get('title'),
                    'description': snippet.get('description', '')[:500],
                    'channel': {
                        'id': snippet.get('channelId'),
                        'title': snippet.get('channelTitle')
                    },
                    'thumbnail': {
                        'default': snippet.get('thumbnails', {}).get('default', {}).get('url'),
                        'medium': snippet.get('thumbnails', {}).get('medium', {}).get('url'),
                        'high': snippet.get('thumbnails', {}).get('high', {}).get('url'),
                        'standard': snippet.get('thumbnails', {}).get('standard', {}).get('url'),
                        'maxres': snippet.get('thumbnails', {}).get('maxres', {}).get('url')
                    },
                    'published_at': snippet.get('publishedAt'),
                    'category_id': snippet.get('categoryId'),
                    'tags': snippet.get('tags', [])[:10],
                    'duration': content_details.get('duration'),
                    'statistics': {
                        'view_count': int(statistics.get('viewCount', 0)),
                        'like_count': int(statistics.get('likeCount', 0)),
                        'comment_count': int(statistics.get('commentCount', 0))
                    },
                    'url': f"https://www.youtube.com/watch?v={item.get('id')}"
                }
                videos.append(video_data)

            result = {
                "success": True,
                "query": query,
                "videos": videos,
                "count": len(videos),
                "max_results": max_results,
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Successfully found {len(videos)} videos for query: {query}")
            return result

        except HttpError as e:
            error_message = str(e)
            logger.error(f"YouTube API error during search: {error_message}")

            if e.resp.status == 403:
                return {
                    "success": False,
                    "query": query,
                    "error": "Quota exceeded or forbidden",
                    "message": "YouTube API quota exceeded or access forbidden.",
                    "videos": [],
                    "count": 0,
                    "max_results": max_results,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "query": query,
                    "error": "API request failed",
                    "message": error_message,
                    "videos": [],
                    "count": 0,
                    "max_results": max_results,
                    "timestamp": datetime.utcnow().isoformat()
                }

        except Exception as e:
            logger.error(f"Unexpected error searching YouTube: {str(e)}")
            return {
                "success": False,
                "query": query,
                "error": "Internal error",
                "message": str(e),
                "videos": [],
                "count": 0,
                "max_results": max_results,
                "timestamp": datetime.utcnow().isoformat()
            }


# Global instance
youtube_service = YouTubeService()
