"""API route handlers."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
import json
import re
from app.models.schemas import (
    ExpertRequest,
    ExpertResponse,
    ContributorRequest,
    ContributorResponse,
    AnalysisRequest,
    AnalysisResponse,
    SearchRequest,
    SearchResponse,
    HealthResponse,
    ChatRequest,
    ChatResponse,
)
from app.services.analysis_service import analysis_service
from app.services.slack_client import slack_client
from app.services.ollama_client import ollama_client
from app.services.github_mcp_service import github_mcp_service
from app.utils.logger import setup_logger
from app.utils.cache import cache_manager
from chat_with_slack import parse_user_query, execute_tool, format_results
from app import __version__

logger = setup_logger(__name__)
router = APIRouter()
OWNER_REPO_PATTERN = r'([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)'


def message_has_command(message: str, commands: List[str]) -> bool:
    """Return True when a command word or phrase appears outside repo-name substrings."""
    return any(re.search(rf'(?<![A-Za-z0-9_.-]){re.escape(command)}(?![A-Za-z0-9_.-])', message) for command in commands)


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
    min_messages: int = Query(default=1, ge=1),
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
    sort_by: str = Query(default="message_count", pattern="^(message_count|engagement)$")
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


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat-style endpoint that handles both Slack and GitHub queries."""
    try:
        message = request.message.lower()
        
        # Detect if this is a GitHub query
        github_keywords = ['github', 'repo', 'repository', 'commit', 'issue', 'pull request', 'file']
        has_github_keyword = any(keyword in message for keyword in github_keywords)
        
        # Also detect owner/repo patterns (e.g., "facebook/react", "shrutiusonavane/cafe-finder")
        has_owner_repo_pattern = re.search(OWNER_REPO_PATTERN, message) is not None
        
        is_github_query = has_github_keyword or has_owner_repo_pattern
        
        if is_github_query:
            # Handle GitHub MCP query
            response_text = await handle_github_query(request.message)
            return ChatResponse(
                message=request.message,
                tool="github_mcp",
                params={"query": request.message},
                response=response_text,
                timestamp=datetime.now(),
            )
        else:
            # Handle Slack query (original logic)
            tool_call = await parse_user_query(request.message)
            tool_name = tool_call.get("tool")
            params = tool_call.get("params", {})

            if not tool_name:
                raise ValueError("No tool selected for the given message")

            results = await execute_tool(tool_name, params)
            formatted_response = await format_results(tool_name, results, request.message)

            return ChatResponse(
                message=request.message,
                tool=tool_name,
                params=params,
                response=formatted_response,
                timestamp=datetime.now(),
            )

    except Exception as e:
        logger.error(f"Error in chat for message '{request.message}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_github_query(message: str) -> str:
    """
    Handle GitHub-related queries using the GitHub MCP service.
    
    Args:
        message: User's natural language query
        
    Returns:
        Formatted response from GitHub
    """
    message_lower = message.lower()
    
    try:
        # Check for owner/repo pattern first (e.g., "shrutiusonavane/cafe-finder")
        owner_repo_match = re.search(OWNER_REPO_PATTERN, message)
        
        # Search repositories
        if message_has_command(message_lower, ['search', 'find', 'look for']) or (owner_repo_match and message_has_command(message_lower, ['search'])):
            # Extract query terms
            query_terms = re.sub(r'search|repo|repository|for|find|github|about', '', message_lower).strip()
            query = query_terms or 'chatbot'
            
            response = await github_mcp_service.search_repositories(query=query, page=1, per_page=5)
            return format_github_response(response)
        
        # Summarize repo - use comprehensive content scan
        elif message_has_command(message_lower, ['summarize', 'summary']):
            if owner_repo_match:
                owner, repo = owner_repo_match.groups()
                logger.info(f"Comprehensive repo summary for {owner}/{repo}")
                
                # Get comprehensive repo content
                summary_data = await github_mcp_service.get_repo_summary_content(
                    owner=owner,
                    repo=repo,
                    branch='main'
                )
                
                if summary_data.get("error"):
                    return summary_data["error"]
                
                if not summary_data.get("files"):
                    return f"Could not find any readable files in {owner}/{repo}"
                
                # Prepare comprehensive content for Ollama
                files_info = summary_data.get("files", {})
                content_preview = "\n\n---\n\n".join([
                    f"File: {filename}\n{content[:1000]}"  # First 1000 chars of each file
                    for filename, content in list(files_info.items())[:5]  # Top 5 files
                ])
                
                file_names = ", ".join(list(files_info.keys())[:5])
                scope_line = f"Repository scope: based on {file_names}."
                
                # Create detailed prompt for Ollama
                prompt = f"""The user asked for a summary of the GitHub repository '{owner}/{repo}'.

Use only the repository files below:

{content_preview}

Write the answer in the same style as a Slack analysis response:
- Start with one clear conversational paragraph explaining what the project appears to do.
- Add one short paragraph for the most important technologies or features, only when the files support it.
- End with exactly this final line: {scope_line}

Do not use numbered sections.
Do not begin with the repository scope line.
Sound friendly and confident, but stay grounded in the files.
Do not invent setup commands, dependencies, features, or technologies that are not visible in the files.
Keep it under 180 words."""
                
                logger.debug(f"Sending comprehensive repo summary to Ollama for {owner}/{repo}")
                response = await enhance_with_ollama(content_preview, f"comprehensive GitHub repository {owner}/{repo}", prompt=prompt)
                return normalize_github_summary_response(response, scope_line) if response else "Unable to generate summary"
            else:
                return "Please specify a repository in format: owner/repo"
        
        # Get file contents - priority pattern: owner/repo/filepath or owner/repo
        elif owner_repo_match or any(kw in message_lower for kw in ['read', 'show', 'get', 'view', 'display', 'file', 'contents', 'about']):
            match = re.search(rf'{OWNER_REPO_PATTERN}(?:/(.+?))?(?:\s|$)', message)
            if match:
                owner, repo, filepath = match.groups()
                filepath = filepath or 'README.md'
                
                response = await github_mcp_service.get_file_contents(
                    owner=owner,
                    repo=repo,
                    path=filepath.strip(),
                    branch='main'
                )
                formatted = format_github_response(response)
                
                # Enhance with context about the file
                if formatted and not formatted.startswith("Error"):
                    enhanced = await enhance_with_ollama(
                        formatted, 
                        f"{filepath} from {owner}/{repo}"
                    )
                    return enhanced if enhanced else formatted
                
                return formatted
            elif owner_repo_match:
                # If we just have owner/repo pattern without file path, treat as repo info request
                owner, repo = owner_repo_match.groups()
                logger.info(f"Fetching README for {owner}/{repo}")
                
                response = await github_mcp_service.get_file_contents(
                    owner=owner,
                    repo=repo,
                    path='README.md',
                    branch='main'
                )
                formatted = format_github_response(response)
                
                # Use Ollama to create a nice summary
                if formatted and not formatted.startswith("Error"):
                    enhanced = await enhance_with_ollama(formatted, f"GitHub repository {owner}/{repo}")
                    return enhanced if enhanced else formatted
                
                return formatted
            else:
                return "Please specify the repository in format: owner/repo/filepath"
        
        # List commits
        elif 'commit' in message_lower:
            match = re.search(OWNER_REPO_PATTERN, message)
            if match:
                owner, repo = match.groups()
                response = await github_mcp_service.list_commits(owner=owner, repo=repo, page=1, per_page=5)
                formatted = format_github_response(response)
                
                # Enhance commit list with Ollama
                if formatted and not formatted.startswith("Error"):
                    enhanced = await enhance_with_ollama(formatted, f"commits from {owner}/{repo}")
                    return enhanced if enhanced else formatted
                
                return formatted
            else:
                return "Please specify the repository in format: owner/repo"
        
        # List issues
        elif 'issue' in message_lower or 'pr' in message_lower or 'pull request' in message_lower:
            match = re.search(OWNER_REPO_PATTERN, message)
            if match:
                owner, repo = match.groups()
                response = await github_mcp_service.list_issues(
                    owner=owner,
                    repo=repo,
                    state='open',
                    page=1,
                    per_page=5
                )
                formatted = format_github_response(response)
                
                # Enhance issues list with Ollama
                if formatted and not formatted.startswith("Error"):
                    enhanced = await enhance_with_ollama(formatted, f"issues from {owner}/{repo}")
                    return enhanced if enhanced else formatted
                
                return formatted
            else:
                return "Please specify the repository in format: owner/repo"
        
        # Help
        elif any(kw in message_lower for kw in ['help', 'what can you do']):
            return """I can help you with GitHub! Try asking me:

🔍 "Search for chatbot repositories"
📄 "Show me facebook/react/README.md"
📝 "List commits from owner/repo"
🐛 "Show issues in owner/repo"
📋 "Summarize owner/repo" (scans entire repo!)

Just ask naturally and I'll help you explore GitHub!"""
        
        # Default - if we have an owner/repo pattern, do comprehensive summary
        elif owner_repo_match:
            owner, repo = owner_repo_match.groups()
            logger.info(f"Default: comprehensive summary for {owner}/{repo}")
            
            summary_data = await github_mcp_service.get_repo_summary_content(
                owner=owner,
                repo=repo,
                branch='main'
            )
            
            if summary_data.get("error") or not summary_data.get("files"):
                # Fallback to README
                response = await github_mcp_service.get_file_contents(
                    owner=owner,
                    repo=repo,
                    path='README.md',
                    branch='main'
                )
                formatted = format_github_response(response)
                enhanced = await enhance_with_ollama(formatted, f"GitHub repository {owner}/{repo}")
                return enhanced if enhanced else formatted
            
            # Use comprehensive data
            files_info = summary_data.get("files", {})
            content_preview = "\n\n---\n\n".join([
                f"File: {filename}\n{content[:1000]}"
                for filename, content in list(files_info.items())[:5]
            ])
            
            enhanced = await enhance_with_ollama(content_preview, f"GitHub repository {owner}/{repo}")
            return enhanced if enhanced else content_preview
        
        else:
            return """I'm connected to GitHub! I can help you:

🔍 Search repositories
📄 Read files from repos
📝 List commits
🐛 View issues
📋 Summarize entire repos

Try: "Search for AI repositories" or "Summarize facebook/react\""""
    
    except Exception as e:
        logger.error(f"Error handling GitHub query: {e}")
        return f"Error: Unable to process GitHub query - {str(e)}"


def format_github_response(mcp_response: dict) -> str:
    """Format GitHub MCP response for display with LLM enhancement."""
    try:
        # Handle errors
        if "error" in mcp_response:
            error_msg = mcp_response.get('error', {})
            if isinstance(error_msg, dict):
                return f"Error: {error_msg.get('message', 'Unknown error')}"
            return f"Error: {error_msg}"
        
        # Extract content from result
        if "result" in mcp_response:
            result = mcp_response["result"]
            
            # Check if it has content (like file contents)
            if "content" in result and isinstance(result["content"], list):
                content_list = result["content"]
                if content_list and len(content_list) > 0:
                    content_item = content_list[0]
                    
                    # Handle text content
                    if isinstance(content_item, dict) and "text" in content_item:
                        text_content = content_item["text"]
                        if text_content and text_content.strip():
                            try:
                                parsed_content = json.loads(text_content)
                            except json.JSONDecodeError:
                                return text_content

                            if isinstance(parsed_content, dict):
                                return format_github_json_payload(parsed_content)
                            return text_content
        
        # If it's a direct text response
        if isinstance(mcp_response, dict):
            if "text" in mcp_response and mcp_response["text"]:
                return mcp_response["text"]
            
            formatted_payload = format_github_json_payload(mcp_response)
            if formatted_payload:
                return formatted_payload
        
        return "No content found in GitHub response"
    
    except Exception as e:
        logger.error(f"Error formatting GitHub response: {e}")
        return f"Could not format GitHub response: {str(e)}"


def format_github_json_payload(payload: dict) -> str:
    """Format common GitHub API JSON payloads for chat display."""
    if "items" in payload:
        items = payload.get("items") or []
        total_count = payload.get("total_count", len(items))
        if not items:
            return "I could not find any matching GitHub repositories."

        lines = [f"Found {total_count} matching repositories. Top results:"]
        for index, item in enumerate(items[:5], start=1):
            if not isinstance(item, dict):
                continue
            full_name = item.get("full_name") or item.get("name") or "Unknown repository"
            description = item.get("description") or "No description provided"
            html_url = item.get("html_url")
            stars = item.get("stargazers_count")
            metadata = f" ({stars} stars)" if stars is not None else ""
            url_text = f" - {html_url}" if html_url else ""
            lines.append(f"{index}. {full_name}{metadata}: {description}{url_text}")
        return "\n".join(lines)

    if payload.get("type") == "file" and payload.get("content"):
        return github_mcp_service.extract_file_text({"result": {"content": [{"text": json.dumps(payload)}]}})

    return json.dumps(payload, indent=2) if payload else ""


def normalize_github_summary_response(response: str, scope_line: str) -> str:
    """Keep GitHub summaries in the same answer-then-scope shape as Slack results."""
    cleaned = (response or "").strip()
    if not cleaned:
        return cleaned

    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    body_lines = [
        line for line in lines
        if not line.lower().startswith("repository scope:")
    ]

    if not body_lines:
        return scope_line

    return "\n\n".join(["\n".join(body_lines), scope_line])


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


async def enhance_with_ollama(content: str, context: str, prompt: Optional[str] = None) -> str:
    """
    Use Ollama LLM to format/enhance and summarize GitHub content.
    
    Args:
        content: The raw GitHub content to enhance
        context: Context about what the content is
        
    Returns:
        Enhanced, human-readable response
    """
    try:
        if not content or len(content.strip()) < 10:
            return content
        
        if prompt is None:
            # If content looks like raw JSON, try to summarize it
            if content.startswith('{'):
                prompt = (
                    "Summarize this GitHub API response in the same style as a Slack analysis answer: "
                    "one concise conversational paragraph, then one short scope/detail line if useful. "
                    f"Response:\n\n{content[:800]}"
                )
            else:
                # For file content, create a nice summary
                prompt = (
                    f"The user is looking at {context}. Write a clear, concise answer in the same style as a Slack analysis response: "
                    "one conversational paragraph with the key takeaway, followed by one short detail line if helpful. "
                    "Do not use numbered sections, and do not invent details that are not in the content.\n\n"
                    f"{content[:2000]}"
                )
        
        logger.debug(f"Sending to Ollama: {prompt[:100]}...")
        response = await ollama_client.ask(prompt)
        
        if response and response.strip():
            return response
        return content
    except Exception as e:
        logger.warning(f"Could not enhance with Ollama ({e}), returning raw content")
        return content

# Made with Bob
