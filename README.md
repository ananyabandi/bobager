# Bobager - Integrated Slack + GitHub AI Chat Tool

A powerful chat interface that combines **Slack workspace intelligence** with **GitHub repository insights** powered by AI and the Model Context Protocol (MCP).

## Features

### 🎯 Slack Intelligence
- **Find Experts**: Identify team members with expertise in specific technologies
- **Discover Contributors**: Locate key contributors in channels
- **Custom Analysis**: Analyze conversations with natural language queries
- **Ollama Integration**: Uses local LLM for intelligent analysis

### 🔗 GitHub Intelligence  
- **Repository Search**: Find and explore GitHub repositories
- **File Exploration**: Read and view file contents from repositories
- **Commit History**: Browse commit history and details
- **Issue Tracking**: View open issues and pull requests
- **GitHub MCP**: Uses the Model Context Protocol for reliable GitHub access

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+ (for GitHub MCP server)
- Slack API credentials (for Slack features)
- GitHub Personal Access Token (for GitHub features)

### Installation

1. **Clone and Setup Python Environment**
```bash
cd bobager
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Install Node.js Dependencies for GitHub MCP**
```bash
npm install  # or npm run install-mcp
```

3. **Configure Environment Variables**
```bash
cp .env.example .env
```

Edit `.env` with:
```
SLACK_BOT_TOKEN=xoxb-your-slack-token
SLACK_SIGNING_SECRET=your-signing-secret
GITHUB_PERSONAL_ACCESS_TOKEN=ghp-your-github-token
OLLAMA_BASE_URL=http://localhost:11434
```

### Running the Application

1. **Start the Backend Server**
```bash
python -m uvicorn app.main:app --reload --port 8000
```

2. **Open in Browser**
```
http://localhost:8000
```

## Chat Examples

### Slack Queries
- "Who can help me with React?"
- "Who's discussed DevOps the most this month?"
- "Find me code snippets about Python in #general"
- "Who are the top contributors in #backend?"

### GitHub Queries
- "Search for machine learning repositories"
- "Show me facebook/react/README.md"
- "List commits from owner/repo"
- "Show open issues in owner/repo"

## Architecture

### Backend (Python/FastAPI)
- **app/services/slack_client.py** - Slack API integration
- **app/services/github_mcp_service.py** - GitHub MCP server wrapper
- **app/services/ollama_client.py** - Local LLM integration
- **app/services/analysis_service.py** - Slack analysis engine
- **app/api/routes.py** - API endpoints

### Frontend (HTML/CSS/JavaScript)
- **index.html** - Chat interface
- **app.js** - Chat logic and API communication
- **styles.css** - UI styling

## API Endpoints

### Slack Endpoints
- `POST /api/v1/chat` - Chat interface (routes to Slack or GitHub)
- `GET /api/v1/experts/{topic}` - Find experts
- `GET /api/v1/contributors/{channel}` - Find contributors
- `POST /api/v1/analyze` - Custom analysis
- `POST /api/v1/search` - Search and analyze

### GitHub Endpoints
- Integrated into `/api/v1/chat` endpoint
- Automatically detected based on query keywords

### Health & Utility
- `GET /health` - Health check
- `GET /cache/stats` - Cache statistics
- `POST /cache/clear` - Clear cache

## Integration Notes

This integration combines:
- **David's Branch**: Python FastAPI backend with Slack integration
- **Shruti's Branch**: GitHub MCP server integration

### How It Works
1. User sends a message to the chat interface
2. The backend analyzes the message for keywords
3. For Slack queries: Routes to Slack analysis service + Ollama LLM
4. For GitHub queries: Routes to GitHub MCP server
5. Formatted response returned to the user

## Troubleshooting

### Backend Won't Connect
- Ensure port 8000 is available
- Check that all environment variables are set
- Verify Python virtual environment is activated

### GitHub MCP Not Working
- Ensure `@modelcontextprotocol/server-github` is installed: `npm install`
- Check GITHUB_PERSONAL_ACCESS_TOKEN is set correctly
- Verify token has appropriate scopes (public_repo, read:user, etc.)

### Slack Integration Issues
- Verify Slack tokens are valid and have correct scopes
- Check that bot is added to channels
- Review logs in `app/utils/logger.py`

## Environment Variables

```env
# Slack
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...

# GitHub
GITHUB_PERSONAL_ACCESS_TOKEN=ghp-...

# Ollama (Local LLM)
OLLAMA_BASE_URL=http://localhost:11434

# Optional
LOG_LEVEL=INFO
CACHE_TTL=3600
```

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Checking Code Quality
```bash
# Format
black app/

# Lint
pylint app/
```

## Files Modified During Integration

From David's Branch:
- `app/` - Complete Python backend structure
- `requirements.txt` - Python dependencies
- `index.html`, `app.js`, `styles.css` - Frontend
- `chat_with_slack.py` - Slack chat utility

From Shruti's Branch:
- GitHub MCP server logic (integrated into `app/services/github_mcp_service.py`)
- Documentation for GitHub MCP setup

## Made with 🤍 by the Bobager Team

---

For detailed setup instructions, see:
- [QUICKSTART.md](QUICKSTART.md) - Get started quickly
- [SETUP_MACOS.md](SETUP_MACOS.md) - macOS specific setup
- [GITHUB_MCP_SETUP.md](GITHUB_MCP_SETUP.md) - GitHub MCP configuration
- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - Integration details