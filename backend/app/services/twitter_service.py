"""
Twitter/X Service - Search tweets using Twikit (no official API needed).
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import asyncio
import os

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from twikit import Client
    TWIKIT_AVAILABLE = True
except ImportError:
    TWIKIT_AVAILABLE = False
    logger.warning("Twikit not installed. Twitter features will be disabled.")


class TwitterService:
    """Service for interacting with Twitter/X using Twikit."""

    def __init__(self):
        """Initialize Twitter service."""
        self.username = settings.TWITTER_USERNAME
        self.email = settings.TWITTER_EMAIL
        self.password = settings.TWITTER_PASSWORD
        self.client = None
        self.logged_in = False
        self.cookies_file = "/tmp/twitter_cookies.json"

    def _is_configured(self) -> bool:
        """Check if Twitter credentials are configured."""
        return bool(self.username and self.password)

    async def _ensure_logged_in(self) -> bool:
        """Ensure we're logged in to Twitter."""
        if not TWIKIT_AVAILABLE:
            logger.error("Twikit library not available")
            return False

        if not self._is_configured():
            logger.warning("Twitter credentials not configured")
            return False

        if self.logged_in and self.client:
            return True

        try:
            self.client = Client('en-US')
            
            if os.path.exists(self.cookies_file):
                try:
                    self.client.load_cookies(self.cookies_file)
                    self.logged_in = True
                    logger.info("Loaded Twitter session from cookies")
                    return True
                except Exception as e:
                    logger.warning(f"Could not load cookies: {e}")

            await self.client.login(
                auth_info_1=self.username,
                auth_info_2=self.email,
                password=self.password
            )
            self.client.save_cookies(self.cookies_file)
            self.logged_in = True
            logger.info("Successfully logged in to Twitter")
            return True

        except Exception as e:
            logger.error(f"Failed to login to Twitter: {str(e)}")
            self.logged_in = False
            return False

    async def search_tweets(
        self,
        query: str,
        max_results: int = 10,
        search_type: str = 'Latest'
    ) -> Dict[str, Any]:
        """
        Search tweets by keyword.

        Args:
            query: Search query/keyword
            max_results: Number of tweets to return (default: 10)
            search_type: 'Latest' or 'Top'

        Returns:
            Dict containing search results and metadata
        """
        if not TWIKIT_AVAILABLE:
            return {
                "success": False,
                "query": query,
                "error": "Library not available",
                "message": "Twikit library is not installed.",
                "tweets": [],
                "count": 0,
                "timestamp": datetime.utcnow().isoformat()
            }

        if not self._is_configured():
            return {
                "success": False,
                "query": query,
                "error": "Not configured",
                "message": "Twitter credentials not configured. Please set TWITTER_USERNAME, TWITTER_EMAIL, and TWITTER_PASSWORD.",
                "tweets": [],
                "count": 0,
                "timestamp": datetime.utcnow().isoformat()
            }

        try:
            if not await self._ensure_logged_in():
                return {
                    "success": False,
                    "query": query,
                    "error": "Login failed",
                    "message": "Could not login to Twitter. Please check your credentials.",
                    "tweets": [],
                    "count": 0,
                    "timestamp": datetime.utcnow().isoformat()
                }

            logger.info(f"Searching Twitter for: {query}")

            tweets_result = await self.client.search_tweet(query, search_type)
            
            tweets = []
            count = 0
            for tweet in tweets_result:
                if count >= max_results:
                    break
                
                tweet_data = {
                    'tweet_id': tweet.id,
                    'text': tweet.text,
                    'user': {
                        'id': tweet.user.id if tweet.user else None,
                        'name': tweet.user.name if tweet.user else 'Unknown',
                        'screen_name': tweet.user.screen_name if tweet.user else 'unknown',
                        'profile_image': tweet.user.profile_image_url if tweet.user else None,
                        'followers_count': tweet.user.followers_count if tweet.user else 0
                    },
                    'created_at': str(tweet.created_at) if hasattr(tweet, 'created_at') else None,
                    'retweet_count': tweet.retweet_count if hasattr(tweet, 'retweet_count') else 0,
                    'favorite_count': tweet.favorite_count if hasattr(tweet, 'favorite_count') else 0,
                    'reply_count': tweet.reply_count if hasattr(tweet, 'reply_count') else 0,
                    'url': f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}" if tweet.user else None
                }
                tweets.append(tweet_data)
                count += 1

            result = {
                "success": True,
                "query": query,
                "search_type": search_type,
                "tweets": tweets,
                "count": len(tweets),
                "max_results": max_results,
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Successfully found {len(tweets)} tweets for query: {query}")
            return result

        except Exception as e:
            logger.error(f"Error searching Twitter: {str(e)}")
            return {
                "success": False,
                "query": query,
                "error": "Search failed",
                "message": str(e),
                "tweets": [],
                "count": 0,
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_trends(self, woeid: int = 1) -> Dict[str, Any]:
        """
        Get trending topics.

        Args:
            woeid: Where On Earth ID (1 for worldwide, 23424977 for USA)

        Returns:
            Dict containing trending topics
        """
        if not TWIKIT_AVAILABLE:
            return {
                "success": False,
                "error": "Library not available",
                "message": "Twikit library is not installed.",
                "trends": [],
                "count": 0,
                "timestamp": datetime.utcnow().isoformat()
            }

        if not self._is_configured():
            return {
                "success": False,
                "error": "Not configured",
                "message": "Twitter credentials not configured.",
                "trends": [],
                "count": 0,
                "timestamp": datetime.utcnow().isoformat()
            }

        try:
            if not await self._ensure_logged_in():
                return {
                    "success": False,
                    "error": "Login failed",
                    "message": "Could not login to Twitter.",
                    "trends": [],
                    "count": 0,
                    "timestamp": datetime.utcnow().isoformat()
                }

            trends_result = await self.client.get_trends('explore')
            
            trends = []
            for i, trend in enumerate(trends_result[:20]):
                trend_data = {
                    'rank': i + 1,
                    'name': trend.name if hasattr(trend, 'name') else str(trend),
                    'tweet_count': trend.tweet_count if hasattr(trend, 'tweet_count') else None,
                    'url': f"https://twitter.com/search?q={trend.name}" if hasattr(trend, 'name') else None
                }
                trends.append(trend_data)

            return {
                "success": True,
                "trends": trends,
                "count": len(trends),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting Twitter trends: {str(e)}")
            return {
                "success": False,
                "error": "Failed to get trends",
                "message": str(e),
                "trends": [],
                "count": 0,
                "timestamp": datetime.utcnow().isoformat()
            }


def _run_async(coro):
    """Run async function in sync context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


twitter_service = TwitterService()
