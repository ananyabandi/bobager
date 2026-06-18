"""Service for aggregating Slack data with Bob LLM analysis."""
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.services.slack_service import slack_service
from app.services.ollama_client import ollama_client
from app.models.schemas import (
    ExpertProfile,
    ContributorProfile,
    UserProfile,
    MessageSummary,
    ExpertResponse,
    ContributorResponse,
    AnalysisResponse
)
from app.utils.logger import setup_logger
from app.utils.cache import cache_manager

logger = setup_logger(__name__)


class AnalysisService:
    """Service for combining Slack data with Bob LLM insights."""
    
    def __init__(self):
        """Initialize analysis service."""
        self.slack_service = slack_service
        self.ollama_client = ollama_client
    
    async def find_experts(
        self,
        topic: str,
        timeframe_days: int = 30,
        min_messages: int = 5,
        channels: Optional[List[str]] = None
    ) -> ExpertResponse:
        """
        Find experts on a specific topic.
        
        Args:
            topic: Technology or topic to search for
            timeframe_days: Number of days to look back
            min_messages: Minimum number of messages required
            channels: Specific channels to search
            
        Returns:
            ExpertResponse with ranked experts
        """
        cache_key = f"experts_{topic}_{timeframe_days}_{min_messages}_{channels}"
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
        
        try:
            # Get relevant messages
            messages = await self.slack_service.get_messages_by_topic(
                topic=topic,
                timeframe_days=timeframe_days,
                channels=channels
            )
            
            if not messages:
                return ExpertResponse(
                    topic=topic,
                    experts=[],
                    total_found=0,
                    timeframe_days=timeframe_days,
                    analysis_timestamp=datetime.now()
                )
            
            # Get user profiles
            user_ids = [msg.get("user") for msg in messages if msg.get("user")]
            unique_user_ids = list(set(uid for uid in user_ids if uid))
            user_profiles = await self.slack_service.get_user_profiles(unique_user_ids)
            
            # Aggregate user activity
            activity = await self.slack_service.aggregate_user_activity(messages)
            
            # Filter users by minimum message count
            qualified_users = {
                uid: data for uid, data in activity.items()
                if data["message_count"] >= min_messages
            }
            
            if not qualified_users:
                return ExpertResponse(
                    topic=topic,
                    experts=[],
                    total_found=0,
                    timeframe_days=timeframe_days,
                    analysis_timestamp=datetime.now()
                )
            
            # Get Bob's analysis
            bob_analysis = await self.ollama_client.analyze_expertise(
                topic=topic,
                messages=messages,
                user_profiles=user_profiles
            )
            
            # Build expert profiles
            experts = []
            bob_experts = bob_analysis.get("experts", [])
            
            for bob_expert in bob_experts:
                user_id = bob_expert.get("user_id")
                if user_id not in qualified_users:
                    continue
                
                user_data = user_profiles.get(user_id, {})
                user_activity = qualified_users[user_id]
                
                # Convert messages to MessageSummary
                relevant_messages = [
                    self.slack_service.convert_to_message_summary(msg)
                    for msg in user_activity["messages"][:10]  # Top 10 messages
                ]
                
                expert = ExpertProfile(
                    user=self.slack_service.convert_to_user_profile(user_data),
                    expertise_score=bob_expert.get("expertise_score", 0.5),
                    message_count=user_activity["message_count"],
                    relevant_messages=relevant_messages,
                    key_topics=bob_expert.get("key_topics", []),
                    analysis=bob_expert.get("analysis", "")
                )
                experts.append(expert)
            
            # Sort by expertise score
            experts.sort(key=lambda x: x.expertise_score, reverse=True)
            
            response = ExpertResponse(
                topic=topic,
                experts=experts,
                total_found=len(experts),
                timeframe_days=timeframe_days,
                analysis_timestamp=datetime.now()
            )
            
            cache_manager.set(cache_key, response)
            logger.info(f"Found {len(experts)} experts for topic: {topic}")
            return response
            
        except Exception as e:
            logger.error(f"Error finding experts: {e}")
            raise
    
    async def find_contributors(
        self,
        channel: str,
        timeframe_days: int = 30,
        limit: int = 10,
        sort_by: str = "message_count"
    ) -> ContributorResponse:
        """
        Find key contributors in a channel.
        
        Args:
            channel: Channel name or ID
            timeframe_days: Number of days to look back
            limit: Maximum number of contributors to return
            sort_by: Sort criteria
            
        Returns:
            ContributorResponse with ranked contributors
        """
        cache_key = f"contributors_{channel}_{timeframe_days}_{limit}_{sort_by}"
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
        
        try:
            # Get channel messages
            messages = await self.slack_service.get_channel_messages(
                channel=channel,
                timeframe_days=timeframe_days,
                limit=200
            )
            
            if not messages:
                return ContributorResponse(
                    channel=channel,
                    contributors=[],
                    total_found=0,
                    timeframe_days=timeframe_days,
                    analysis_timestamp=datetime.now()
                )
            
            # Get user profiles
            user_ids = [msg.get("user") for msg in messages if msg.get("user")]
            unique_user_ids = list(set(uid for uid in user_ids if uid))
            user_profiles = await self.slack_service.get_user_profiles(unique_user_ids)
            
            # Aggregate user activity
            activity = await self.slack_service.aggregate_user_activity(messages)
            
            # Get Bob's analysis
            bob_analysis = await self.ollama_client.analyze_contributors(
                channel=channel,
                messages=messages,
                user_profiles=user_profiles
            )
            
            # Build contributor profiles
            contributors = []
            bob_contributors = bob_analysis.get("contributors", [])
            
            for bob_contributor in bob_contributors:
                user_id = bob_contributor.get("user_id")
                if user_id not in activity:
                    continue
                
                user_data = user_profiles.get(user_id, {})
                user_activity = activity[user_id]
                
                # Get top threads
                top_messages = sorted(
                    user_activity["messages"],
                    key=lambda m: m.get("reply_count", 0) + len(m.get("reactions", [])),
                    reverse=True
                )[:5]
                
                top_threads = [
                    self.slack_service.convert_to_message_summary(msg)
                    for msg in top_messages
                ]
                
                contributor = ContributorProfile(
                    user=self.slack_service.convert_to_user_profile(user_data),
                    message_count=user_activity["message_count"],
                    engagement_score=bob_contributor.get("engagement_score", 0.5),
                    top_threads=top_threads,
                    contribution_summary=bob_contributor.get("contribution_summary", "")
                )
                contributors.append(contributor)
            
            # Sort based on criteria
            if sort_by == "engagement":
                contributors.sort(key=lambda x: x.engagement_score, reverse=True)
            else:  # message_count
                contributors.sort(key=lambda x: x.message_count, reverse=True)
            
            # Limit results
            contributors = contributors[:limit]
            
            response = ContributorResponse(
                channel=channel,
                contributors=contributors,
                total_found=len(contributors),
                timeframe_days=timeframe_days,
                analysis_timestamp=datetime.now()
            )
            
            cache_manager.set(cache_key, response)
            logger.info(f"Found {len(contributors)} contributors for channel: {channel}")
            return response
            
        except Exception as e:
            logger.error(f"Error finding contributors: {e}")
            raise
    
    async def custom_analysis(
        self,
        query: str,
        channels: Optional[List[str]] = None,
        timeframe_days: int = 30,
        context: Optional[Dict[str, Any]] = None
    ) -> AnalysisResponse:
        """
        Perform custom analysis based on user query.
        
        Args:
            query: Natural language query
            channels: Specific channels to analyze
            timeframe_days: Number of days to look back
            context: Additional context
            
        Returns:
            AnalysisResponse with insights
        """
        cache_key = f"analysis_{query}_{channels}_{timeframe_days}"
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
        
        try:
            # Get relevant messages (use query as search term)
            messages = await self.slack_service.get_messages_by_topic(
                topic=query,
                timeframe_days=timeframe_days,
                channels=channels
            )
            
            if not messages:
                return AnalysisResponse(
                    query=query,
                    insights="No relevant messages found for the given query.",
                    relevant_users=[],
                    relevant_messages=[],
                    metadata={"message_count": 0},
                    analysis_timestamp=datetime.now()
                )
            
            # Get user profiles
            user_ids = [msg.get("user") for msg in messages if msg.get("user")]
            unique_user_ids = list(set(uid for uid in user_ids if uid))
            user_profiles = await self.slack_service.get_user_profiles(unique_user_ids)
            
            # Get Bob's analysis
            bob_analysis = await self.ollama_client.custom_analysis(
                query=query,
                messages=messages,
                user_profiles=user_profiles,
                context=context
            )
            
            # Extract relevant users
            relevant_user_ids = bob_analysis.get("relevant_users", [])
            relevant_users = [
                self.slack_service.convert_to_user_profile(user_profiles.get(uid, {}))
                for uid in relevant_user_ids
                if uid in user_profiles
            ]
            
            # Extract relevant messages
            relevant_msg_ids = bob_analysis.get("key_messages", [])
            relevant_messages = [
                self.slack_service.convert_to_message_summary(msg)
                for msg in messages
                if msg.get("ts") in relevant_msg_ids
            ]
            
            response = AnalysisResponse(
                query=query,
                insights=bob_analysis.get("insights", ""),
                relevant_users=relevant_users,
                relevant_messages=relevant_messages,
                metadata={
                    "total_messages_analyzed": len(messages),
                    "channels_searched": channels or "all",
                    "timeframe_days": timeframe_days
                },
                analysis_timestamp=datetime.now()
            )
            
            cache_manager.set(cache_key, response)
            logger.info(f"Completed custom analysis for query: {query}")
            return response
            
        except Exception as e:
            logger.error(f"Error in custom analysis: {e}")
            raise
    
    async def search_and_analyze(
        self,
        query: str,
        timeframe_days: int = 30,
        channels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search for messages about a topic and provide natural language analysis.
        
        Args:
            query: Topic or keyword to search for
            timeframe_days: Number of days to look back
            channels: Specific channels to search
            
        Returns:
            Dictionary with answer and metadata
        """
        cache_key = f"search_analyze_{query}_{timeframe_days}_{channels}"
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
        
        try:
            # Get relevant messages using search
            messages = await self.slack_service.get_messages_by_topic(
                topic=query,
                timeframe_days=timeframe_days,
                channels=channels
            )
            
            if not messages:
                return {
                    "answer": f"No messages found about '{query}' in the specified timeframe.",
                    "total_messages": 0,
                    "channels_searched": channels
                }
            
            # Get user profiles
            user_ids = [msg.get("user") for msg in messages if msg.get("user")]
            unique_user_ids = list(set(uid for uid in user_ids if uid))
            user_profiles = await self.slack_service.get_user_profiles(unique_user_ids)
            
            # Get natural language analysis from Ollama
            answer = await self.ollama_client.analyze_topic_discussion(
                query=query,
                messages=messages,
                user_profiles=user_profiles
            )
            
            result = {
                "answer": answer,
                "total_messages": len(messages),
                "channels_searched": channels
            }
            
            cache_manager.set(cache_key, result)
            logger.info(f"Completed search and analysis for query: {query}")
            return result
            
        except Exception as e:
            logger.error(f"Error in search and analysis: {e}")
            raise


# Global analysis service instance
analysis_service = AnalysisService()

# Made with Bob
