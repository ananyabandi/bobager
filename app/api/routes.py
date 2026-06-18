"""API route handlers."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
from app.models.schemas import (
    ExpertRequest,
    ExpertResponse,
    ContributorRequest,
    ContributorResponse,
    AnalysisRequest,
    AnalysisResponse,
    SearchRequest,
    SearchResponse,
    HealthResponse
)
from app.services.analysis_service import analysis_service
from app.services.slack_client import slack_client
from app.services.ollama_client import ollama_client
from app.utils.logger import setup_logger
from app.utils.cache import cache_manager
from app import __version__

logger = setup_logger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns system status and connectivity information.
    """
    try:
        slack_connected = await slack_client.health_check()
        ollama_connected = await ollama_client.health_check()
        
        return HealthResponse(
            status="healthy" if (slack_connected and ollama_connected) else "degraded",
            version=__version__,
            slack_api_connected=slack_connected,
            ollama_connected=ollama_connected,
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@router.get("/experts/{topic}", response_model=ExpertResponse)
async def find_experts(
    topic: str,
    timeframe_days: int = Query(default=30, ge=1, le=365),
    min_messages: int = Query(default=5, ge=1),
    channels: Optional[str] = Query(default=None, description="Comma-separated channel names")
):
    """
    Find experts on a specific technology or topic.
    
    Args:
        topic: Technology or topic to search for (e.g., "React", "Python", "DevOps")
        timeframe_days: Number of days to look back (1-365)
        min_messages: Minimum number of messages required to be considered
        channels: Optional comma-separated list of channel names to search
        
    Returns:
        List of experts ranked by expertise score with analysis
    """
    try:
        channel_list = channels.split(",") if channels else None
        
        result = await analysis_service.find_experts(
            topic=topic,
            timeframe_days=timeframe_days,
            min_messages=min_messages,
            channels=channel_list
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error finding experts for topic '{topic}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/experts", response_model=ExpertResponse)
async def find_experts_post(request: ExpertRequest):
    """
    Find experts on a specific technology or topic (POST version).
    
    Accepts a JSON request body with search parameters.
    """
    try:
        result = await analysis_service.find_experts(
            topic=request.topic,
            timeframe_days=request.timeframe_days,
            min_messages=request.min_messages,
            channels=request.channels
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error finding experts for topic '{request.topic}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contributors/{channel}", response_model=ContributorResponse)
async def find_contributors(
    channel: str,
    timeframe_days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=10, ge=1, le=50),
    sort_by: str = Query(default="message_count", regex="^(message_count|engagement)$")
):
    """
    Find key contributors in a specific channel.
    
    Args:
        channel: Channel name or ID
        timeframe_days: Number of days to look back (1-365)
        limit: Maximum number of contributors to return (1-50)
        sort_by: Sort criteria - "message_count" or "engagement"
        
    Returns:
        List of top contributors with engagement metrics
    """
    try:
        result = await analysis_service.find_contributors(
            channel=channel,
            timeframe_days=timeframe_days,
            limit=limit,
            sort_by=sort_by
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error finding contributors for channel '{channel}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contributors", response_model=ContributorResponse)
async def find_contributors_post(request: ContributorRequest):
    """
    Find key contributors in a specific channel (POST version).
    
    Accepts a JSON request body with search parameters.
    """
    try:
        result = await analysis_service.find_contributors(
            channel=request.channel,
            timeframe_days=request.timeframe_days,
            limit=request.limit,
            sort_by=request.sort_by
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error finding contributors for channel '{request.channel}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=AnalysisResponse)
async def custom_analysis(request: AnalysisRequest):
    """
    Perform custom analysis based on a natural language query.
    
    This endpoint allows flexible queries like:
    - "Who are the experts in database optimization?"
    - "Find people discussing microservices architecture"
    - "Identify contributors to the recent API redesign discussion"
    
    Args:
        request: Analysis request with query and optional parameters
        
    Returns:
        Analysis insights with relevant users and messages
    """
    try:
        result = await analysis_service.custom_analysis(
            query=request.query,
            channels=request.channels,
            timeframe_days=request.timeframe_days,
            context=request.context
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in custom analysis for query '{request.query}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=SearchResponse)
async def search_topic(request: SearchRequest):
    """
    Search all channels for a topic and get natural language analysis.
    
    This endpoint searches Slack messages for a specific topic/keyword and uses
    Ollama to provide a natural language answer about who discussed it the most.
    
    Example queries:
    - "pizza" -> "Based on 50 messages, John (15 messages) and Sarah (12 messages)
                  talked about pizza most, focusing on toppings and delivery..."
    - "React" -> "Based on 30 messages, Mike (10 messages) discussed React most,
                  primarily about hooks and performance optimization..."
    
    Args:
        request: Search request with query and optional parameters
        
    Returns:
        Natural language answer with metadata about the search
    """
    try:
        result = await analysis_service.search_and_analyze(
            query=request.query,
            timeframe_days=request.timeframe_days,
            channels=request.channels
        )
        
        return SearchResponse(
            query=request.query,
            answer=result["answer"],
            total_messages_found=result["total_messages"],
            timeframe_days=request.timeframe_days,
            channels_searched=request.channels,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error in search for query '{request.query}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/stats")
async def get_cache_stats():
    """
    Get cache statistics.
    
    Returns information about cache usage and performance.
    """
    try:
        stats = cache_manager.get_stats()
        return {
            "cache_stats": stats,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/clear")
async def clear_cache():
    """
    Clear all cached data.
    
    Use this to force fresh data retrieval on next requests.
    """
    try:
        cache_manager.clear()
        return {
            "message": "Cache cleared successfully",
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Made with Bob
