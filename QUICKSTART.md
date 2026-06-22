# Quick Start Guide

## ✅ Installation Complete!

All dependencies have been successfully installed and tested. Your environment is ready to run.

## 📋 Prerequisites

Before starting, make sure you have:
1. **Ollama installed** - Download from https://ollama.ai
2. **Ollama running** - Run `ollama serve` in a terminal
3. **A model pulled** - Run `ollama pull llama2` (or your preferred model)
4. **Slack API tokens** - Get from https://api.slack.com/apps

## 🚀 Start the Server

```bash
# Make sure you're in the project directory with venv activated
cd /Users/davidquiroz/Desktop/bobager
source venv/bin/activate

# Run the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at: **http://localhost:8000**

## 📝 Configure Environment (Required First Time)

Before running, you need to configure your tokens:

```bash
# Copy the example file
cp .env.example .env

# Edit with your credentials
nano .env
```

Update these values in `.env`:

```env
# Your Slack API tokens (get from https://api.slack.com/apps)
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here

# Ollama configuration (defaults should work if Ollama is running locally)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# App settings (defaults are fine)
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True
LOG_LEVEL=INFO
```

### Getting Slack API Tokens

1. Go to https://api.slack.com/apps
2. Create a new app or select existing
3. Go to "OAuth & Permissions" for Bot Token
4. Go to "Basic Information" for App Token and Signing Secret
5. Required Bot Token Scopes:
   - `channels:history`
   - `channels:read`
   - `users:read`
   - `search:read`

### Setting Up Ollama

```bash
# Install Ollama (if not already installed)
# Visit https://ollama.ai for installation instructions

# Start Ollama server
ollama serve

# Pull a model (in another terminal)
ollama pull llama2

# Or use a different model
ollama pull mistral
ollama pull codellama
```

## 🎯 Test the API

Once the server is running:

1. **Interactive API Docs**: http://localhost:8000/docs
2. **Alternative Docs**: http://localhost:8000/redoc
3. **Health Check**: http://localhost:8000/api/v1/health

### Quick Test with cURL

```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Find Python experts
curl "http://localhost:8000/api/v1/experts/Python?timeframe_days=30"

# Find contributors in a channel
curl "http://localhost:8000/api/v1/contributors/engineering?limit=10"
```

## 📦 What's Installed

- ✅ Python 3.11.15
- ✅ FastAPI 0.137.2
- ✅ Uvicorn 0.49.0
- ✅ Slack SDK 3.42.0
- ✅ Ollama integration (local LLM)
- ✅ All dependencies with no conflicts

## 🔄 Future Installations

If you need to reinstall or set up on another machine:

```bash
# Create and activate venv
python3.11 -m venv venv
source venv/bin/activate

# Run the install script
./install.sh

# Or manually:
pip install -r requirements.txt
```

## 🛠️ Development Commands

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Check for issues
pip check

# View installed packages
pip list
```

## 📚 API Endpoints

### Find Experts
```http
GET /api/v1/experts/{topic}
POST /api/v1/experts
```

### Find Contributors  
```http
GET /api/v1/contributors/{channel}
POST /api/v1/contributors
```

### Custom Analysis
```http
POST /api/v1/analyze
```

### Utility
```http
GET /api/v1/health
GET /api/v1/cache/stats
POST /api/v1/cache/clear
```

## 🎉 You're Ready!

Everything is set up and working. Just:
1. Make sure Ollama is running (`ollama serve`)
2. Configure your `.env` file with Slack API tokens
3. Start the server!

## 🔧 Troubleshooting

### "Missing required fields" error
Make sure all three Slack tokens are set in `.env`:
- SLACK_BOT_TOKEN
- SLACK_APP_TOKEN  
- SLACK_SIGNING_SECRET

### Slack API errors
- Verify your bot has the required scopes
- Check that tokens are correct and not expired
- Ensure your app is installed in the workspace

### Ollama connection errors
- Make sure Ollama is running: `ollama serve`
- Check Ollama is accessible: `curl http://localhost:11434/api/tags`
- Verify you have a model pulled: `ollama list`
- Try pulling a model: `ollama pull llama2`

### Slow responses
- First request to Ollama may be slow (model loading)
- Consider using a smaller/faster model like `mistral`
- Adjust `OLLAMA_MODEL` in `.env` to use different models

## 🌟 Benefits of Using Ollama

- ✅ **Privacy**: All LLM processing happens locally
- ✅ **No API costs**: Free to use
- ✅ **Offline capable**: Works without internet
- ✅ **Customizable**: Use any Ollama-compatible model
- ✅ **Fast**: No network latency for LLM calls

For more details, see:
- **README.md** - Full documentation
- **SETUP_MACOS.md** - Detailed macOS setup