# 🤖 Bobager - GitHub-Powered AI Chatbot

A beautiful chatbot interface integrated with GitHub MCP (Model Context Protocol) server for real-time GitHub repository analysis.

## ✨ Features

- 🎨 IBM Bob-inspired UI with gradient theme
- 🔍 Search GitHub repositories
- 📄 Read files from any repository
- 📝 View commit history
- 🐛 List and analyze issues
- 🚀 Real-time GitHub API integration via MCP

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Start the Server
```bash
npm start
```

### 3. Open in Browser
Visit: **http://localhost:3000**

## 💬 Try These Commands

```
"Search for chatbot repositories"
"Show me facebook/react/README.md"
"List commits from torvalds/linux"
"Show issues in microsoft/vscode"
"Help"
```

## 📁 Project Structure

```
bobager/
├── index.html              # Chatbot UI
├── app.js                  # Frontend (calls backend API)
├── styles.css              # Styling
├── server.js               # Backend with MCP integration
├── package.json            # Node.js config
├── mcp-config.json         # GitHub token (gitignored)
└── INTEGRATION_GUIDE.md    # Detailed documentation
```

## 🔧 How It Works

1. User types message in chatbot
2. Frontend sends to backend API
3. Backend parses intent and calls GitHub MCP
4. MCP communicates with GitHub API
5. Response formatted and displayed

## 📚 Documentation

- **INTEGRATION_GUIDE.md** - Complete integration guide
- **CORRECTED_TESTS.md** - All 26 MCP tools available
- **GITHUB_MCP_SETUP.md** - Initial MCP setup

## 🛠️ Development

```bash
npm run dev  # Auto-reload on changes
```

## 🔐 Security

- GitHub token stored in `mcp-config.json` (gitignored)
- Never commit tokens to repository
- Token loaded automatically on server start

## 🎯 Current Status

✅ Frontend chatbot UI
✅ Backend Express server
✅ GitHub MCP integration
✅ Natural language parsing
✅ Real-time GitHub data

## 🚀 What's Next

- Add more MCP tools (create issues, PRs, etc.)
- Improve natural language understanding
- Add authentication
- Deploy to production

---

**Built with ❤️ using GitHub MCP Server**