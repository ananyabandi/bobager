"""Service layer for Slack data operations."""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.services.slack_client import slack_client
from app.models.schemas import UserProfile, MessageSummary
from app.utils.logger import setup_logger
from app.utils.cache import cache_manager

logger = setup_logger(__name__)


class SlackService:
    """Service for fetching and processing Slack data."""
    
    def __init__(self):
        """Initialize Slack service."""
        self.slack_client = slack_client
    
    async def get_messages_by_topic(
        self,
        topic: str,
        timeframe_days: int = 30,
        channels: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get messages related to a specific topic.
        
        Args:
            topic: Topic to search for
            timeframe_days: Number of days to look back
            channels: Specific channels to search (None for all)
            
        Returns:
            List of relevant messages
        """
        cache_key = f"messages_topic_{topic}_{timeframe_days}_{channels}"
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
        
        try:
            # Search for messages containing the topic
            messages = await self.slack_client.search_messages(
                query=topic,
                count=200,
                sort="timestamp"
            )
            
            # Filter by timeframe
            cutoff_date = datetime.now() - timedelta(days=timeframe_days)
            filtered_messages = [
                msg for msg in messages
                if datetime.fromtimestamp(float(msg.get("ts", 0))) > cutoff_date
            ]
            
            # Filter by channels if specified
            if channels:
                filtered_messages = [
                    msg for msg in filtered_messages
                    if msg.get("channel", {}).get("name") in channels
                ]
            
            cache_manager.set(cache_key, filtered_messages)
            logger.info(f"Found {len(filtered_messages)} messages for topic: {topic}")
            return filtered_messages
            
        except Exception as e:
            logger.error(f"Error getting messages by topic: {e}")
            raise
    
    async def get_channel_messages(
        self,
        channel: str,
        timeframe_days: int = 30,
        limit: int = 200
    ) -> List[Dict[str, Any]]:
        """
        Get messages from a specific channel.
        
        Args:
            channel: Channel name or ID
            timeframe_days: Number of days to look back
            limit: Maximum number of messages
            
        Returns:
            List of messages
        """
        cache_key = f"channel_messages_{channel}_{timeframe_days}_{limit}"
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
        
        try:
            # Get channel ID if name provided
            channels = await self.slack_client.get_channels()
            channel_id = None
            
            for ch in channels:
                if ch.get("name") == channel or ch.get("id") == channel:
                    channel_id = ch.get("id")
                    break
            
            if not channel_id:
                raise ValueError(f"Channel not found: {channel}")
            
            # Get messages
            since = datetime.now() - timedelta(days=timeframe_days)
            messages = await self.slack_client.get_channel_messages(
                channel_id=channel_id,
                limit=limit,
                since=since
            )
            
            cache_manager.set(cache_key, messages)
            logger.info(f"Retrieved {len(messages)} messages from channel: {channel}")
            return messages
            
        except Exception as e:
            logger.error(f"Error getting channel messages: {e}")
            raise
    
    async def get_user_profiles(
        self,
        user_ids: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get user profiles for multiple users.
        
        Args:
            user_ids: List of user IDs
            
        Returns:
            Dictionary of user profiles keyed by user_id
        """
        profiles = {}
        
        for user_id in user_ids:
            cache_key = f"user_profile_{user_id}"
            cached = cache_manager.get(cache_key)
            
            if cached:
                profiles[user_id] = cached
            else:
                try:
                    profile = await self.slack_client.get_user_profile(user_id)
                    profiles[user_id] = profile
                    cache_manager.set(cache_key, profile)
                except Exception as e:
                    logger.warning(f"Could not get profile for user {user_id}: {e}")
                    profiles[user_id] = {"id": user_id, "name": user_id}
        
        logger.info(f"Retrieved {len(profiles)} user profiles")
        return profiles
    
    async def get_thread_context(
        self,
        channel_id: str,
        thread_ts: str
    ) -> List[Dict[str, Any]]:
        """
        Get all messages in a thread.
        
        Args:
            channel_id: Channel ID
            thread_ts: Thread timestamp
            
        Returns:
            List of thread messages
        """
        cache_key = f"thread_{channel_id}_{thread_ts}"
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
        
        try:
            replies = await self.slack_client.get_thread_replies(
                channel_id=channel_id,
                thread_ts=thread_ts
            )
            
            cache_manager.set(cache_key, replies)
            logger.info(f"Retrieved thread with {len(replies)} messages")
            return replies
            
        except Exception as e:
            logger.error(f"Error getting thread context: {e}")
            raise
    
    def convert_to_user_profile(self, slack_user: Dict[str, Any]) -> UserProfile:
        """
        Convert Slack user data to UserProfile model.
        
        Args:
            slack_user: Slack user dictionary
            
        Returns:
            UserProfile instance
        """
        profile = slack_user.get("profile", {})
        return UserProfile(
            user_id=slack_user.get("id", ""),
            username=slack_user.get("name", ""),
            real_name=slack_user.get("real_name") or profile.get("real_name"),
            email=profile.get("email"),
            title=profile.get("title"),
            avatar_url=profile.get("image_192")
        )
    
    def convert_to_message_summary(self, slack_message: Dict[str, Any]) -> MessageSummary:
        """
        Convert Slack message to MessageSummary model.
        
        Args:
            slack_message: Slack message dictionary
            
        Returns:
            MessageSummary instance
        """
        ts = slack_message.get("ts", "0")
        timestamp = datetime.fromtimestamp(float(ts))
        
        reactions = []
        if "reactions" in slack_message:
            reactions = [r.get("name", "") for r in slack_message["reactions"]]
        
        return MessageSummary(
            message_id=ts,
            user_id=slack_message.get("user", ""),
            channel=slack_message.get("channel", ""),
            timestamp=timestamp,
            text=slack_message.get("text", ""),
            reactions=reactions if reactions else None,
            thread_replies=slack_message.get("reply_count", 0)
        )
    
    async def aggregate_user_activity(
        self,
        messages: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Aggregate activity metrics for users from messages.
        
        Args:
            messages: List of messages
            
        Returns:
            Dictionary of user activity metrics
        """
        activity = {}
        
        for msg in messages:
            user_id = msg.get("user")
            if not user_id:
                continue
            
            if user_id not in activity:
                activity[user_id] = {
                    "message_count": 0,
                    "thread_count": 0,
                    "reaction_count": 0,
                    "messages": []
                }
            
            activity[user_id]["message_count"] += 1
            activity[user_id]["messages"].append(msg)
            
            if msg.get("thread_ts"):
                activity[user_id]["thread_count"] += 1
            
            reactions = msg.get("reactions", [])
            for reaction in reactions:
                activity[user_id]["reaction_count"] += reaction.get("count", 0)
        
        return activity


# Global Slack service instance
slack_service = SlackService()

# Made with Bob
