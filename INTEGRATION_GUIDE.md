# Bobager + GitHub MCP Integration Guide

Your chatbot is now integrated with the GitHub MCP server! 🎉

## What's New

✅ **Backend Server** (`server.js`) - Node.js/Express server that connects to GitHub MCP
✅ **Updated Frontend** (`app.js`) - Now calls the backend API instead of canned responses
✅ **Package Configuration** (`package.json`) - Dependencies and start scripts

---

## How to Run

### Step 1: Install Dependencies

```bash
npm install
```

This installs:
- `express` - Web server
- `cors` - Cross-origin requests
- `nodemon` - Auto-restart during development (optional)

### Step 2: Start the Server

```bash
npm start
```

The server will:
- Start on http://localhost:3000
- Load your GitHub token from `mcp-config.json`
- Connect to the GitHub MCP server
- Serve your chatbot interface

### Step 3: Open in Browser

Visit: **http://localhost:3000**

---

## What You Can Ask

### 🔍 Search Repositories
```
"Search for chatbot repositories"
"Find machine learning repos"
"Search for python projects"
```

### 📄 Read Files
```
"Show me facebook/react/README.md"
"Read octocat/Hello-World/README"
"Get the package.json from owner/repo"
```

### 📝 List Commits
```
"List commits from facebook/react"
"Show commits in owner/repo"
```

### 🐛 View Issues
```
"Show issues in facebook/react"
"List issues from owner/repo"
```

### ❓ Get Help
```
"Help"
"What can you do?"
```

---

## Architecture

```
┌─────────────────┐
│   Browser       │
│  (index.html)   │
│   (app.js)      │
└────────┬────────┘
         │ HTTP POST /api/chat
         ▼
┌─────────────────┐
│  Express Server │
│   (server.js)   │
└────────┬────────┘
         │ JSON-RPC
         ▼
┌─────────────────┐
│  GitHub MCP     │
│     Server      │
└────────┬────────┘
         │ REST API
         ▼
┌─────────────────┐
│   GitHub API    │
└─────────────────┘
```

---

## How It Works

1. **User types a message** in the chatbot UI
2. **Frontend sends** the message to `/api/chat` endpoint
3. **Backend analyzes** the message to determine intent
4. **Backend calls** the appropriate GitHub MCP tool
5. **MCP server** communicates with GitHub API
6. **Response flows back** through the chain
7. **Frontend displays** the formatted response

---

## API Endpoints

### POST /api/chat
Send a chat message and get a response.

**Request:**
```json
{
  "message": "Search for chatbot repositories"
}
```

**Response:**
```json
{
  "response": "Found repositories:\n1. owner/repo - description\n..."
}
```

### GET /api/health
Check if the server and MCP connection are working.

**Response:**
```json
{
  "status": "ok",
  "mcpConnected": true,
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

---

## Supported Commands

The backend parses natural language and maps to MCP tools:

| User Intent | MCP Tool | Example |
|------------|----------|---------|
| Search repos | `search_repositories` | "Search for AI repos" |
| Read file | `get_file_contents` | "Show me owner/repo/file.js" |
| List commits | `list_commits` | "Commits from owner/repo" |
| View issues | `list_issues` | "Issues in owner/repo" |

---

## Development

### Run with Auto-Reload
```bash
npm run dev
```

Uses `nodemon` to automatically restart when you change files.

### Modify Intent Parsing

Edit `server.js` in the `/api/chat` endpoint to add new commands:

```javascript
else if (lowerMessage.includes('your-keyword')) {
  const mcpResponse = await callMCP('tools/call', {
    name: 'tool_name',
    arguments: { /* your args */ }
  });
  response = formatResponse(mcpResponse);
}
```

### Add New MCP Tools

See `CORRECTED_TESTS.md` for all 26 available MCP tools. Add handlers in `server.js` for any tool you want to support.

---

## Troubleshooting

### "Connection error" in chatbot
**Problem:** Server is not running
**Solution:** Run `npm start` in terminal

### "MCP request timeout"
**Problem:** GitHub MCP server not responding
**Solution:** Check your GitHub token in `mcp-config.json`

### "Module not found"
**Problem:** Dependencies not installed
**Solution:** Run `npm install`

### CORS errors
**Problem:** Frontend and backend on different origins
**Solution:** Server already has CORS enabled, make sure you're accessing via http://localhost:3000

---

## Environment Variables

The server reads your GitHub token from `mcp-config.json`. Alternatively, you can set it as an environment variable:

```bash
export GITHUB_PERSONAL_ACCESS_TOKEN="your_token_here"
npm start
```

---

## Production Deployment

For production, you'll want to:

1. **Use environment variables** instead of `mcp-config.json`
2. **Add authentication** to protect your API
3. **Rate limiting** to prevent abuse
4. **Error handling** improvements
5. **Deploy to a service** like Heroku, Railway, or Vercel

---

## Next Steps

1. ✅ Run `npm install`
2. ✅ Run `npm start`
3. ✅ Open http://localhost:3000
4. ✅ Try: "Search for chatbot repositories"
5. ✅ Explore other commands!

---

## Files Overview

- `server.js` - Backend server with MCP integration
- `app.js` - Frontend JavaScript (updated to call API)
- `index.html` - Chatbot UI
- `styles.css` - Styling
- `package.json` - Node.js configuration
- `mcp-config.json` - GitHub token (gitignored)

---

**Your chatbot now has real GitHub powers! 🚀**