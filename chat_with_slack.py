#!/usr/bin/env python3
"""
Natural Language Interface to Slack Analysis
Uses Ollama to understand queries and orchestrate MCP tool calls
"""
import asyncio
import json
import httpx
from typing import Dict, Any
from app.services.analysis_service import analysis_service
from app.models.schemas import AnalysisResponse, UserProfile
from app.config.settings import settings
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
)

PEOPLE_HINTS = (
    "who",
    "whom",
    "who can",
    "who should",
    "person",
    "people",
    "expert",
    "experts",
    "ask",
    "go to",
)

# System prompt to teach Ollama how to use our tools
SYSTEM_PROMPT = """You are a helpful assistant that can analyze Slack workspace data.

You have access to these tools:

1. find_experts(topic: str, timeframe_days: int = 30, min_messages: int = 1, channels: list = None)
   - Finds subject matter experts on a specific TECHNOLOGY or SKILL
   - Use when: User asks about experts, specialists, or who knows about a technology
   - Example: "Find Python experts" → {"tool": "find_experts", "params": {"topic": "Python"}}
   - Example: "Who knows React?" → {"tool": "find_experts", "params": {"topic": "React"}}
    - For broad questions like "who can help with HTML?", leave min_messages unset so the default stays inclusive

2. find_contributors(channel: str, timeframe_days: int = 30, limit: int = 10, sort_by: str = "message_count")
   - Finds top contributors in a SPECIFIC CHANNEL (like #engineering, #backend)
   - Use when: User mentions a channel name or asks about activity in a channel
   - Example: "Top contributors in engineering" → {"tool": "find_contributors", "params": {"channel": "engineering"}}
   - Example: "Most active in #backend" → {"tool": "find_contributors", "params": {"channel": "backend"}}

3. custom_analysis(query: str, channels: list = None, timeframe_days: int = 30)
   - Performs custom analysis for ANY OTHER QUESTION
   - Use when: User asks about discussions, topics, opinions, or anything not fitting above
   - Example: "What are people saying about APIs?" → {"tool": "custom_analysis", "params": {"query": "What are people saying about APIs?"}}
   - Example: "Who talked about pizza?" → {"tool": "custom_analysis", "params": {"query": "Who talked about pizza the most?"}}
   - Example: "Discussions about security" → {"tool": "custom_analysis", "params": {"query": "Discussions about security"}}

IMPORTANT RULES:
- If the question is about a TOPIC/SUBJECT (not a channel), use custom_analysis
- If the question mentions a CHANNEL NAME (like #engineering), use find_contributors
- If the question is about EXPERTISE in a technology, use find_experts
- When in doubt, use custom_analysis - it's the most flexible

When the user asks a question:
1. Determine which tool to use based on the rules above
2. Extract the parameters from their question
3. Respond with ONLY a JSON object in this format:
   {"tool": "tool_name", "params": {"param1": "value1", "param2": "value2"}}

Do not include any other text, just the JSON.

Examples:
User: "Find Python experts from the last 60 days"
You: {"tool": "find_experts", "params": {"topic": "Python", "timeframe_days": 60}}

User: "Who are the top 5 contributors in the backend channel?"
You: {"tool": "find_contributors", "params": {"channel": "backend", "limit": 5}}

User: "What are people discussing about microservices?"
You: {"tool": "custom_analysis", "params": {"query": "What are people discussing about microservices?"}}

User: "Who talked about pizza the most?"
You: {"tool": "custom_analysis", "params": {"query": "Who talked about pizza the most?"}}

User: "Find discussions about deployment"
You: {"tool": "custom_analysis", "params": {"query": "Find discussions about deployment"}}
"""


async def call_ollama(prompt: str, system: str = "", temperature: float = 0.7) -> str:
    """
    Call Ollama API directly.
    
    Args:
        prompt: The prompt to send
        system: System prompt (optional)
        temperature: Temperature for generation
        
    Returns:
        Generated text response
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{settings.ollama_base_url}/api/generate",
            json={
                "model": settings.ollama_model,
                "prompt": prompt,
                "system": system,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            }
        )
        response.raise_for_status()
        result = response.json()
        return result["response"]


async def parse_user_query(query: str) -> Dict[str, Any]:
    """
    Use Ollama to parse natural language query into tool call.
    
    Args:
        query: Natural language query from user
        
    Returns:
        Dictionary with 'tool' and 'params' keys
    """
    response = ""
    try:
        # Ask Ollama to convert natural language to tool call
        response = await call_ollama(
            prompt=f"User query: {query}",
            system=SYSTEM_PROMPT,
            temperature=0.1  # Low temperature for consistent parsing
        )
        
        # Parse the JSON response
        tool_call = json.loads(response.strip())
        tool_call = _normalize_tool_call(query, tool_call)
        return tool_call
    
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Ollama response as JSON: {response}")
        raise ValueError(f"Could not understand the query. Please try rephrasing.")
    except Exception as e:
        logger.error(f"Error parsing query: {e}")
        raise


async def execute_tool(tool_name: str, params: Dict[str, Any]) -> Any:
    """
    Execute the specified tool with given parameters.
    
    Args:
        tool_name: Name of the tool to execute
        params: Parameters for the tool
        
    Returns:
        Tool execution result
    """
    if tool_name == "find_experts":
        return await analysis_service.find_experts(**params)
    
    elif tool_name == "find_contributors":
        return await analysis_service.find_contributors(**params)
    
    elif tool_name == "custom_analysis":
        return await analysis_service.custom_analysis(**params)
    
    else:
        raise ValueError(f"Unknown tool: {tool_name}")


def _query_requests_explanation(query: str) -> bool:
    """Return True when the user is asking to understand or explain something."""
    lowered = query.lower()
    return any(hint in lowered for hint in EXPLANATION_HINTS)


def _query_requests_people(query: str) -> bool:
    """Return True when the user is explicitly asking about people."""
    lowered = query.lower()
    return any(hint in lowered for hint in PEOPLE_HINTS)


def _normalize_tool_call(original_query: str, tool_call: Dict[str, Any]) -> Dict[str, Any]:
    """Preserve user intent when the parser over-compresses a custom analysis query."""
    if tool_call.get("tool") != "custom_analysis":
        return tool_call

    params = tool_call.setdefault("params", {})
    parsed_query = params.get("query")

    if _query_requests_explanation(original_query):
        params["query"] = original_query.strip()
        return tool_call

    if not isinstance(parsed_query, str) or not parsed_query.strip():
        params["query"] = original_query.strip()

    return tool_call


def _format_user_label(user: UserProfile) -> str:
    """Build a readable label for a Slack user."""
    if user.real_name and user.username and user.real_name != user.username:
        return f"{user.real_name} (@{user.username})"
    if user.real_name:
        return user.real_name
    if user.username:
        return f"@{user.username}"
    return user.user_id


def _format_custom_analysis_results(results: AnalysisResponse) -> str:
    """Format custom analysis deterministically from validated fields."""
    sections = [results.insights.strip() or "No clear insights were returned."]

    if results.relevant_users and _query_requests_people(results.query):
        user_labels = ", ".join(_format_user_label(user) for user in results.relevant_users)
        sections.append(f"Relevant people: {user_labels}.")

    total_messages = results.metadata.get("total_messages_analyzed")
    timeframe_days = results.metadata.get("timeframe_days")
    channels = results.metadata.get("channels_searched")
    scope_parts = []

    if isinstance(total_messages, int):
        scope_parts.append(f"based on {total_messages} matching messages")
    if isinstance(timeframe_days, int):
        scope_parts.append(f"over the last {timeframe_days} days")
    if channels:
        if isinstance(channels, list):
            scope_parts.append(f"across channels: {', '.join(channels)}")
        else:
            scope_parts.append(f"across {channels} channels")

    if scope_parts:
        sections.append("Analysis scope: " + ", ".join(scope_parts) + ".")

    return "\n\n".join(sections)


async def format_results(tool_name: str, results: Any, original_query: str) -> str:
    """
    Use Ollama to format results in a human-friendly way.
    
    Args:
        tool_name: Name of the tool that was executed
        results: Raw results from the tool
        original_query: Original user query
        
    Returns:
        Human-friendly formatted response
    """
    if tool_name == "custom_analysis" and isinstance(results, AnalysisResponse):
        return _format_custom_analysis_results(results)

    # Convert results to JSON string
    if hasattr(results, 'model_dump'):
        results_json = json.dumps(results.model_dump(), indent=2, default=str)
    else:
        results_json = json.dumps(results, indent=2, default=str)
    
    # Ask Ollama to format the results nicely
    format_prompt = f"""The user asked: "{original_query}"

We executed the {tool_name} tool and got these results:

{results_json}

Please provide a clear, concise summary of these results in a conversational way.
Focus on the most important information and make it easy to understand.
"""
    
    response = await call_ollama(
        prompt=format_prompt,
        temperature=0.7
    )
    
    return response


async def chat_loop():
    """Main chat loop for natural language interaction."""
    print("=" * 60)
    print("🤖 Slack Analysis Chat")
    print("=" * 60)
    print("\nAsk me anything about your Slack workspace!")
    print("\nExamples:")
    print("  • Find Python experts from the last 30 days")
    print("  • Who are the top contributors in #engineering?")
    print("  • What are people saying about microservices?")
    print("\nType 'quit' or 'exit' to stop.\n")
    print("=" * 60)
    
    while True:
        try:
            # Get user input
            query = input("\n💬 You: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            print("\n🤔 Thinking...")
            
            # Step 1: Parse query into tool call using Ollama
            tool_call = await parse_user_query(query)
            tool_name = tool_call.get('tool')
            params = tool_call.get('params', {})
            
            # Validate tool_name
            if not tool_name:
                raise ValueError("No tool specified in the parsed query")
            
            print(f"🔧 Using tool: {tool_name}")
            print(f"📋 Parameters: {json.dumps(params, indent=2)}")
            
            # Step 2: Execute the tool
            print("\n⚙️  Executing...")
            results = await execute_tool(tool_name, params)
            
            # Step 3: Format results using Ollama
            print("\n📊 Analyzing results...")
            formatted_response = await format_results(tool_name, results, query)
            
            # Step 4: Display to user
            print(f"\n🤖 Assistant:\n{formatted_response}")
            print("\n" + "-" * 60)
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try rephrasing your question.")


async def main():
    """Entry point."""
    try:
        await chat_loop()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Fatal error: {e}")


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob