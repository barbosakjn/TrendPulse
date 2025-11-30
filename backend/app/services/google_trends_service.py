"""
Google Trends Service - Fetch trending searches using trendspyg.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from trendspyg import download_google_trends_rss
import pandas as pd

logger = logging.getLogger(__name__)

COUNTRY_TO_GEO = {
    'united_states': 'US',
    'brazil': 'BR',
    'united_kingdom': 'GB',
    'canada': 'CA',
    'australia': 'AU',
    'germany': 'DE',
    'france': 'FR',
    'india': 'IN',
    'japan': 'JP',
    'mexico': 'MX',
    'spain': 'ES',
    'italy': 'IT',
    'russia': 'RU',
    'south_korea': 'KR',
    'netherlands': 'NL',
    'argentina': 'AR',
    'colombia': 'CO',
    'portugal': 'PT',
    'poland': 'PL',
    'turkey': 'TR',
}


class GoogleTrendsService:
    """Service for interacting with Google Trends via trendspyg."""

    def __init__(self):
        """Initialize Google Trends service."""
        logger.info("Google Trends service initialized (using trendspyg)")

    def get_trending_searches(self, country: str = 'united_states') -> Dict[str, Any]:
        """
        Get top trending searches for a specific country using RSS feed.

        Args:
            country: Country name (default: 'united_states')

        Returns:
            Dict containing trending searches and metadata
        """
        try:
            geo = COUNTRY_TO_GEO.get(country.lower(), 'US')
            logger.info(f"Fetching trending searches for country: {country} (geo: {geo})")

            trends_list = download_google_trends_rss(geo=geo, output_format='dict')

            if not trends_list or len(trends_list) == 0:
                logger.warning(f"No trending searches found for country: {country}")
                return {
                    "success": False,
                    "country": country,
                    "trends": [],
                    "count": 0,
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": "No trending searches available"
                }

            trends_list = trends_list[:20]

            formatted_trends = []
            for idx, trend in enumerate(trends_list):
                trend_name = trend.get('trend', f'Trend {idx + 1}')
                traffic = trend.get('traffic', None)
                news_articles = trend.get('news_articles', [])
                news_url = news_articles[0].get('url') if news_articles else None
                
                formatted_trends.append({
                    "rank": idx + 1,
                    "query": trend_name,
                    "title": trend_name,
                    "traffic": traffic,
                    "news_url": news_url
                })

            response = {
                "success": True,
                "country": country,
                "trends": formatted_trends,
                "count": len(formatted_trends),
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Successfully fetched {len(formatted_trends)} trending searches")
            return response

        except Exception as e:
            logger.error(f"Error fetching trending searches: {str(e)}")
            return {
                "success": False,
                "country": country,
                "trends": [],
                "count": 0,
                "timestamp": datetime.utcnow().isoformat(),
                "error": "API request failed",
                "message": str(e)
            }

    def get_keyword_interest(
        self,
        keyword: str,
        timeframe: str = 'today 12-m',
        geo: str = 'US'
    ) -> Dict[str, Any]:
        """
        Get interest over time for a specific keyword.
        
        Note: trendspyg focuses on trending searches. For detailed keyword
        interest data, this returns a message about the limitation.

        Args:
            keyword: Search keyword to analyze
            timeframe: Time period (default: 'today 12-m')
            geo: Geographic location (default: 'US')

        Returns:
            Dict containing interest data or limitation message
        """
        try:
            logger.info(f"Keyword interest requested for: '{keyword}' (feature limited)")
            
            return {
                "success": False,
                "keyword": keyword,
                "timeframe": timeframe,
                "geo": geo,
                "data": [],
                "count": 0,
                "related_queries": {},
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Keyword interest data is temporarily unavailable. Please use trending searches instead.",
                "average_interest": 0,
                "peak_interest": 0
            }

        except Exception as e:
            logger.error(f"Error in keyword interest: {str(e)}")
            return {
                "success": False,
                "keyword": keyword,
                "timeframe": timeframe,
                "geo": geo,
                "data": [],
                "timestamp": datetime.utcnow().isoformat(),
                "error": "Internal error",
                "message": str(e)
            }


google_trends_service = GoogleTrendsService()
