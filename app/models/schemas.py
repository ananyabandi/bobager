"""Pydantic models for request/response schemas."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ExpertRequest(BaseModel):
    """Request model for finding experts."""
    topic: str = Field(..., description="Technology or topic to search for")
    timeframe_days: int = Field(default=30, ge=1, le=365, description="Number of days to look back")
    min_messages: int = Field(default=1, ge=1, description="Minimum number of messages")
    channels: Optional[List[str]] = Field(default=None, description="Specific channels to search")


class ContributorRequest(BaseModel):
    """Request model for finding contributors."""
    channel: str = Field(..., description="Channel name or ID")
    timeframe_days: int = Field(default=30, ge=1, le=365, description="Number of days to look back")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of contributors to return")
    sort_by: str = Field(default="message_count", description="Sort by: message_count, engagement, expertise")


class AnalysisRequest(BaseModel):
    """Request model for custom analysis."""
    query: str = Field(..., description="Natural language query for analysis")
    channels: Optional[List[str]] = Field(default=None, description="Specific channels to analyze")
    timeframe_days: int = Field(default=30, ge=1, le=365, description="Number of days to look back")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for analysis")


class SearchRequest(BaseModel):
    """Request model for searching and analyzing topic discussions."""
    query: str = Field(..., description="Topic or keyword to search for (e.g., 'pizza', 'React', 'deployment')")
    timeframe_days: int = Field(default=30, ge=1, le=365, description="Number of days to look back")
    channels: Optional[List[str]] = Field(default=None, description="Specific channels to search (None for all)")


class SearchResponse(BaseModel):
    """Response model for search with natural language analysis."""
    query: str
    answer: str = Field(..., description="Natural language answer about who discussed the topic")
    total_messages_found: int
    timeframe_days: int
    channels_searched: Optional[List[str]]
    timestamp: datetime


class ChatRequest(BaseModel):
    """Request model for chat-style natural language interaction."""
    message: str = Field(..., min_length=1, description="User message to analyze")


class ChatResponse(BaseModel):
    """Response model for chat-style natural language interaction."""
    message: str
    tool: str
    params: Dict[str, Any]
    response: str
    timestamp: datetime


class UserProfile(BaseModel):
    """User profile information."""
    user_id: str
    username: str
    real_name: Optional[str] = None
    email: Optional[str] = None
    title: Optional[str] = None
    avatar_url: Optional[str] = None


class MessageSummary(BaseModel):
    """Summary of a message."""
    message_id: str
    user_id: str
    channel: str
    timestamp: datetime
    text: str
    reactions: Optional[List[str]] = None
    thread_replies: int = 0


class ExpertProfile(BaseModel):
    """Expert profile with analysis."""
    user: UserProfile
    expertise_score: float = Field(..., ge=0, le=1, description="Expertise score from 0 to 1")
    message_count: int
    relevant_messages: List[MessageSummary]
    key_topics: List[str]
    analysis: str = Field(..., description="Bob's analysis of expertise")


class ContributorProfile(BaseModel):
    """Contributor profile with metrics."""
    user: UserProfile
    message_count: int
    engagement_score: float = Field(..., ge=0, le=1, description="Engagement score from 0 to 1")
    top_threads: List[MessageSummary]
    contribution_summary: str


class ExpertResponse(BaseModel):
    """Response model for expert search."""
    topic: str
    experts: List[ExpertProfile]
    total_found: int
    timeframe_days: int
    analysis_timestamp: datetime


class ContributorResponse(BaseModel):
    """Response model for contributor search."""
    channel: str
    contributors: List[ContributorProfile]
    total_found: int
    timeframe_days: int
    analysis_timestamp: datetime


class AnalysisResponse(BaseModel):
    """Response model for custom analysis."""
    query: str
    insights: str = Field(..., description="Bob's analysis insights")
    relevant_users: List[UserProfile]
    relevant_messages: List[MessageSummary]
    metadata: Dict[str, Any]
    analysis_timestamp: datetime


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    slack_api_connected: bool
    ollama_connected: bool
    timestamp: datetime

# Made with Bob
