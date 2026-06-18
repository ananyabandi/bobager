# macOS Setup Guide for Bobager

Complete setup instructions for running Bobager on macOS with Homebrew.

## Prerequisites Check

First, verify you have the required tools:

```bash
# Check Python version (need 3.11+)
python3 --version

# Check if Homebrew is installed
brew --version

# Check if you have pip
pip3 --version
```

## Step 1: Install Python 3.11+ (if needed)

If you don't have Python 3.11 or higher:

```bash
# Install Python 3.11 via Homebrew
brew install python@3.11

# Verify installation
python3.11 --version
```

## Step 2: Set Up Virtual Environment

Navigate to the project directory and create a virtual environment:

```bash
# Navigate to project
cd /Users/davidquiroz/Desktop/bobager

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Your prompt should now show (venv) at the beginning
```

## Step 3: Install Dependencies

With the virtual environment activated:

```bash
# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# This will install:
# - FastAPI and Uvicorn (web framework)
# - MCP SDK (for Slack connection)
# - httpx (for Bob API calls)
# - Pydantic (data validation)
# - pytest (testing)
# - and other dependencies
```

## Step 4: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your settings
nano .env
# or use your preferred editor:
# code .env  (VS Code)
# vim .env   (Vim)
```

Update these critical values in `.env`:

```env
# Your Slack MCP server details
SLACK_MCP_HOST=localhost
SLACK_MCP_PORT=3000
SLACK_MCP_TRANSPORT=stdio

# Your Bob API credentials
BOB_API_URL=http://localhost:8080/api
BOB_API_KEY=your_actual_bob_api_key_here

# App settings (defaults are fine for development)
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True
LOG_LEVEL=INFO
```

## Step 5: Verify Slack MCP Server

Make sure your Slack MCP server is running:

```bash
# Check if your Slack MCP server process is running
# (adjust the command based on how you start your MCP server)
ps aux | grep slack-mcp

# If not running, start it according to your MCP server's documentation
```

## Step 6: Run the Application

With everything configured:

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the FastAPI server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# You should see output like:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

## Step 7: Test the API

Open a new terminal window (keep the server running) and test:

```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Or open in your browser:
# http://localhost:8000/docs  (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

## Step 8: Run Tests (Optional)

In a new terminal with virtual environment activated:

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Common Issues & Solutions

### Issue: "command not found: python3"
```bash
# Install Python via Homebrew
brew install python@3.11
```

### Issue: "No module named 'fastapi'"
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Connection refused" when accessing API
```bash
# Check if server is running
lsof -i :8000

# If port is in use, kill the process or use a different port
kill -9 <PID>
# or
python -m uvicorn app.main:app --reload --port 8001
```

### Issue: "Cannot connect to Slack MCP server"
```bash
# Verify MCP server is running
ps aux | grep slack-mcp

# Check MCP server logs
# Verify SLACK_MCP_HOST and SLACK_MCP_PORT in .env
```

### Issue: "Bob API connection failed"
```bash
# Verify Bob API is accessible
curl http://localhost:8080/api/health

# Check BOB_API_URL and BOB_API_KEY in .env
```

## Development Workflow

### Starting Development Session
```bash
cd /Users/davidquiroz/Desktop/bobager
source venv/bin/activate
python -m uvicorn app.main:app --reload
```

### Stopping the Server
Press `CTRL+C` in the terminal where the server is running

### Deactivating Virtual Environment
```bash
deactivate
```

## Using Docker (Alternative Method)

If you prefer Docker:

```bash
# Install Docker Desktop for Mac (if not installed)
brew install --cask docker

# Start Docker Desktop, then:

# Build and run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Quick Start Script

Create a convenience script:

```bash
# Create start script
cat > start.sh << 'EOF'
#!/bin/bash
cd /Users/davidquiroz/Desktop/bobager
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
EOF

# Make it executable
chmod +x start.sh

# Run it
./start.sh
```

## Next Steps

1. ✅ Access Swagger UI: http://localhost:8000/docs
2. ✅ Test the `/api/v1/health` endpoint
3. ✅ Try finding experts: `/api/v1/experts/Python`
4. ✅ Explore the interactive API documentation
5. ✅ Start building your frontend to call these APIs

## Useful Commands

```bash
# Check what's running on port 8000
lsof -i :8000

# View real-time logs
tail -f logs/app.log

# Check Python packages installed
pip list

# Update a specific package
pip install --upgrade fastapi

# Freeze current dependencies
pip freeze > requirements.txt
```

## Support

If you encounter issues:
1. Check the logs in the terminal
2. Verify all environment variables in `.env`
3. Ensure Slack MCP server is running
4. Confirm Bob API is accessible
5. Check the troubleshooting section above

Happy coding! 🚀