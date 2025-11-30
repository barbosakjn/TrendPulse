"""
Reddit Service - Fetch trending posts from Reddit.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

import praw
from praw.exceptions import PRAWException
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedditService:
    """Service for interacting with Reddit API using PRAW."""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """
        Initialize Reddit service with credentials.

        Args:
            client_id: Reddit application client ID (optional for read-only)
            client_secret: Reddit application client secret (optional for read-only)
            user_agent: User agent string for API requests
        """
        self.client_id = client_id or settings.REDDIT_CLIENT_ID
        self.client_secret = client_secret or settings.REDDIT_CLIENT_SECRET
        self.user_agent = user_agent or settings.REDDIT_USER_AGENT
        self.reddit = None
        # Always initialize, even without credentials (read-only mode)
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Reddit API client in read-only mode."""
        try:
            # If we have credentials, use them
            if self.client_id and self.client_secret:
                self.reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent,
                    check_for_async=False
                )
                logger.info("Reddit API client initialized with credentials")
            else:
                # Use read-only mode without credentials
                # This works for public subreddits
                self.reddit = praw.Reddit(
                    client_id='',
                    client_secret='',
                    user_agent=self.user_agent,
                    check_for_async=False
                )
                logger.info("Reddit API client initialized in read-only mode (no credentials)")
        except Exception as e:
            logger.error(f"Failed to initialize Reddit API client: {str(e)}")
            self.reddit = None

    def get_trending_posts(
        self,
        subreddit: str = 'all',
        limit: int = 20,
        time_filter: str = 'day'
    ) -> Dict[str, Any]:
        """
        Get trending posts from a subreddit.

        Args:
            subreddit: Subreddit name (default: 'all' for r/all)
            limit: Number of posts to return (1-100, default: 20)
            time_filter: Time period for hot posts - 'hour', 'day', 'week', 'month', 'year', 'all'

        Returns:
            Dict containing trending posts and metadata

        Raises:
            Exception: If API request fails or authentication error
        """
        if not self.reddit:
            self._initialize_client()

        if not self.reddit:
            return {
                "success": False,
                "subreddit": subreddit,
                "error": "Client initialization failed",
                "message": "Failed to initialize Reddit API client.",
                "posts": [],
                "count": 0,
                "limit": limit,
                "timestamp": datetime.utcnow().isoformat()
            }

        try:
            logger.info(f"Fetching trending posts from r/{subreddit}, limit: {limit}")

            # Validate limit
            limit = max(1, min(limit, 100))

            # Get subreddit
            subreddit_obj = self.reddit.subreddit(subreddit)

            # Get hot posts (trending)
            posts = []
            for submission in subreddit_obj.hot(limit=limit):
                # Skip stickied posts
                if submission.stickied:
                    continue

                post_data = {
                    'post_id': submission.id,
                    'title': submission.title,
                    'author': str(submission.author) if submission.author else '[deleted]',
                    'subreddit': submission.subreddit.display_name,
                    'upvotes': submission.score,
                    'upvote_ratio': submission.upvote_ratio,
                    'num_comments': submission.num_comments,
                    'url': f"https://reddit.com{submission.permalink}",
                    'created_at': datetime.fromtimestamp(submission.created_utc).isoformat(),
                    'is_self': submission.is_self,
                    'selftext': submission.selftext[:500] if submission.is_self else '',  # Truncate long text
                    'link_url': submission.url if not submission.is_self else None,
                    'thumbnail': submission.thumbnail if hasattr(submission, 'thumbnail') and submission.thumbnail not in ['self', 'default', 'nsfw', 'spoiler'] else None,
                    'over_18': submission.over_18,
                    'spoiler': submission.spoiler,
                    'awards': submission.total_awards_received if hasattr(submission, 'total_awards_received') else 0,
                }

                posts.append(post_data)

            result = {
                "success": True,
                "subreddit": subreddit,
                "posts": posts,
                "count": len(posts),
                "limit": limit,
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Successfully fetched {len(posts)} trending posts from r/{subreddit}")
            return result

        except PRAWException as e:
            error_message = str(e)
            logger.error(f"Reddit API error: {error_message}")

            # Handle specific error cases
            if 'invalid_grant' in error_message or 'unauthorized' in error_message.lower():
                return {
                    "success": False,
                    "subreddit": subreddit,
                    "error": "Authentication failed",
                    "message": "Invalid Reddit API credentials. Please check your client_id and client_secret.",
                    "posts": [],
                    "count": 0,
                    "limit": limit,
                    "timestamp": datetime.utcnow().isoformat()
                }
            elif 'not found' in error_message.lower() or 'banned' in error_message.lower():
                return {
                    "success": False,
                    "subreddit": subreddit,
                    "error": "Subreddit not found",
                    "message": f"Subreddit r/{subreddit} not found or is banned.",
                    "posts": [],
                    "count": 0,
                    "limit": limit,
                    "timestamp": datetime.utcnow().isoformat()
                }
            elif 'private' in error_message.lower():
                return {
                    "success": False,
                    "subreddit": subreddit,
                    "error": "Private subreddit",
                    "message": f"Subreddit r/{subreddit} is private and cannot be accessed.",
                    "posts": [],
                    "count": 0,
                    "limit": limit,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "subreddit": subreddit,
                    "error": "API request failed",
                    "message": error_message,
                    "posts": [],
                    "count": 0,
                    "limit": limit,
                    "timestamp": datetime.utcnow().isoformat()
                }

        except Exception as e:
            logger.error(f"Unexpected error fetching trending posts: {str(e)}")
            return {
                "success": False,
                "subreddit": subreddit,
                "error": "Internal error",
                "message": str(e),
                "posts": [],
                "count": 0,
                "limit": limit,
                "timestamp": datetime.utcnow().isoformat()
            }


# Global instance
reddit_service = RedditService()
