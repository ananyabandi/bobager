"""GitHub MCP (Model Context Protocol) Service for querying GitHub data."""
import asyncio
import base64
import json
import logging
from typing import Any, Dict, Optional, List
from subprocess import Popen, PIPE
import os

from app.config import settings

logger = logging.getLogger(__name__)


class GitHubMCPService:
    """Service for interacting with GitHub via Model Context Protocol."""
    
    def __init__(self):
        """Initialize the GitHub MCP Service."""
        self.github_token = settings.github_personal_access_token or ""
        
    async def call_mcp(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Call the GitHub MCP server with a method and optional parameters.
        
        Args:
            method: The MCP method name (e.g., 'tools/call')
            params: Optional parameters for the method
            
        Returns:
            The MCP response as a dictionary
        """
        return await asyncio.to_thread(self._call_mcp_sync, method, params)
    
    def _call_mcp_sync(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Synchronous wrapper for calling MCP server."""
        try:
            # Check if token is available
            if not self.github_token or self.github_token.strip() == "":
                logger.error("GitHub token is not configured!")
                return {"error": {"message": "GitHub token not configured. Please set GITHUB_PERSONAL_ACCESS_TOKEN in .env"}}
            
            # Create a fresh MCP process for each request
            env = os.environ.copy()
            env["GITHUB_PERSONAL_ACCESS_TOKEN"] = self.github_token
            
            logger.debug(f"Spawning MCP server with token (length: {len(self.github_token)})")
            
            process = Popen(
                ["npx", "-y", "@modelcontextprotocol/server-github"],
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
                env=env,
                text=True
            )
            
            # Build the JSON-RPC request
            request = {
                "jsonrpc": "2.0",
                "method": method,
                "id": 1
            }
            
            if params:
                request["params"] = params
            
            logger.debug(f"Sending MCP request: {request}")
            
            # Send request and get response
            stdout, stderr = process.communicate(
                input=json.dumps(request) + "\n",
                timeout=30
            )
            
            if stderr:
                logger.warning(f"MCP stderr: {stderr}")
            
            logger.debug(f"MCP stdout: {stdout[:500]}")  # Log first 500 chars
            
            # Parse response
            if stdout:
                for line in stdout.strip().split("\n"):
                    if line.strip():
                        try:
                            response = json.loads(line)
                            if "id" in response and response["id"] == 1:
                                return response
                        except json.JSONDecodeError:
                            continue
            
            return {"error": {"message": "No valid response from MCP server"}}
            
        except asyncio.TimeoutError:
            return {"error": "MCP request timeout"}
        except Exception as e:
            logger.error(f"MCP call failed: {e}")
            return {"error": str(e)}
    
    async def search_repositories(self, query: str, page: int = 1, per_page: int = 5) -> Dict[str, Any]:
        """
        Search for repositories on GitHub.
        
        Args:
            query: Search query
            page: Page number (default 1)
            per_page: Results per page (default 5)
            
        Returns:
            Search results from GitHub MCP
        """
        return await self.call_mcp(
            "tools/call",
            {
                "name": "search_repositories",
                "arguments": {
                    "query": query or "chatbot",
                    "page": page,
                    "perPage": per_page
                }
            }
        )
    
    async def get_file_contents(
        self,
        owner: str,
        repo: str,
        path: str = "README.md",
        branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Get file contents from a GitHub repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: File path (default README.md)
            branch: Branch name (default main)
            
        Returns:
            File contents from GitHub MCP
        """
        return await self.call_mcp(
            "tools/call",
            {
                "name": "get_file_contents",
                "arguments": {
                    "owner": owner,
                    "repo": repo,
                    "path": path,
                    "branch": branch
                }
            }
        )
    
    async def list_commits(
        self,
        owner: str,
        repo: str,
        page: int = 1,
        per_page: int = 5
    ) -> Dict[str, Any]:
        """
        List commits from a GitHub repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            page: Page number (default 1)
            per_page: Results per page (default 5)
            
        Returns:
            Commits from GitHub MCP
        """
        return await self.call_mcp(
            "tools/call",
            {
                "name": "list_commits",
                "arguments": {
                    "owner": owner,
                    "repo": repo,
                    "page": page,
                    "perPage": per_page
                }
            }
        )
    
    async def list_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        page: int = 1,
        per_page: int = 5
    ) -> Dict[str, Any]:
        """
        List issues from a GitHub repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state ('open', 'closed', 'all')
            page: Page number (default 1)
            per_page: Results per page (default 5)
            
        Returns:
            Issues from GitHub MCP
        """
        return await self.call_mcp(
            "tools/call",
            {
                "name": "list_issues",
                "arguments": {
                    "owner": owner,
                    "repo": repo,
                    "state": state,
                    "page": page,
                    "per_page": per_page
                }
            }
        )
    
    async def get_repo_summary_content(
        self,
        owner: str,
        repo: str,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Get comprehensive repo summary by fetching key files.
        
        Intelligently fetches README, package.json, setup.py, and other 
        important files to provide Ollama with full context about the repo.
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name (default main)
            
        Returns:
            Dictionary with aggregated content from key files
        """
        key_files = [
            "README.md",
            "README",
            "package.json",
            "setup.py",
            "pyproject.toml",
            "requirements.txt",
            "Dockerfile",
            ".github/workflows/main.yml",
            "src/index.ts",
            "src/index.js",
            "src/main.py",
            "src/App.tsx",
            "src/App.jsx",
            "index.html",
            "index.ts",
            "index.js",
            "script.js",
            "app.js",
            "styles.css",
            "style.css",
            "main.py",
        ]
        
        summary_content = {
            "repo": f"{owner}/{repo}",
            "files": {},
            "error": None,
            "last_error": None
        }
        
        # Try to fetch each key file
        for file_path in key_files:
            for candidate_branch in dict.fromkeys([branch, "master"]):
                try:
                    file_response = await self.get_file_contents(
                        owner=owner,
                        repo=repo,
                        path=file_path,
                        branch=candidate_branch
                    )
                    error_message = self.extract_error_message(file_response)
                    if error_message:
                        summary_content["last_error"] = error_message
                        continue

                    file_content = self.extract_file_text(file_response)
                    if file_content:
                        summary_content["files"][file_path] = file_content
                        # We got the README, stop looking for alternatives
                        if file_path in ["README.md", "README"]:
                            return summary_content
                        if len(summary_content["files"]) >= 5:
                            return summary_content
                        break
                except Exception as e:
                    # File might not exist, continue to next
                    logger.debug(f"Could not fetch {file_path}: {str(e)}")
                    continue

        root_listing = await self.get_root_listing(owner=owner, repo=repo, branch=branch)
        if root_listing.get("content"):
            summary_content["files"]["Repository root listing"] = root_listing["content"]
            summary_content["error"] = None
            return summary_content

        if root_listing.get("error"):
            summary_content["last_error"] = root_listing["error"]
        
        if not summary_content["files"]:
            summary_content["error"] = (
                f"Could not fetch files from {owner}/{repo}: {summary_content['last_error']}"
                if summary_content.get("last_error")
                else f"Could not fetch files from {owner}/{repo}"
            )
        
        return summary_content

    async def get_root_listing(self, owner: str, repo: str, branch: str = "main") -> Dict[str, Optional[str]]:
        """Fetch a lightweight root directory listing as a summary fallback."""
        for candidate_branch in dict.fromkeys([branch, "master"]):
            response = await self.get_file_contents(
                owner=owner,
                repo=repo,
                path="",
                branch=candidate_branch
            )
            error_message = self.extract_error_message(response)
            if error_message:
                continue

            text_content = self.extract_text_content(response)
            if not text_content:
                continue

            try:
                payload = json.loads(text_content)
            except json.JSONDecodeError:
                return {"content": text_content, "error": None}

            if isinstance(payload, list):
                entries = []
                for item in payload[:40]:
                    if not isinstance(item, dict):
                        continue
                    item_type = item.get("type", "item")
                    name = item.get("name") or item.get("path") or "unnamed"
                    entries.append(f"- {item_type}: {name}")
                if entries:
                    return {
                        "content": "Root repository files and directories:\n" + "\n".join(entries),
                        "error": None
                    }

        return {"content": None, "error": "Unable to read repository root directory"}

    @staticmethod
    def extract_error_message(mcp_response: Dict[str, Any]) -> Optional[str]:
        """Extract a useful error message from an MCP response."""
        error = mcp_response.get("error")
        if isinstance(error, dict):
            return error.get("message") or json.dumps(error)
        if error:
            return str(error)
        return None

    @staticmethod
    def extract_text_content(mcp_response: Dict[str, Any]) -> str:
        """Extract the text payload from a GitHub MCP response."""
        result = mcp_response.get("result", {})
        content_list = result.get("content", [])
        if not isinstance(content_list, list) or not content_list:
            return ""

        first_content = content_list[0]
        if isinstance(first_content, dict):
            return first_content.get("text", "") or ""
        if isinstance(first_content, str):
            return first_content
        return ""

    @classmethod
    def extract_file_text(cls, mcp_response: Dict[str, Any]) -> str:
        """Extract readable file text from raw or JSON-wrapped MCP content."""
        text_content = cls.extract_text_content(mcp_response)
        if not text_content.strip():
            return ""

        try:
            payload = json.loads(text_content)
        except json.JSONDecodeError:
            return text_content

        if not isinstance(payload, dict):
            return text_content

        file_content = payload.get("content")
        if not isinstance(file_content, str) or not file_content:
            return text_content

        if payload.get("encoding") == "base64":
            try:
                return base64.b64decode(file_content).decode("utf-8", errors="replace")
            except Exception:
                logger.debug("Could not decode base64 file content", exc_info=True)
                return ""

        return file_content
    
    def _format_response(self, mcp_response: Dict[str, Any]) -> str:
        """Format MCP response for display."""
        if "error" in mcp_response:
            return f"Error: {mcp_response['error']['message']}"
        
        if "result" in mcp_response:
            content = mcp_response.get("result", {}).get("content", [])
            if content and isinstance(content, list):
                return content[0].get("text", "No content found")
        
        return "No response from GitHub"


# Create singleton instance
github_mcp_service = GitHubMCPService()
