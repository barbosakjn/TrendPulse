"""
Trends API routes for TrendPulse.
Handles trending searches, keyword interest analysis, and YouTube trending videos.
"""
from fastapi import APIRouter, HTTPException, status
from typing import Union

from app.schemas.trends import (
    GoogleTrendsRequest,
    TrendingSearchesResponse,
    KeywordInterestResponse,
    YouTubeTrendingRequest,
    YouTubeTrendingResponse,
    RedditTrendingRequest,
    RedditTrendingResponse,
    ExaSearchRequest,
    ExaSearchResponse,
    ErrorResponse,
)
from app.services.google_trends_service import google_trends_service
from app.services.youtube_service import youtube_service
from app.services.reddit_service import reddit_service
from app.services.exa_service import exa_service


# Create router
router = APIRouter()


# ============================================================================
# GOOGLE TRENDS ENDPOINT
# ============================================================================

@router.post(
    "/google",
    response_model=Union[TrendingSearchesResponse, KeywordInterestResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Google Trends data",
    description="Fetch trending searches or keyword interest data from Google Trends",
    responses={
        200: {
            "description": "Google Trends data retrieved successfully",
            "content": {
                "application/json": {
                    "examples": {
                        "trending_searches": {
                            "summary": "Trending Searches Example",
                            "value": {
                                "success": True,
                                "country": "united_states",
                                "trends": [
                                    {"rank": 1, "query": "trending topic 1", "title": "trending topic 1"},
                                    {"rank": 2, "query": "trending topic 2", "title": "trending topic 2"}
                                ],
                                "count": 2,
                                "timestamp": "2024-01-01T12:00:00"
                            }
                        },
                        "keyword_interest": {
                            "summary": "Keyword Interest Example",
                            "value": {
                                "success": True,
                                "keyword": "AI",
                                "timeframe": "today 12-m",
                                "geo": "US",
                                "data": [
                                    {"date": "2024-01-01", "value": 75},
                                    {"date": "2024-01-02", "value": 80}
                                ],
                                "count": 2,
                                "related_queries": {
                                    "top": [{"query": "artificial intelligence", "value": 100}],
                                    "rising": [{"query": "AI tools", "value": "Breakout"}]
                                },
                                "timestamp": "2024-01-01T12:00:00",
                                "average_interest": 77.5,
                                "peak_interest": 80
                            }
                        }
                    }
                }
            }
        },
        400: {"model": ErrorResponse, "description": "Bad request - invalid action or missing parameters"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_google_trends(request: GoogleTrendsRequest):
    """
    Get Google Trends data based on the action specified.

    **Actions:**
    - `trending_searches`: Get top 20 trending searches for a country
    - `keyword_interest`: Get interest over time for a specific keyword

    **Examples:**

    Trending Searches:
    ```json
    {
        "action": "trending_searches",
        "country": "united_states"
    }
    ```

    Keyword Interest:
    ```json
    {
        "action": "keyword_interest",
        "keyword": "AI",
        "timeframe": "today 12-m",
        "geo": "US"
    }
    ```
    """
    try:
        # Validate action
        if request.action not in ["trending_searches", "keyword_interest"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": "Invalid action",
                    "message": f"Action must be 'trending_searches' or 'keyword_interest', got '{request.action}'"
                }
            )

        # Handle trending searches
        if request.action == "trending_searches":
            country = request.country or "united_states"
            result = google_trends_service.get_trending_searches(country=country)
            return result

        # Handle keyword interest
        elif request.action == "keyword_interest":
            if not request.keyword:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "success": False,
                        "error": "Missing parameter",
                        "message": "Keyword is required for keyword_interest action"
                    }
                )

            result = google_trends_service.get_keyword_interest(
                keyword=request.keyword,
                timeframe=request.timeframe or "today 12-m",
                geo=request.geo or "US"
            )
            return result

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal server error",
                "message": str(e)
            }
        )


# ============================================================================
# YOUTUBE TRENDING ENDPOINT
# ============================================================================

@router.post(
    "/youtube",
    response_model=YouTubeTrendingResponse,
    status_code=status.HTTP_200_OK,
    summary="Get YouTube trending videos",
    description="Fetch trending videos from YouTube for a specific country and category",
    responses={
        200: {
            "description": "YouTube trending videos retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "country": "US",
                        "category": None,
                        "videos": [
                            {
                                "video_id": "dQw4w9WgXcQ",
                                "title": "Example Video",
                                "description": "This is an example video description...",
                                "channel": {
                                    "id": "UCuAXFkgsw1L7xaCfnd5JJOw",
                                    "title": "Example Channel"
                                },
                                "thumbnail": {
                                    "default": "https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg",
                                    "medium": "https://i.ytimg.com/vi/dQw4w9WgXcQ/mqdefault.jpg",
                                    "high": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
                                    "standard": "https://i.ytimg.com/vi/dQw4w9WgXcQ/sddefault.jpg",
                                    "maxres": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
                                },
                                "published_at": "2024-01-01T12:00:00Z",
                                "category_id": "10",
                                "tags": ["music", "trending"],
                                "duration": "PT3M42S",
                                "statistics": {
                                    "view_count": 1000000,
                                    "like_count": 50000,
                                    "comment_count": 5000
                                },
                                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                            }
                        ],
                        "count": 1,
                        "max_results": 20,
                        "timestamp": "2024-01-01T12:00:00"
                    }
                }
            }
        },
        400: {"model": ErrorResponse, "description": "Bad request - invalid parameters"},
        403: {"model": ErrorResponse, "description": "API key not configured or quota exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_youtube_trending(request: YouTubeTrendingRequest):
    """
    Get trending videos from YouTube.

    **Parameters:**
    - `country`: ISO 3166-1 alpha-2 country code (e.g., 'US', 'BR', 'GB')
    - `category`: Optional video category ID:
      - `10`: Music
      - `20`: Gaming
      - `22`: People & Blogs
      - `23`: Comedy
      - `24`: Entertainment
      - `25`: News & Politics
      - `26`: Howto & Style
      - `27`: Education
      - `28`: Science & Technology
    - `max_results`: Number of videos to return (1-50, default: 20)

    **Example:**
    ```json
    {
        "country": "US",
        "category": "28",
        "max_results": 10
    }
    ```
    """
    try:
        result = youtube_service.get_trending_videos(
            country=request.country,
            category=request.category,
            max_results=request.max_results
        )
        return result

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal server error",
                "message": str(e)
            }
        )


# ============================================================================
# REDDIT TRENDING ENDPOINT
# ============================================================================

@router.post(
    "/reddit",
    response_model=RedditTrendingResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Reddit trending posts",
    description="Fetch trending (hot) posts from a specific subreddit or r/all",
    responses={
        200: {
            "description": "Reddit trending posts retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "subreddit": "all",
                        "posts": [
                            {
                                "post_id": "abc123",
                                "title": "Example Reddit Post",
                                "author": "reddit_user",
                                "subreddit": "news",
                                "upvotes": 15000,
                                "upvote_ratio": 0.95,
                                "num_comments": 500,
                                "url": "https://reddit.com/r/news/comments/abc123/example_post",
                                "created_at": "2024-01-01T12:00:00",
                                "is_self": False,
                                "selftext": "",
                                "link_url": "https://example.com/news-article",
                                "thumbnail": "https://i.redd.it/thumbnail.jpg",
                                "over_18": False,
                                "spoiler": False,
                                "awards": 10
                            }
                        ],
                        "count": 1,
                        "limit": 20,
                        "timestamp": "2024-01-01T12:00:00"
                    }
                }
            }
        },
        400: {"model": ErrorResponse, "description": "Bad request - invalid parameters"},
        403: {"model": ErrorResponse, "description": "API credentials not configured or subreddit is private"},
        404: {"model": ErrorResponse, "description": "Subreddit not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_reddit_trending(request: RedditTrendingRequest):
    """
    Get trending posts from Reddit.

    **Parameters:**
    - `subreddit`: Subreddit name (e.g., 'all', 'python', 'news', 'worldnews')
    - `limit`: Number of posts to return (1-100, default: 20)

    **Popular Subreddits:**
    - `all`: All of Reddit
    - `news`: Breaking news
    - `worldnews`: World news
    - `technology`: Technology news
    - `science`: Science discussions
    - `programming`: Programming topics
    - `python`: Python programming

    **Example:**
    ```json
    {
        "subreddit": "python",
        "limit": 10
    }
    ```
    """
    try:
        result = reddit_service.get_trending_posts(
            subreddit=request.subreddit,
            limit=request.limit
        )
        return result

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal server error",
                "message": str(e)
            }
        )


# ============================================================================
# EXA AI SEARCH ENDPOINT
# ============================================================================

@router.post(
    "/exa",
    response_model=ExaSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search and research using Exa AI",
    description="Perform advanced web search or deep research using Exa AI",
    responses={
        200: {
            "description": "Exa search results retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "query": "latest AI trends 2024",
                        "results": [
                            {
                                "id": "example123",
                                "title": "Top AI Trends in 2024",
                                "url": "https://example.com/ai-trends",
                                "author": "John Doe",
                                "published_date": "2024-01-15",
                                "score": 0.95,
                                "text": "Artificial intelligence is rapidly evolving...",
                                "highlights": ["AI trends", "machine learning", "2024"],
                                "summary": None
                            }
                        ],
                        "count": 1,
                        "num_results": 10,
                        "autoprompt_string": "Find recent articles about AI trends in 2024",
                        "timestamp": "2024-01-01T12:00:00"
                    }
                }
            }
        },
        400: {"model": ErrorResponse, "description": "Bad request - invalid action or missing parameters"},
        403: {"model": ErrorResponse, "description": "API key not configured or rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def search_exa(request: ExaSearchRequest):
    """
    Search and research using Exa AI.

    **Actions:**
    - `search_trending`: Search for trending content on a topic
    - `deep_research`: Perform deep research with detailed summaries

    **Parameters:**
    - `action`: Action to perform ('search_trending' or 'deep_research')
    - `query`: Search query (required for search_trending)
    - `topic`: Research topic (required for deep_research)
    - `num_results`: Number of results (1-100, default: 10)

    **Example - Search Trending:**
    ```json
    {
        "action": "search_trending",
        "query": "AI breakthroughs 2024",
        "num_results": 10
    }
    ```

    **Example - Deep Research:**
    ```json
    {
        "action": "deep_research",
        "topic": "quantum computing applications",
        "num_results": 5
    }
    ```
    """
    try:
        # Validate action
        if request.action not in ["search_trending", "deep_research"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": "Invalid action",
                    "message": f"Action must be 'search_trending' or 'deep_research', got '{request.action}'"
                }
            )

        # Handle search trending
        if request.action == "search_trending":
            if not request.query:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "success": False,
                        "error": "Missing parameter",
                        "message": "Query is required for search_trending action"
                    }
                )

            result = exa_service.search_trending(
                query=request.query,
                num_results=request.num_results
            )
            return result

        # Handle deep research
        elif request.action == "deep_research":
            if not request.topic:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "success": False,
                        "error": "Missing parameter",
                        "message": "Topic is required for deep_research action"
                    }
                )

            result = exa_service.deep_research(
                topic=request.topic,
                num_results=request.num_results
            )
            return result

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal server error",
                "message": str(e)
            }
        )
