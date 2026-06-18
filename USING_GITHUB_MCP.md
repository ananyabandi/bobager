# Using GitHub MCP Server - Quick Guide

The GitHub MCP server is now running! Here's how to use it.

## Current Status
✅ GitHub MCP Server is running on stdio
✅ Your token is configured
✅ Ready to accept commands

## How It Works

The MCP server accepts JSON-RPC commands via stdin and returns responses via stdout.

---

## Method 1: Using the Helper Script (Easiest)

I've created a helper script for you:

```bash
./test-github-mcp.sh
```

This interactive script lets you:
1. List available tools
2. Search repositories
3. List your repositories
4. Get file contents
5. Create a repository

---

## Method 2: Direct JSON-RPC Commands

### List Available Tools
```bash
export GITHUB_PERSONAL_ACCESS_TOKEN="YOUR_GITHUB_TOKEN_HERE"
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | npx -y @modelcontextprotocol/server-github
```

### Search Repositories
```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"search_repositories","arguments":{"query":"chatbot AI"}},"id":2}' | npx -y @modelcontextprotocol/server-github
```

### List Your Repositories
```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_repositories","arguments":{}},"id":3}' | npx -y @modelcontextprotocol/server-github
```

### Get File Contents
```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_file_contents","arguments":{"owner":"username","repo":"reponame","path":"README.md"}},"id":4}' | npx -y @modelcontextprotocol/server-github
```

### Create an Issue
```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"create_issue","arguments":{"owner":"username","repo":"reponame","title":"Bug report","body":"Description of the bug"}},"id":5}' | npx -y @modelcontextprotocol/server-github
```

### List Commits
```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_commits","arguments":{"owner":"username","repo":"reponame","page":1,"per_page":10}},"id":6}' | npx -y @modelcontextprotocol/server-github
```

### Create a Pull Request
```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"create_pull_request","arguments":{"owner":"username","repo":"reponame","title":"Feature: Add new feature","body":"Description","head":"feature-branch","base":"main"}},"id":7}' | npx -y @modelcontextprotocol/server-github
```

### Fork a Repository
```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"fork_repository","arguments":{"owner":"username","repo":"reponame"}},"id":8}' | npx -y @modelcontextprotocol/server-github
```

### Create a Branch
```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"create_branch","arguments":{"owner":"username","repo":"reponame","branch":"new-feature","from_branch":"main"}},"id":9}' | npx -y @modelcontextprotocol/server-github
```

---

## Method 3: Python Script

Create a Python script to interact with the MCP server:

```python
#!/usr/bin/env python3
import subprocess
import json
import os

def call_github_mcp(method, params=None):
    env = os.environ.copy()
    env['GITHUB_PERSONAL_ACCESS_TOKEN'] = 'YOUR_GITHUB_TOKEN_HERE'
    
    request = {
        'jsonrpc': '2.0',
        'method': method,
        'id': 1
    }
    
    if params:
        request['params'] = params
    
    process = subprocess.Popen(
        ['npx', '-y', '@modelcontextprotocol/server-github'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    
    stdout, stderr = process.communicate(
        input=(json.dumps(request) + '\n').encode()
    )
    
    return json.loads(stdout.decode())

# Example: List repositories
result = call_github_mcp('tools/call', {
    'name': 'list_repositories',
    'arguments': {}
})
print(json.dumps(result, indent=2))
```

---

## Available Tools

The GitHub MCP server provides these tools:

1. **create_repository** - Create a new repository
2. **get_file_contents** - Read file contents from a repo
3. **push_files** - Push multiple files to a repo
4. **create_or_update_file** - Create or update a single file
5. **search_repositories** - Search GitHub repositories
6. **create_issue** - Create an issue
7. **create_pull_request** - Create a pull request
8. **fork_repository** - Fork a repository
9. **create_branch** - Create a new branch
10. **list_commits** - Get commit history
11. **list_issues** - List repository issues
12. **update_issue** - Update an existing issue
13. **add_issue_comment** - Comment on an issue
14. **search_code** - Search code in repositories
15. **search_issues** - Search issues and PRs
16. **search_users** - Search GitHub users
17. **get_issue** - Get issue details
18. **list_pull_requests** - List pull requests
19. **get_pull_request** - Get PR details
20. **list_repositories** - List your repositories

---

## Example Workflow: Analyze a Repository

```bash
# 1. Search for a repository
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"search_repositories","arguments":{"query":"chatbot"}},"id":1}' | npx -y @modelcontextprotocol/server-github

# 2. Get the README
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_file_contents","arguments":{"owner":"owner","repo":"repo","path":"README.md"}},"id":2}' | npx -y @modelcontextprotocol/server-github

# 3. List recent commits
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_commits","arguments":{"owner":"owner","repo":"repo"}},"id":3}' | npx -y @modelcontextprotocol/server-github

# 4. List open issues
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_issues","arguments":{"owner":"owner","repo":"repo","state":"open"}},"id":4}' | npx -y @modelcontextprotocol/server-github
```

---

## Tips

1. **Keep the server running**: The MCP server stays active and waits for commands
2. **One command at a time**: Send one JSON-RPC request, wait for response
3. **Check responses**: Look for errors in the response JSON
4. **Use the helper script**: It's easier than typing JSON manually

---

## Troubleshooting

**Server not responding?**
- Make sure the token is set: `export GITHUB_PERSONAL_ACCESS_TOKEN="..."`
- Check that the server is running
- Verify your JSON syntax is correct

**Permission errors?**
- Check your token has the right scopes
- Verify you have access to the repository

**Rate limiting?**
- GitHub has API rate limits
- Wait a few minutes and try again

---

## Next Steps

1. Try the helper script: `./test-github-mcp.sh`
2. List your repositories to test the connection
3. Explore other tools based on your needs
4. Build your own scripts using the examples above

Happy coding! 🚀