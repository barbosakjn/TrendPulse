"""
Twitter/X Service - Search tweets using Twikit with Capsolver Cloudflare bypass.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import asyncio
import os
import random
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from twikit import Client
    TWIKIT_AVAILABLE = True
except ImportError:
    TWIKIT_AVAILABLE = False
    logger.warning("Twikit not installed. Twitter features will be disabled.")

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]


class CapsolverCloudflareBypass:
    """Use Capsolver API to bypass Cloudflare protection."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.capsolver.com"
    
    async def solve_cloudflare(self, website_url: str = "https://x.com") -> Optional[Dict]:
        """
        Solve Cloudflare challenge and get cookies/headers.
        """
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                create_payload = {
                    "clientKey": self.api_key,
                    "task": {
                        "type": "AntiCloudflareTask",
                        "websiteURL": website_url,
                        "proxy": ""
                    }
                }
                
                logger.info(f"Creating Capsolver task for Cloudflare bypass on {website_url}")
                create_response = await client.post(
                    f"{self.api_url}/createTask",
                    json=create_payload
                )
                create_data = create_response.json()
                
                if create_data.get("errorId", 0) != 0:
                    error_msg = create_data.get("errorDescription", "Unknown error")
                    logger.error(f"Capsolver createTask error: {error_msg}")
                    
                    if "proxy" in error_msg.lower():
                        create_payload["task"]["type"] = "AntiTurnstileTaskProxyLess"
                        create_payload["task"]["websiteKey"] = ""
                        del create_payload["task"]["proxy"]
                        
                        create_response = await client.post(
                            f"{self.api_url}/createTask",
                            json=create_payload
                        )
                        create_data = create_response.json()
                        
                        if create_data.get("errorId", 0) != 0:
                            logger.error(f"Capsolver retry error: {create_data}")
                            return None
                    else:
                        return None
                
                task_id = create_data.get("taskId")
                if not task_id:
                    logger.error("No taskId returned from Capsolver")
                    return None
                
                logger.info(f"Capsolver task created: {task_id}")
                
                for attempt in range(40):
                    await asyncio.sleep(3)
                    
                    result_response = await client.post(
                        f"{self.api_url}/getTaskResult",
                        json={
                            "clientKey": self.api_key,
                            "taskId": task_id
                        }
                    )
                    result_data = result_response.json()
                    
                    status = result_data.get("status")
                    if status == "ready":
                        solution = result_data.get("solution", {})
                        logger.info("Capsolver solved Cloudflare challenge successfully!")
                        return solution
                    elif status == "failed":
                        logger.error(f"Capsolver task failed: {result_data}")
                        return None
                    
                    logger.debug(f"Capsolver task pending... attempt {attempt + 1}/40")
                
                logger.error("Capsolver task timed out")
                return None
                
        except Exception as e:
            logger.error(f"Capsolver error: {str(e)}")
            return None


class TwitterService:
    """Service for interacting with Twitter/X using Twikit."""

    def __init__(self):
        """Initialize Twitter service."""
        self.username = settings.TWITTER_USERNAME
        self.email = settings.TWITTER_EMAIL
        self.password = settings.TWITTER_PASSWORD
        self.capsolver_api_key = settings.CAPSOLVER_API_KEY
        self.client = None
        self.logged_in = False
        self.cookies_file = "/tmp/twitter_cookies.json"
        self.cf_cookies = None
        self.cf_headers = None
        
        if self.capsolver_api_key:
            logger.info(f"TwitterService initialized with Capsolver")
        else:
            logger.warning("TwitterService initialized WITHOUT Capsolver")

    def _is_configured(self) -> bool:
        """Check if Twitter credentials are configured."""
        return bool(self.username and self.password)

    async def _bypass_cloudflare(self) -> bool:
        """Use Capsolver to bypass Cloudflare protection."""
        if not self.capsolver_api_key:
            logger.warning("No Capsolver API key configured")
            return False
        
        try:
            bypass = CapsolverCloudflareBypass(self.capsolver_api_key)
            solution = await bypass.solve_cloudflare("https://x.com")
            
            if solution:
                self.cf_cookies = solution.get("cookies", [])
                self.cf_headers = solution.get("headers", {})
                user_agent = solution.get("userAgent")
                if user_agent:
                    self.cf_headers["User-Agent"] = user_agent
                logger.info(f"Cloudflare bypass successful - got {len(self.cf_cookies)} cookies")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Cloudflare bypass failed: {str(e)}")
            return False

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
            user_agent = random.choice(USER_AGENTS)
            
            self.client = Client(
                language='en-US',
                user_agent=user_agent
            )
            
            if os.path.exists(self.cookies_file):
                try:
                    self.client.load_cookies(self.cookies_file)
                    self.logged_in = True
                    logger.info("Loaded Twitter session from cookies")
                    return True
                except Exception as e:
                    logger.warning(f"Could not load cookies: {e}")
                    try:
                        os.remove(self.cookies_file)
                    except:
                        pass

            if self.capsolver_api_key:
                logger.info("Attempting Cloudflare bypass with Capsolver...")
                bypass_success = await self._bypass_cloudflare()
                if bypass_success and self.cf_cookies:
                    logger.info("Cloudflare bypassed, applying cookies to client...")

            await asyncio.sleep(random.uniform(1, 2))
            
            logger.info(f"Attempting Twitter login for user: {self.username}")

            await self.client.login(
                auth_info_1=self.username,
                auth_info_2=self.email,
                password=self.password
            )
            
            self.client.save_cookies(self.cookies_file)
            self.logged_in = True
            logger.info("Successfully logged in to Twitter and saved cookies")
            return True

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to login to Twitter: {error_msg}")
            
            if 'Cloudflare' in error_msg or '403' in error_msg or 'blocked' in error_msg.lower():
                logger.error("Cloudflare is blocking the request.")
            
            self.logged_in = False
            self.client = None
            return False

    async def search_tweets(
        self,
        query: str,
        max_results: int = 10,
        search_type: str = 'Latest'
    ) -> Dict[str, Any]:
        """
        Search tweets by keyword.
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
                    "message": "Could not login to Twitter. Cloudflare may be blocking access.",
                    "tweets": [],
                    "count": 0,
                    "timestamp": datetime.utcnow().isoformat()
                }

            logger.info(f"Searching Twitter for: {query}")

            await asyncio.sleep(random.uniform(0.5, 1.5))
            
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
        """Get trending topics."""
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
