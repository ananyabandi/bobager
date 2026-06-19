"""Service for aggregating Slack data with Bob LLM analysis."""
import json
import re
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

    @staticmethod
    def _extract_user_id(candidate: Any) -> Optional[str]:
        """Normalize Ollama user references into a Slack user ID string."""
        if isinstance(candidate, str):
            return candidate

        if isinstance(candidate, dict):
            for key in ("user_id", "id", "username"):
                value = candidate.get(key)
                if isinstance(value, str) and value:
                    return value

        return None

    @staticmethod
    def _extract_message_id(candidate: Any) -> Optional[str]:
        """Normalize Ollama message references into a Slack timestamp string."""
        if isinstance(candidate, str):
            return candidate

        if isinstance(candidate, dict):
            for key in ("message_id", "ts", "id"):
                value = candidate.get(key)
                if value is not None:
                    return str(value)

        return None

    @staticmethod
    def _display_name(user_data: Dict[str, Any], fallback: str) -> str:
        """Build a human-readable name for a Slack user."""
        profile = user_data.get("profile", {}) if isinstance(user_data, dict) else {}

        for value in (
            user_data.get("real_name") if isinstance(user_data, dict) else None,
            profile.get("real_name"),
            user_data.get("name") if isinstance(user_data, dict) else None,
            profile.get("display_name"),
            fallback,
        ):
            if isinstance(value, str) and value:
                return value

        return fallback

    @classmethod
    def _sanitize_insights(cls, insights: str, user_profiles: Dict[str, Dict[str, Any]]) -> str:
        """Replace or remove Slack-style IDs that are not backed by known user profiles."""
        sanitized = insights

        for user_id, user_data in user_profiles.items():
            display_name = cls._display_name(user_data, user_id)
            sanitized = re.sub(rf"\b{re.escape(user_id)}\b", display_name, sanitized)

        known_user_ids = set(user_profiles)

        def replace_unknown_user(match: re.Match[str]) -> str:
            user_id = match.group(0)
            if user_id in known_user_ids:
                return user_id
            return "another user"

        return re.sub(r"\bU[A-Z0-9]{2,}\b", replace_unknown_user, sanitized)

    @staticmethod
    def _build_custom_analysis_search_terms(query: str) -> List[str]:
        """Derive fallback Slack search terms from a natural-language query."""
        normalized_query = query.strip()
        terms: List[str] = [normalized_query] if normalized_query else []
        lowered = normalized_query.lower()
        mentions_code = "code" in lowered
        asks_about_person_topics = (
            "talk about" in lowered
            or "talks about" in lowered
            or "discuss" in lowered
            or "what does" in lowered
        )

        name_matches = re.findall(r"(?:code\s+)?([a-z]+\s+[a-z]+)\s+(?:wrote|posted|put)", lowered)
        if not name_matches:
            name_matches = re.findall(
                r"(?:what\s+does\s+)?([a-z]+\s+[a-z]+)\s+(?:talk\s+about|talks\s+about|discuss(?:\s+about)?)",
                lowered,
            )

        for raw_name in name_matches:
            cleaned_name = " ".join(part.capitalize() for part in raw_name.split())

            if asks_about_person_topics:
                terms.append(f'from:"{cleaned_name}"')
                terms.append(f"from:{cleaned_name.replace(' ', '.')}")

            if mentions_code:
                terms.append(f'"{cleaned_name}" code')
                terms.append(f"{cleaned_name} code")

            terms.append(f'"{cleaned_name}"')
            terms.append(cleaned_name)

        if mentions_code and not name_matches:
            condensed = re.sub(r"[^a-z0-9\s]", " ", lowered)
            condensed = re.sub(r"\s+", " ", condensed).strip()
            if condensed and condensed != normalized_query:
                terms.append(condensed)

        unique_terms: List[str] = []
        seen = set()
        for term in terms:
            candidate = term.strip()
            if candidate and candidate not in seen:
                seen.add(candidate)
                unique_terms.append(candidate)

        return unique_terms

    async def _get_messages_for_custom_analysis(
        self,
        query: str,
        timeframe_days: int,
        channels: Optional[List[str]],
    ) -> List[Dict[str, Any]]:
        """Search Slack using the original query plus a few derived fallback terms."""
        search_terms = self._build_custom_analysis_search_terms(query)
        combined_messages: List[Dict[str, Any]] = []
        seen_messages = set()
        max_messages = 200

        for search_term in search_terms:
            messages = await self.slack_service.get_messages_by_topic(
                topic=search_term,
                timeframe_days=timeframe_days,
                channels=channels,
            )

            for message in messages:
                message_key = (
                    str(message.get("ts", "")),
                    str(message.get("user", "")),
                    str(message.get("text", "")),
                )
                if message_key in seen_messages:
                    continue
                seen_messages.add(message_key)
                combined_messages.append(message)
                if len(combined_messages) >= max_messages:
                    return combined_messages

        return combined_messages

    def _build_fallback_experts(
        self,
        topic: str,
        qualified_users: Dict[str, Dict[str, Any]],
        user_profiles: Dict[str, Dict[str, Any]]
    ) -> List[ExpertProfile]:
        """Build heuristic expert results when the LLM does not return any valid experts."""
        ranked_users = sorted(
            qualified_users.items(),
            key=lambda item: (
                item[1].get("message_count", 0),
                item[1].get("reaction_count", 0),
                item[1].get("thread_count", 0),
            ),
            reverse=True,
        )
        highest_message_count = ranked_users[0][1].get("message_count", 1) if ranked_users else 1
        experts: List[ExpertProfile] = []

        for user_id, user_activity in ranked_users[:5]:
            user_data = user_profiles.get(user_id, {})
            message_count = user_activity.get("message_count", 0)
            score = 0.5 + 0.4 * (message_count / max(highest_message_count, 1))
            display_name = self._display_name(user_data, user_id)
            relevant_messages = [
                self.slack_service.convert_to_message_summary(msg)
                for msg in user_activity.get("messages", [])[:10]
            ]

            experts.append(
                ExpertProfile(
                    user=self.slack_service.convert_to_user_profile(user_data),
                    expertise_score=min(score, 0.95),
                    message_count=message_count,
                    relevant_messages=relevant_messages,
                    key_topics=[topic],
                    analysis=(
                        f"{display_name} mentioned {topic} in {message_count} matching "
                        f"message{'s' if message_count != 1 else ''}."
                    ),
                )
            )

        return experts
    
    async def find_experts(
        self,
        topic: str,
        timeframe_days: int = 30,
        min_messages: int = 1,
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
        # Convert channels list to tuple for hashable cache key
        channels_key = tuple(channels) if channels else None
        cache_key = f"experts_{topic}_{timeframe_days}_{min_messages}_{channels_key}"
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

            if not experts and qualified_users:
                logger.info(
                    "Ollama returned no valid experts for topic '%s'; using Slack activity fallback",
                    topic,
                )
                experts = self._build_fallback_experts(
                    topic=topic,
                    qualified_users=qualified_users,
                    user_profiles=user_profiles,
                )
            
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
        # Convert channels list to tuple for hashable cache key
        channels_key = tuple(channels) if channels else None
        cache_key = f"analysis_{query}_{channels_key}_{timeframe_days}"
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
        
        try:
            messages = await self._get_messages_for_custom_analysis(
                query=query,
                timeframe_days=timeframe_days,
                channels=channels,
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
            relevant_user_ids = [
                user_id
                for user_id in (
                    self._extract_user_id(candidate)
                    for candidate in bob_analysis.get("relevant_users", [])
                )
                if user_id
            ]
            relevant_users = [
                self.slack_service.convert_to_user_profile(user_profiles.get(uid, {}))
                for uid in relevant_user_ids
                if uid in user_profiles
            ]
            
            # Extract relevant messages
            relevant_msg_ids = {
                message_id
                for message_id in (
                    self._extract_message_id(candidate)
                    for candidate in bob_analysis.get("key_messages", [])
                )
                if message_id
            }
            relevant_messages = [
                self.slack_service.convert_to_message_summary(msg)
                for msg in messages
                if msg.get("ts") in relevant_msg_ids
            ]
            
            # Handle insights - convert to string if it's a dict
            insights_data = bob_analysis.get("insights", "")
            if isinstance(insights_data, dict):
                # Convert dict to formatted string
                insights = json.dumps(insights_data, indent=2)
            else:
                insights = str(insights_data)
            insights = self._sanitize_insights(insights, user_profiles)
            
            response = AnalysisResponse(
                query=query,
                insights=insights,
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
        # Convert channels list to tuple for hashable cache key
        channels_key = tuple(channels) if channels else None
        cache_key = f"search_analyze_{query}_{timeframe_days}_{channels_key}"
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
