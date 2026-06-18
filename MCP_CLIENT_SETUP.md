# How to Use GitHub MCP Server - Client Setup Guide

You have the GitHub MCP server configured (`mcp-config.json` with your token), but you need an MCP-compatible client to use it.

## What is MCP?

MCP (Model Context Protocol) allows AI assistants to connect to external tools and services. You need an MCP client (like Claude Desktop, VS Code extensions, etc.) to use the GitHub MCP server.

---

## Option 1: Claude Desktop App (Recommended)

**Best for:** Direct interaction with Claude and GitHub repositories

### Setup Steps:

1. **Download Claude Desktop:**
   - Visit: https://claude.ai/download
   - Install for macOS

2. **Configure MCP:**
   - Open Claude Desktop
   - Go to Settings → Developer → Edit Config
   - This opens `claude_desktop_config.json`
   - Add this configuration:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_GITHUB_TOKEN_HERE"
      }
    }
  }
}
```

3. **Restart Claude Desktop**

4. **Test it:**
   - Ask Claude: "List my GitHub repositories"
   - Ask Claude: "Analyze the repository [owner/repo]"

---

## Option 2: VS Code Extensions

### A. Continue Extension

1. **Install Continue:**
   - Open VS Code
   - Go to Extensions (Cmd+Shift+X)
   - Search for "Continue"
   - Install it

2. **Configure MCP:**
   - Open Continue settings
   - Add MCP server configuration
   - Point to: `/Users/shrutisonavane/bobager/mcp-config.json`

3. **Use it:**
   - Open Continue chat panel
   - Ask about GitHub repositories

### B. Roo Cline Extension

1. **Install Roo Cline:**
   - Open VS Code Extensions
   - Search for "Roo Cline"
   - Install it

2. **Configure MCP:**
   - Open Roo Cline settings
   - Navigate to MCP configuration
   - Add config file path: `/Users/shrutisonavane/bobager/mcp-config.json`

3. **Use it:**
   - Open Roo Cline panel
   - Start asking about GitHub repos

---

## Option 3: Custom Integration (Advanced)

If you want to integrate the GitHub MCP server into your own application:

### Using Node.js:

```javascript
const { spawn } = require('child_process');

// Start the MCP server
const mcpServer = spawn('npx', ['-y', '@modelcontextprotocol/server-github'], {
  env: {
    ...process.env,
    GITHUB_PERSONAL_ACCESS_TOKEN: 'YOUR_GITHUB_TOKEN_HERE'
  }
});

// Communicate with the server via stdin/stdout
mcpServer.stdout.on('data', (data) => {
  console.log('MCP Response:', data.toString());
});

// Send requests to the server
const request = {
  jsonrpc: '2.0',
  method: 'tools/list',
  id: 1
};

mcpServer.stdin.write(JSON.stringify(request) + '\n');
```

### Using Python:

```python
import subprocess
import json
import os

# Start the MCP server
env = os.environ.copy()
env['GITHUB_PERSONAL_ACCESS_TOKEN'] = 'YOUR_GITHUB_TOKEN_HERE'

process = subprocess.Popen(
    ['npx', '-y', '@modelcontextprotocol/server-github'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env=env
)

# Send request
request = {
    'jsonrpc': '2.0',
    'method': 'tools/list',
    'id': 1
}

process.stdin.write((json.dumps(request) + '\n').encode())
process.stdin.flush()

# Read response
response = process.stdout.readline()
print(json.loads(response))
```

---

## Quick Test Without a Client

You can test the GitHub MCP server directly from the command line:

```bash
# Set your token
export GITHUB_PERSONAL_ACCESS_TOKEN="YOUR_GITHUB_TOKEN_HERE"

# Run the server
npx -y @modelcontextprotocol/server-github
```

Then send JSON-RPC requests via stdin. Example:
```json
{"jsonrpc":"2.0","method":"tools/list","id":1}
```

---

## Recommended Next Steps

### For Most Users:
1. ✅ **Install Claude Desktop** (easiest option)
2. Configure it with your `mcp-config.json` settings
3. Start chatting with Claude about your GitHub repos

### For Developers:
1. ✅ **Install Continue or Roo Cline** in VS Code
2. Configure MCP settings
3. Use it while coding

### For Custom Integration:
1. Use the Node.js or Python examples above
2. Build your own MCP client
3. Integrate with your application

---

## What Can You Do Once Set Up?

With any MCP client configured, you can:

- 📊 **Analyze repositories:** "Analyze the structure of owner/repo"
- 📄 **Read files:** "Show me the README from owner/repo"
- 🔍 **Search:** "Find repositories about machine learning"
- 📝 **Create issues:** "Create an issue in my repo about bug X"
- 🔀 **Manage PRs:** "List open pull requests in owner/repo"
- 📈 **View commits:** "Show recent commits in owner/repo"
- 🍴 **Fork repos:** "Fork owner/repo to my account"

---

## Need Help Choosing?

**Answer these questions:**

1. Do you want to chat with an AI about GitHub repos?
   → **Use Claude Desktop**

2. Do you want GitHub integration while coding in VS Code?
   → **Use Continue or Roo Cline extension**

3. Do you want to build your own tool?
   → **Use custom integration**

---

## Resources

- Claude Desktop: https://claude.ai/download
- Continue Extension: https://marketplace.visualstudio.com/items?itemName=Continue.continue
- MCP Documentation: https://modelcontextprotocol.io/
- GitHub MCP Server: https://github.com/modelcontextprotocol/servers/tree/main/src/github

---

## Your Current Setup Status

✅ GitHub token created
✅ `mcp-config.json` configured with your token
✅ `.gitignore` protecting your token
⏳ **Next:** Choose and install an MCP client (Claude Desktop recommended)

Once you install a client, you'll be able to use the GitHub MCP server!