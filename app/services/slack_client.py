"""Slack API client using slack-sdk."""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class SlackClient:
    """Client for interacting with Slack API."""
    
    def __init__(self):
        """Initialize Slack client."""
        self.client = WebClient(token=settings.slack_bot_token)
        # Separate client for search API which requires user token
        self.search_client = WebClient(token=settings.slack_user_token) if settings.slack_user_token else None
        self.connected = False
        logger.info("SlackClient initialized")
        if not settings.slack_user_token:
            logger.warning("No user token provided - search_messages will not work")
    
    async def connect(self) -> None:
        """Test connection to Slack API."""
        try:
            response = self.client.auth_test()
            self.connected = response["ok"]
            if self.connected:
                logger.info(f"Connected to Slack workspace: {response['team']}")
        except SlackApiError as e:
            logger.error(f"Failed to connect to Slack: {e}")
            self.connected = False
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from Slack API."""
        self.connected = False
        logger.info("Disconnected from Slack")
    
    async def get_channels(self) -> List[Dict[str, Any]]:
        """
        Get list of Slack channels.
        
        Returns:
            List of channel dictionaries
        """
        try:
            channels = []
            cursor = None
            
            while True:
                response = self.client.conversations_list(
                    types="public_channel,private_channel",
                    limit=200,
                    cursor=cursor
                )
                
                channels.extend(response.get("channels", []))
                
                cursor = response.get("response_metadata", {}).get("next_cursor")
                if not cursor:
                    break
            
            logger.debug(f"Retrieved {len(channels)} channels")
            return channels
            
        except SlackApiError as e:
            logger.error(f"Error getting channels: {e}")
            raise
    
    async def get_channel_messages(
        self,
        channel_id: str,
        limit: int = 100,
        since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get messages from a specific channel.
        
        Args:
            channel_id: Channel ID
            limit: Maximum number of messages to retrieve
            since: Only get messages after this timestamp
            
        Returns:
            List of message dictionaries
        """
        try:
            messages = []
            cursor = None
            oldest = str(since.timestamp()) if since else None
            
            while len(messages) < limit:
                response = self.client.conversations_history(
                    channel=channel_id,
                    limit=min(200, limit - len(messages)),
                    oldest=oldest,
                    cursor=cursor
                )
                
                messages.extend(response.get("messages", []))
                
                cursor = response.get("response_metadata", {}).get("next_cursor")
                if not cursor or len(messages) >= limit:
                    break
            
            logger.debug(f"Retrieved {len(messages)} messages from channel {channel_id}")
            return messages[:limit]
            
        except SlackApiError as e:
            logger.error(f"Error getting channel messages: {e}")
            raise
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get user profile information.
        
        Args:
            user_id: User ID
            
        Returns:
            User profile dictionary
        """
        try:
            response = self.client.users_info(user=user_id)
            logger.debug(f"Retrieved profile for user {user_id}")
            return response.get("user", {})
            
        except SlackApiError as e:
            logger.error(f"Error getting user profile: {e}")
            raise
    
    async def search_messages(
        self,
        query: str,
        count: int = 100,
        sort: str = "timestamp"
    ) -> List[Dict[str, Any]]:
        """
        Search messages across all channels.
        
        NOTE: This endpoint requires a user token (xoxp-), not a bot token.
        
        Args:
            query: Search query
            count: Maximum number of results
            sort: Sort order (timestamp, score)
            
        Returns:
            List of matching messages
            
        Raises:
            ValueError: If no user token is configured
            SlackApiError: If the Slack API request fails
        """
        if not self.search_client:
            raise ValueError(
                "search_messages requires a user token (SLACK_USER_TOKEN). "
                "Bot tokens (xoxb-) are not allowed for this endpoint. "
                "Please configure SLACK_USER_TOKEN in your .env file."
            )
        
        try:
            messages = []
            page = 1
            
            while len(messages) < count:
                response = self.search_client.search_messages(
                    query=query,
                    count=min(100, count - len(messages)),
                    page=page,
                    sort=sort
                )
                
                matches = response.get("messages", {}).get("matches", [])
                if not matches:
                    break
                
                messages.extend(matches)
                page += 1
                
                if len(matches) < 100:  # Last page
                    break
            
            logger.debug(f"Found {len(messages)} messages matching query: {query}")
            return messages[:count]
            
        except SlackApiError as e:
            logger.error(f"Error searching messages: {e}")
            raise
    
    async def get_thread_replies(
        self,
        channel_id: str,
        thread_ts: str
    ) -> List[Dict[str, Any]]:
        """
        Get replies in a thread.
        
        Args:
            channel_id: Channel ID
            thread_ts: Thread timestamp
            
        Returns:
            List of reply messages
        """
        try:
            response = self.client.conversations_replies(
                channel=channel_id,
                ts=thread_ts
            )
            
            replies = response.get("messages", [])
            logger.debug(f"Retrieved {len(replies)} replies from thread {thread_ts}")
            return replies
            
        except SlackApiError as e:
            logger.error(f"Error getting thread replies: {e}")
            raise
    
    async def get_channel_by_name(self, channel_name: str) -> Optional[Dict[str, Any]]:
        """
        Get channel by name.
        
        Args:
            channel_name: Channel name (without #)
            
        Returns:
            Channel dictionary or None if not found
        """
        try:
            channels = await self.get_channels()
            for channel in channels:
                if channel.get("name") == channel_name:
                    return channel
            return None
            
        except Exception as e:
            logger.error(f"Error getting channel by name: {e}")
            raise
    
    async def health_check(self) -> bool:
        """
        Check if connection to Slack is healthy.
        
        Returns:
            True if connected and healthy, False otherwise
        """
        try:
            response = self.client.auth_test()
            return response.get("ok", False)
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# Global Slack client instance
slack_client = SlackClient()

# Made with Bob
