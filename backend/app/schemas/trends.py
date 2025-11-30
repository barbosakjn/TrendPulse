"""
Pydantic schemas for Trends APIs (Google Trends, YouTube, etc.).
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class TrendingSearchesRequest(BaseModel):
    """Request schema for getting trending searches."""
    country: str = Field(
        default="united_states",
        description="Country for trending searches (e.g., 'united_states', 'brazil', 'united_kingdom')"
    )


class KeywordInterestRequest(BaseModel):
    """Request schema for getting keyword interest over time."""
    keyword: str = Field(
        ...,
        description="Keyword to analyze",
        min_length=1,
        max_length=200
    )
    timeframe: str = Field(
        default="today 12-m",
        description="Time period (e.g., 'now 1-H', 'now 7-d', 'today 1-m', 'today 12-m', 'today 5-y', 'all')"
    )
    geo: str = Field(
        default="US",
        description="Geographic location (e.g., 'US', 'BR', 'GB', '' for worldwide)"
    )


class GoogleTrendsRequest(BaseModel):
    """Combined request schema for Google Trends endpoint."""
    action: str = Field(
        ...,
        description="Action to perform: 'trending_searches' or 'keyword_interest'"
    )
    country: Optional[str] = Field(
        default="united_states",
        description="Country for trending searches"
    )
    keyword: Optional[str] = Field(
        default=None,
        description="Keyword for interest analysis"
    )
    timeframe: Optional[str] = Field(
        default="today 12-m",
        description="Timeframe for interest analysis"
    )
    geo: Optional[str] = Field(
        default="US",
        description="Geographic location for interest analysis"
    )


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class TrendItem(BaseModel):
    """Individual trend item in trending searches."""
    rank: int = Field(..., description="Ranking position")
    query: str = Field(..., description="Search query")
    title: str = Field(..., description="Display title")


class TrendingSearchesResponse(BaseModel):
    """Response schema for trending searches."""
    success: bool = Field(..., description="Whether the request was successful")
    country: str = Field(..., description="Country code used")
    trends: List[TrendItem] = Field(..., description="List of trending searches")
    count: int = Field(..., description="Number of trends returned")
    timestamp: str = Field(..., description="ISO timestamp of when data was fetched")
    message: Optional[str] = Field(None, description="Optional message")
    error: Optional[str] = Field(None, description="Error type if failed")


class InterestDataPoint(BaseModel):
    """Individual data point in interest over time."""
    date: str = Field(..., description="Date of the data point")
    value: int = Field(..., description="Interest value (0-100)")


class RelatedQuery(BaseModel):
    """Related query item."""
    query: str = Field(..., description="Related search query")
    value: Any = Field(..., description="Value (numeric or 'Breakout')")


class RelatedQueries(BaseModel):
    """Related queries for a keyword."""
    top: Optional[List[RelatedQuery]] = Field(None, description="Top related queries")
    rising: Optional[List[RelatedQuery]] = Field(None, description="Rising related queries")


class KeywordInterestResponse(BaseModel):
    """Response schema for keyword interest over time."""
    success: bool = Field(..., description="Whether the request was successful")
    keyword: str = Field(..., description="Keyword analyzed")
    timeframe: str = Field(..., description="Timeframe used")
    geo: str = Field(..., description="Geographic location used")
    data: List[InterestDataPoint] = Field(..., description="Interest over time data points")
    count: int = Field(..., description="Number of data points")
    related_queries: Optional[Dict[str, List[RelatedQuery]]] = Field(
        None,
        description="Related queries (top and rising)"
    )
    timestamp: str = Field(..., description="ISO timestamp of when data was fetched")
    average_interest: Optional[float] = Field(None, description="Average interest value")
    peak_interest: Optional[int] = Field(None, description="Peak interest value")
    message: Optional[str] = Field(None, description="Optional message")
    error: Optional[str] = Field(None, description="Error type if failed")


class ErrorResponse(BaseModel):
    """Error response schema."""
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    timestamp: str = Field(..., description="ISO timestamp of the error")


# ============================================================================
# YOUTUBE SCHEMAS
# ============================================================================

class YouTubeTrendingRequest(BaseModel):
    """Request schema for YouTube trending videos or search."""
    action: str = Field(
        default="trending_videos",
        description="Action to perform: 'trending_videos' or 'search'"
    )
    country: str = Field(
        default="US",
        description="ISO 3166-1 alpha-2 country code (e.g., 'US', 'BR', 'GB')"
    )
    category: Optional[str] = Field(
        default=None,
        description="Video category ID (e.g., '10' for Music, '20' for Gaming, '28' for Science & Technology)"
    )
    query: Optional[str] = Field(
        default=None,
        description="Search query/keyword (required for 'search' action)"
    )
    max_results: int = Field(
        default=20,
        ge=1,
        le=50,
        description="Number of videos to return (1-50)"
    )


class YouTubeChannel(BaseModel):
    """YouTube channel information."""
    id: str = Field(..., description="Channel ID")
    title: str = Field(..., description="Channel name")


class YouTubeThumbnail(BaseModel):
    """YouTube video thumbnails."""
    default: Optional[str] = Field(None, description="Default thumbnail URL")
    medium: Optional[str] = Field(None, description="Medium thumbnail URL")
    high: Optional[str] = Field(None, description="High quality thumbnail URL")
    standard: Optional[str] = Field(None, description="Standard quality thumbnail URL")
    maxres: Optional[str] = Field(None, description="Maximum resolution thumbnail URL")


class YouTubeStatistics(BaseModel):
    """YouTube video statistics."""
    view_count: int = Field(..., description="Number of views")
    like_count: int = Field(..., description="Number of likes")
    comment_count: int = Field(..., description="Number of comments")


class YouTubeVideo(BaseModel):
    """Individual YouTube video item."""
    video_id: str = Field(..., description="YouTube video ID")
    title: str = Field(..., description="Video title")
    description: str = Field(..., description="Video description (truncated)")
    channel: YouTubeChannel = Field(..., description="Channel information")
    thumbnail: YouTubeThumbnail = Field(..., description="Video thumbnails")
    published_at: str = Field(..., description="Publication date (ISO 8601)")
    category_id: str = Field(..., description="Video category ID")
    tags: List[str] = Field(..., description="Video tags")
    duration: str = Field(..., description="Video duration (ISO 8601)")
    statistics: YouTubeStatistics = Field(..., description="Video statistics")
    url: str = Field(..., description="YouTube video URL")


class YouTubeTrendingResponse(BaseModel):
    """Response schema for YouTube trending videos or search results."""
    success: bool = Field(..., description="Whether the request was successful")
    country: Optional[str] = Field(None, description="Country code used (for trending)")
    category: Optional[str] = Field(None, description="Category ID used (if any)")
    query: Optional[str] = Field(None, description="Search query (for search results)")
    videos: List[YouTubeVideo] = Field(..., description="List of videos")
    count: int = Field(..., description="Number of videos returned")
    max_results: int = Field(..., description="Maximum results requested")
    timestamp: str = Field(..., description="ISO timestamp of when data was fetched")
    message: Optional[str] = Field(None, description="Optional message")
    error: Optional[str] = Field(None, description="Error type if failed")


# ============================================================================
# REDDIT SCHEMAS
# ============================================================================

class RedditTrendingRequest(BaseModel):
    """Request schema for Reddit trending posts."""
    subreddit: str = Field(
        default="all",
        description="Subreddit name (e.g., 'all', 'python', 'news')"
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of posts to return (1-100)"
    )


class RedditPost(BaseModel):
    """Individual Reddit post item."""
    post_id: str = Field(..., description="Reddit post ID")
    title: str = Field(..., description="Post title")
    author: str = Field(..., description="Post author username")
    subreddit: str = Field(..., description="Subreddit name")
    upvotes: int = Field(..., description="Number of upvotes (score)")
    upvote_ratio: float = Field(..., description="Upvote ratio (0.0-1.0)")
    num_comments: int = Field(..., description="Number of comments")
    url: str = Field(..., description="Reddit post URL")
    created_at: str = Field(..., description="Creation date (ISO 8601)")
    is_self: bool = Field(..., description="Whether this is a self/text post")
    selftext: str = Field(..., description="Self post text (truncated)")
    link_url: Optional[str] = Field(None, description="External link URL (if link post)")
    thumbnail: Optional[str] = Field(None, description="Post thumbnail URL")
    over_18: bool = Field(..., description="Whether post is NSFW")
    spoiler: bool = Field(..., description="Whether post is marked as spoiler")
    awards: int = Field(..., description="Number of awards received")


class RedditTrendingResponse(BaseModel):
    """Response schema for Reddit trending posts."""
    success: bool = Field(..., description="Whether the request was successful")
    subreddit: str = Field(..., description="Subreddit name used")
    posts: List[RedditPost] = Field(..., description="List of trending posts")
    count: int = Field(..., description="Number of posts returned")
    limit: int = Field(..., description="Maximum results requested")
    timestamp: str = Field(..., description="ISO timestamp of when data was fetched")
    message: Optional[str] = Field(None, description="Optional message")
    error: Optional[str] = Field(None, description="Error type if failed")


# ============================================================================
# EXA SCHEMAS
# ============================================================================

class ExaSearchRequest(BaseModel):
    """Request schema for Exa search."""
    action: str = Field(
        ...,
        description="Action to perform: 'search_trending' or 'deep_research'"
    )
    query: Optional[str] = Field(
        None,
        description="Search query (required for search_trending)"
    )
    topic: Optional[str] = Field(
        None,
        description="Research topic (required for deep_research)"
    )
    num_results: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of results to return"
    )


class ExaResult(BaseModel):
    """Individual Exa search result."""
    id: str = Field(..., description="Result ID")
    title: str = Field(..., description="Result title")
    url: str = Field(..., description="Result URL")
    author: Optional[str] = Field(None, description="Content author")
    published_date: Optional[str] = Field(None, description="Publication date")
    score: Optional[float] = Field(None, description="Relevance score")
    text: Optional[str] = Field(None, description="Text content/summary")
    highlights: Optional[List[str]] = Field(None, description="Content highlights")
    summary: Optional[str] = Field(None, description="AI-generated summary (deep research only)")


class ExaSearchResponse(BaseModel):
    """Response schema for Exa search."""
    success: bool = Field(..., description="Whether the request was successful")
    query: Optional[str] = Field(None, description="Search query used")
    topic: Optional[str] = Field(None, description="Research topic used")
    results: List[ExaResult] = Field(..., description="List of search results")
    count: int = Field(..., description="Number of results returned")
    num_results: int = Field(..., description="Maximum results requested")
    autoprompt_string: Optional[str] = Field(None, description="Exa autoprompt used")
    timestamp: str = Field(..., description="ISO timestamp of when data was fetched")
    message: Optional[str] = Field(None, description="Optional message")
    error: Optional[str] = Field(None, description="Error type if failed")
