"""Ollama LLM client for chat analysis."""
import httpx
import json
from typing import Dict, Any, List, Optional
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

EXPLANATION_HINTS = (
    "understand",
    "explain",
    "what does",
    "what do",
    "how does",
    "walk me through",
    "summarize",
    "summary",
    "code",
)


class OllamaClient:
    """Client for interacting with Ollama LLM."""
    
    def __init__(self):
        """Initialize Ollama client."""
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        logger.info(f"OllamaClient initialized with model: {self.model}")

    async def ask(self, prompt: str) -> str:
        """Ask Ollama for a plain-text response."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
    
    async def analyze_expertise(
        self,
        topic: str,
        messages: List[Dict[str, Any]],
        user_profiles: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze messages to identify experts on a topic.
        
        Args:
            topic: Technology or topic to analyze
            messages: List of message dictionaries
            user_profiles: Dictionary of user profiles keyed by user_id
            
        Returns:
            Analysis results with expert rankings
        """
        try:
            # Build context from messages
            context = self._build_message_context(messages, user_profiles)
            available_user_ids = sorted(user_profiles.keys())
            
            # Create prompt for Ollama
            prompt = f"""Analyze the following Slack messages to identify experts on the topic: "{topic}"

Context:
{context}

Task:
1. Identify users who demonstrate expertise in {topic}
2. Score each user's expertise from 0 to 1 based on:
   - Depth of knowledge shown in messages
   - Frequency of relevant contributions
   - Quality of explanations and solutions provided
   - Recognition from other users (replies, reactions)
3. Extract key topics each expert discusses
4. Provide a brief analysis of each expert's contributions

Rules:
- Use ONLY these Slack user IDs when populating experts: {available_user_ids}
- If no listed user demonstrates expertise, return an empty experts array
- Do not invent placeholder IDs or users

Return ONLY a valid JSON response with this exact structure (no markdown, no extra text):
{{
    "experts": []
}}"""

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                # Parse the response
                analysis = json.loads(result["response"])
                
                logger.info(f"Ollama analyzed {len(messages)} messages for topic: {topic}")
                return analysis
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling Ollama: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Ollama response: {e}")
            # Return empty result on parse error
            return {"experts": []}
        except Exception as e:
            logger.error(f"Error analyzing expertise: {e}")
            raise
    
    async def analyze_contributors(
        self,
        channel: str,
        messages: List[Dict[str, Any]],
        user_profiles: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze channel contributors and their impact.
        
        Args:
            channel: Channel name
            messages: List of message dictionaries
            user_profiles: Dictionary of user profiles keyed by user_id
            
        Returns:
            Analysis results with contributor rankings
        """
        try:
            context = self._build_message_context(messages, user_profiles)
            available_user_ids = sorted(user_profiles.keys())
            
            prompt = f"""Analyze the following messages from the #{channel} Slack channel to identify key contributors.

Context:
{context}

Task:
1. Identify the most valuable contributors to this channel
2. Score each contributor's engagement from 0 to 1 based on:
   - Message frequency and consistency
   - Quality and helpfulness of contributions
   - Thread participation and responses
   - Community engagement (reactions received, replies generated)
3. Summarize each contributor's main contributions

Rules:
- Use ONLY these Slack user IDs when populating contributors: {available_user_ids}
- If no listed user qualifies, return an empty contributors array
- Do not invent placeholder IDs or users

Return ONLY a valid JSON response with this exact structure (no markdown, no extra text):
{{
    "contributors": []
}}"""

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                # Parse the response
                analysis = json.loads(result["response"])
                
                logger.info(f"Ollama analyzed contributors for channel: {channel}")
                return analysis
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling Ollama: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Ollama response: {e}")
            return {"contributors": []}
        except Exception as e:
            logger.error(f"Error analyzing contributors: {e}")
            raise
    
    async def custom_analysis(
        self,
        query: str,
        messages: List[Dict[str, Any]],
        user_profiles: Dict[str, Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform custom analysis based on user query.
        
        Args:
            query: Natural language query
            messages: List of message dictionaries
            user_profiles: Dictionary of user profiles
            context: Additional context for analysis
            
        Returns:
            Analysis results
        """
        try:
            message_context = self._build_message_context(messages, user_profiles)
            available_user_ids = sorted(user_profiles.keys())
            available_message_ids = [str(msg.get("ts")) for msg in messages if msg.get("ts")]
            explanation_focus = self._query_requests_explanation(query)
            
            additional_context = ""
            if context:
                additional_context = f"\n\nAdditional Context:\n{context}"

            focus_guidance = """
Focus on explaining the content, behavior, or purpose of the code or discussion.
- Answer what the code is doing or what the discussion means.
- Mention people only when needed for context.
- Do not turn the answer into a who-talked-about-it summary unless the query explicitly asks who.
""".strip() if explanation_focus else """
Focus on the main request in the query and support it with evidence from the messages.
""".strip()
            
            prompt = f"""Analyze the following Slack messages to answer this query: "{query}"

Message Context:
{message_context}{additional_context}

Task:
Provide a comprehensive analysis that addresses the query. Include:
1. Key insights relevant to the query
2. Relevant users and their contributions
3. Important messages or threads
4. Any patterns or trends observed

Analysis Focus:
{focus_guidance}

Rules:
- Use ONLY these Slack user IDs when populating relevant_users: {available_user_ids}
- Use ONLY these message IDs when populating key_messages: {available_message_ids[:50]}
- If no provided user ID or message ID applies, return an empty list for that field
- Do not invent placeholder IDs, users, or messages
- In insights, prefer names from the message context and do not mention raw Slack IDs unless they appear in the provided lists

Return ONLY a valid JSON response with this exact structure (no markdown, no extra text):
{{
    "insights": "Detailed analysis and insights",
    "relevant_users": [],
    "key_messages": []
}}"""

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                # Parse the response
                analysis = json.loads(result["response"])
                
                logger.info(f"Ollama performed custom analysis for query: {query}")
                return analysis
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling Ollama: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Ollama response: {e}")
            return {"insights": "Error parsing response", "relevant_users": [], "key_messages": []}
        except Exception as e:
            logger.error(f"Error in custom analysis: {e}")
            raise

    @staticmethod
    def _query_requests_explanation(query: str) -> bool:
        """Return True when the user is asking to understand or explain something."""
        lowered = query.lower()
        return any(hint in lowered for hint in EXPLANATION_HINTS)
    
    async def analyze_topic_discussion(
        self,
        query: str,
        messages: List[Dict[str, Any]],
        user_profiles: Dict[str, Dict[str, Any]]
    ) -> str:
        """
        Analyze who talked about a topic the most and provide natural language answer.
        
        Args:
            query: Topic or keyword to analyze
            messages: List of message dictionaries
            user_profiles: Dictionary of user profiles
            
        Returns:
            Natural language answer about who discussed the topic
        """
        try:
            # Build context with user aggregation
            user_message_counts: Dict[str, int] = {}
            user_messages: Dict[str, List[str]] = {}
            
            for msg in messages:
                user_id = msg.get("user", "unknown")
                if user_id == "unknown":
                    continue
                    
                user_message_counts[user_id] = user_message_counts.get(user_id, 0) + 1
                if user_id not in user_messages:
                    user_messages[user_id] = []
                user_messages[user_id].append(msg.get("text", ""))
            
            # Build context for Ollama
            context_parts = []
            for user_id, count in sorted(user_message_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                user_name = user_profiles.get(user_id, {}).get("real_name") or user_profiles.get(user_id, {}).get("name", user_id)
                sample_messages = user_messages[user_id][:3]  # First 3 messages as examples
                context_parts.append(
                    f"{user_name} ({count} messages): {' | '.join(sample_messages)}"
                )
            
            context = "\n".join(context_parts)
            
            prompt = f"""Based on the following Slack messages about "{query}", provide a natural language answer about who discussed this topic the most.

Message Data:
{context}

Total messages analyzed: {len(messages)}

Task:
Write a natural, conversational answer that:
1. Identifies who talked about "{query}" the most (mention top 2-3 people with their message counts)
2. Briefly describes what aspects they focused on
3. Mentions any interesting patterns or insights

Write the answer as if you're having a conversation. Start with something like "Based on {len(messages)} messages..." and make it informative but friendly.

Return ONLY the natural language answer text (no JSON, no markdown, just the answer):"""

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                answer = result["response"].strip()
                
                logger.info(f"Ollama generated natural language answer for query: {query}")
                return answer
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling Ollama: {e}")
            raise
        except Exception as e:
            logger.error(f"Error analyzing topic discussion: {e}")
            raise
    
    def _build_message_context(
        self,
        messages: List[Dict[str, Any]],
        user_profiles: Dict[str, Dict[str, Any]]
    ) -> str:
        """
        Build formatted context from messages and user profiles.
        
        Args:
            messages: List of message dictionaries
            user_profiles: Dictionary of user profiles
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for msg in messages[:100]:  # Limit to 100 messages to avoid token limits
            user_id = msg.get("user", "unknown")
            user_name = user_profiles.get(user_id, {}).get("real_name", user_id)
            text = msg.get("text", "")
            timestamp = msg.get("ts", "")
            reactions = msg.get("reactions", [])
            reply_count = msg.get("reply_count", 0)
            
            reaction_str = ""
            if reactions:
                reaction_str = f" [Reactions: {', '.join([r.get('name', '') for r in reactions])}]"
            
            reply_str = ""
            if reply_count > 0:
                reply_str = f" [{reply_count} replies]"
            
            context_parts.append(
                f"[{timestamp}] {user_name}: {text}{reaction_str}{reply_str}"
            )
        
        return "\n".join(context_parts)
    
    async def health_check(self) -> bool:
        """
        Check if Ollama is accessible.
        
        Returns:
            True if Ollama is healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False


# Global Ollama client instance
ollama_client = OllamaClient()

# Made with Bob
