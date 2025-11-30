"""
Google Trends Service - Fetch trending searches and keyword interest data.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from pytrends.request import TrendReq
from pytrends.exceptions import ResponseError
import pandas as pd

logger = logging.getLogger(__name__)


class GoogleTrendsService:
    """Service for interacting with Google Trends API."""

    def __init__(self):
        """Initialize Google Trends service with TrendReq client."""
        self.pytrends = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize or reinitialize the pytrends client."""
        try:
            self.pytrends = TrendReq(
                hl='en-US',
                tz=360,
                timeout=(10, 30)  # (connect timeout, read timeout)
            )
            logger.info("Google Trends client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Trends client: {str(e)}")
            raise

    def get_trending_searches(self, country: str = 'united_states') -> Dict[str, Any]:
        """
        Get top 20 trending searches for a specific country.

        Args:
            country: Country name (default: 'united_states')
                    Valid values: 'united_states', 'brazil', 'united_kingdom', etc.

        Returns:
            Dict containing trending searches and metadata

        Raises:
            Exception: If request fails or times out
        """
        try:
            logger.info(f"Fetching trending searches for country: {country}")

            # Get trending searches
            trending_df = self.pytrends.trending_searches(pn=country)

            if trending_df is None or trending_df.empty:
                logger.warning(f"No trending searches found for country: {country}")
                return {
                    "success": False,
                    "country": country,
                    "trends": [],
                    "count": 0,
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": "No trending searches available"
                }

            # Convert to list (get first column which contains the search terms)
            trends_list = trending_df.iloc[:, 0].tolist()[:20]

            result = {
                "success": True,
                "country": country,
                "trends": [
                    {
                        "rank": idx + 1,
                        "query": trend,
                        "title": trend
                    }
                    for idx, trend in enumerate(trends_list)
                ],
                "count": len(trends_list),
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Successfully fetched {len(trends_list)} trending searches")
            return result

        except ResponseError as e:
            logger.error(f"Google Trends API error: {str(e)}")
            return {
                "success": False,
                "country": country,
                "trends": [],
                "count": 0,
                "timestamp": datetime.utcnow().isoformat(),
                "error": "API request failed",
                "message": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error fetching trending searches: {str(e)}")
            return {
                "success": False,
                "country": country,
                "trends": [],
                "count": 0,
                "timestamp": datetime.utcnow().isoformat(),
                "error": "Internal error",
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

        Args:
            keyword: Search keyword to analyze
            timeframe: Time period (default: 'today 12-m')
                      Examples: 'now 1-H', 'now 4-H', 'now 1-d', 'now 7-d',
                               'today 1-m', 'today 3-m', 'today 12-m', 'today 5-y', 'all'
            geo: Geographic location (default: 'US')
                 Examples: 'US', 'BR', 'GB', '' for worldwide

        Returns:
            Dict containing interest over time data and related queries

        Raises:
            Exception: If request fails or times out
        """
        try:
            logger.info(f"Fetching interest for keyword: '{keyword}', timeframe: {timeframe}, geo: {geo}")

            # Build payload
            self.pytrends.build_payload(
                kw_list=[keyword],
                cat=0,
                timeframe=timeframe,
                geo=geo,
                gprop=''
            )

            # Get interest over time
            interest_over_time_df = self.pytrends.interest_over_time()

            if interest_over_time_df is None or interest_over_time_df.empty:
                logger.warning(f"No interest data found for keyword: {keyword}")
                return {
                    "success": False,
                    "keyword": keyword,
                    "timeframe": timeframe,
                    "geo": geo,
                    "data": [],
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": "No interest data available"
                }

            # Remove 'isPartial' column if present
            if 'isPartial' in interest_over_time_df.columns:
                interest_over_time_df = interest_over_time_df.drop(columns=['isPartial'])

            # Convert to list of dicts
            interest_data = []
            for date, row in interest_over_time_df.iterrows():
                interest_data.append({
                    "date": date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date),
                    "value": int(row[keyword]) if keyword in row else 0
                })

            # Try to get related queries
            related_queries = {}
            try:
                related_queries_dict = self.pytrends.related_queries()
                if related_queries_dict and keyword in related_queries_dict:
                    keyword_queries = related_queries_dict[keyword]

                    # Top queries
                    if 'top' in keyword_queries and keyword_queries['top'] is not None:
                        top_df = keyword_queries['top']
                        related_queries['top'] = [
                            {
                                "query": row['query'],
                                "value": int(row['value'])
                            }
                            for _, row in top_df.head(10).iterrows()
                        ]

                    # Rising queries
                    if 'rising' in keyword_queries and keyword_queries['rising'] is not None:
                        rising_df = keyword_queries['rising']
                        related_queries['rising'] = [
                            {
                                "query": row['query'],
                                "value": str(row['value'])  # Can be 'Breakout' or numeric
                            }
                            for _, row in rising_df.head(10).iterrows()
                        ]
            except Exception as e:
                logger.warning(f"Could not fetch related queries: {str(e)}")
                related_queries = {}

            result = {
                "success": True,
                "keyword": keyword,
                "timeframe": timeframe,
                "geo": geo,
                "data": interest_data,
                "count": len(interest_data),
                "related_queries": related_queries,
                "timestamp": datetime.utcnow().isoformat(),
                "average_interest": sum([d['value'] for d in interest_data]) / len(interest_data) if interest_data else 0,
                "peak_interest": max([d['value'] for d in interest_data]) if interest_data else 0
            }

            logger.info(f"Successfully fetched interest data for '{keyword}': {len(interest_data)} data points")
            return result

        except ResponseError as e:
            logger.error(f"Google Trends API error for keyword '{keyword}': {str(e)}")
            return {
                "success": False,
                "keyword": keyword,
                "timeframe": timeframe,
                "geo": geo,
                "data": [],
                "timestamp": datetime.utcnow().isoformat(),
                "error": "API request failed",
                "message": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error fetching interest for '{keyword}': {str(e)}")
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


# Global instance
google_trends_service = GoogleTrendsService()
