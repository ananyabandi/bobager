# Bobager

Slack MCP + Bob LLM Integration API for analyzing chat history, identifying experts, and finding key contributors.

## Features

- 🔍 **Find Experts**: Identify subject matter experts on specific technologies or topics
- 👥 **Analyze Contributors**: Discover key contributors in channels
- 🤖 **Custom Analysis**: Perform flexible analysis with natural language queries
- ⚡ **Caching**: Built-in caching for improved performance
- 📊 **Rich Insights**: Powered by Bob LLM for intelligent analysis

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Client    │─────▶│  FastAPI     │─────▶│  Slack MCP  │
│  (Frontend) │      │   Server     │      │   Server    │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   Bob LLM    │
                     │     API      │
                     └──────────────┘
```

## Prerequisites

- Python 3.11+
- Slack MCP server running locally
- Bob API access
- Docker (optional, for containerized deployment)

## Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bobager
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **View logs**
   ```bash
   docker-compose logs -f
   ```

3. **Stop the service**
   ```bash
   docker-compose down
   ```

## Configuration

Edit `.env` file with your settings:

```env
# Slack MCP Server Configuration
SLACK_MCP_HOST=localhost
SLACK_MCP_PORT=3000
SLACK_MCP_TRANSPORT=stdio

# Bob API Configuration
BOB_API_URL=http://localhost:8080/api
BOB_API_KEY=your_bob_api_key_here

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True

# Cache Configuration
CACHE_TTL=3600
CACHE_MAX_SIZE=1000

# Logging
LOG_LEVEL=INFO
```

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check
```http
GET /api/v1/health
```

### Find Experts
```http
GET /api/v1/experts/{topic}?timeframe_days=30&min_messages=5&channels=engineering,backend

POST /api/v1/experts
Content-Type: application/json

{
  "topic": "React",
  "timeframe_days": 30,
  "min_messages": 5,
  "channels": ["engineering", "frontend"]
}
```

### Find Contributors
```http
GET /api/v1/contributors/{channel}?timeframe_days=30&limit=10&sort_by=engagement

POST /api/v1/contributors
Content-Type: application/json

{
  "channel": "engineering",
  "timeframe_days": 30,
  "limit": 10,
  "sort_by": "message_count"
}
```

### Custom Analysis
```http
POST /api/v1/analyze
Content-Type: application/json

{
  "query": "Who are the experts in database optimization?",
  "channels": ["engineering", "backend"],
  "timeframe_days": 90,
  "context": {
    "project": "database-migration"
  }
}
```

### Cache Management
```http
GET /api/v1/cache/stats
POST /api/v1/cache/clear
```

## Usage Examples

### Python
```python
import httpx

# Find React experts
response = httpx.get(
    "http://localhost:8000/api/v1/experts/React",
    params={"timeframe_days": 30, "min_messages": 5}
)
experts = response.json()

# Find channel contributors
response = httpx.get(
    "http://localhost:8000/api/v1/contributors/engineering",
    params={"limit": 10, "sort_by": "engagement"}
)
contributors = response.json()

# Custom analysis
response = httpx.post(
    "http://localhost:8000/api/v1/analyze",
    json={
        "query": "Who discussed microservices architecture?",
        "timeframe_days": 60
    }
)
analysis = response.json()
```

### cURL
```bash
# Find experts
curl "http://localhost:8000/api/v1/experts/Python?timeframe_days=30"

# Find contributors
curl "http://localhost:8000/api/v1/contributors/engineering?limit=10"

# Custom analysis
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"query": "Who are the DevOps experts?", "timeframe_days": 90}'
```

## Project Structure

```
bobager/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # API endpoints
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── mcp_client.py       # Slack MCP client
│   │   ├── bob_client.py       # Bob LLM client
│   │   ├── slack_service.py    # Slack data service
│   │   └── analysis_service.py # Analysis orchestration
│   └── utils/
│       ├── __init__.py
│       ├── logger.py           # Logging setup
│       └── cache.py            # Cache manager
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
isort app/
```

### Type Checking
```bash
mypy app/
```

## Troubleshooting

### Slack MCP Connection Issues
- Ensure your Slack MCP server is running
- Check `SLACK_MCP_HOST` and `SLACK_MCP_PORT` in `.env`
- Verify the MCP transport type matches your server configuration

### Bob API Issues
- Verify `BOB_API_URL` and `BOB_API_KEY` are correct
- Check Bob API is accessible from your network
- Review logs for detailed error messages

### Cache Issues
- Clear cache using `POST /api/v1/cache/clear`
- Adjust `CACHE_TTL` and `CACHE_MAX_SIZE` in `.env`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

ISC

## Support

For issues and questions, please open an issue on GitHub.

## Roadmap

- [ ] Add authentication and authorization
- [ ] Implement rate limiting
- [ ] Add Redis cache support
- [ ] Create web frontend
- [ ] Add more analysis types
- [ ] Support multiple Slack workspaces
- [ ] Add export functionality (PDF, CSV)
- [ ] Implement webhooks for real-time analysis