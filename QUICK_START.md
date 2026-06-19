# 🚀 Quick Start - Integrated Slack + GitHub Bobager

## 1️⃣ Install Dependencies

### Python
```bash
source venv/bin/activate  # Activate virtual environment
pip install -r requirements.txt
```

### Node.js (for GitHub MCP)
```bash
npm install
# This installs @modelcontextprotocol/server-github
```

## 2️⃣ Configure Environment

```bash
cp .env.example .env
```

Then edit `.env` with your credentials:
```env
# Slack Credentials (from Slack API dashboard)
SLACK_BOT_TOKEN=xoxb-YOUR-TOKEN-HERE
SLACK_SIGNING_SECRET=YOUR-SECRET-HERE

# GitHub Personal Access Token (from github.com/settings/tokens)
GITHUB_PERSONAL_ACCESS_TOKEN=ghp-YOUR-TOKEN-HERE

# Ollama (Local LLM)
OLLAMA_BASE_URL=http://localhost:11434

# Optional
LOG_LEVEL=INFO
```

## 3️⃣ Start the Server

```bash
python -m uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

## 4️⃣ Open in Browser

Navigate to: **http://localhost:8000**

## 5️⃣ Test Both Features

### Test Slack Query
Ask: **"Who's an expert in React?"**

Expected: Gets Slack expert analysis from your workspace

### Test GitHub Query
Ask: **"Search for machine learning repositories"**

Expected: Returns GitHub repositories matching the query

## 📝 Chat Examples

### Slack Queries
- "Who can help me with Python?"
- "Who's talked about DevOps the most?"
- "Find contributors in #backend"
- "What code snippets were shared about Docker?"

### GitHub Queries
- "Search for chatbot repositories"
- "Show me facebook/react/README.md"
- "List commits from octocat/Hello-World"
- "Show open issues in tensorflow/tensorflow"

## 🔧 Configuration Notes

### Getting Slack Credentials
1. Go to https://api.slack.com/apps
2. Create a new app or select existing
3. Copy "Bot User OAuth Token" → `SLACK_BOT_TOKEN`
4. Copy "Signing Secret" → `SLACK_SIGNING_SECRET`
5. Add bot to your workspace channels

### Getting GitHub Token
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `public_repo`, `read:user`
4. Copy token → `GITHUB_PERSONAL_ACCESS_TOKEN`

### Running Ollama
```bash
# Install Ollama from https://ollama.ai
# Then run:
ollama serve

# In another terminal, pull a model:
ollama pull llama2  # or your preferred model
```

## ✅ Troubleshooting

### Backend won't start
```
Error: Address already in use
→ Try different port: --port 8001
```

### GitHub MCP not working
```
Error: MCP request timeout
→ Verify npm install completed
→ Check GITHUB_PERSONAL_ACCESS_TOKEN is set
→ Check Node.js is installed: node --version
```

### Slack connection failing
```
Error: Failed to connect to Slack
→ Verify SLACK_BOT_TOKEN is correct
→ Verify bot has scopes: chat:write, users:read, channels:history
→ Verify bot is added to channels
```

## 📚 Full Documentation

- [README.md](README.md) - Complete overview
- [INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md) - Technical details
- [INTEGRATION_CHECKLIST.md](INTEGRATION_CHECKLIST.md) - What was integrated
- [QUICKSTART.md](QUICKSTART.md) - Original David's guide
- [GITHUB_MCP_SETUP.md](GITHUB_MCP_SETUP.md) - GitHub MCP details

## 🎉 You're Ready!

Your integrated Slack + GitHub chat tool is now running!

---

**Questions?** Check the documentation files or see the troubleshooting section above.
