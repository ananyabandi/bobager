# Step-by-Step: Testing GitHub MCP Server

Follow these exact steps to test your GitHub MCP server.

---

## Test 1: List Available Tools (5 seconds)

**Step 1:** Open a new terminal window

**Step 2:** Copy and paste this ENTIRE command:
```bash
export GITHUB_PERSONAL_ACCESS_TOKEN="YOUR_GITHUB_TOKEN_HERE" && echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | npx -y @modelcontextprotocol/server-github
```

**Step 3:** Press Enter

**Expected Result:** You'll see a JSON response listing all available tools like:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {"name": "create_repository", ...},
      {"name": "get_file_contents", ...},
      ...
    ]
  }
}
```

✅ **Success!** If you see the tools list, the server is working!

---

## Test 2: List Your GitHub Repositories (10 seconds)

**Step 1:** In the same terminal, copy and paste:
```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_repositories","arguments":{}},"id":2}' | npx -y @modelcontextprotocol/server-github
```

**Step 2:** Press Enter

**Expected Result:** You'll see a list of your GitHub repositories:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Repository: username/repo1\nDescription: ...\n..."
      }
    ]
  }
}
```

✅ **Success!** You can now see your repositories!

---

## Test 3: Search for Repositories (10 seconds)

**Step 1:** Copy and paste:
```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"search_repositories","arguments":{"query":"chatbot"}},"id":3}' | npx -y @modelcontextprotocol/server-github
```

**Step 2:** Press Enter

**Expected Result:** You'll see search results for repositories about "chatbot"

✅ **Success!** You can search GitHub!

---

## Test 4: Read a File from a Repository (15 seconds)

**Step 1:** First, pick a repository you want to read from. For example:
- Owner: `octocat`
- Repo: `Hello-World`
- File: `README`

**Step 2:** Copy and paste (replace with your own repo if you want):
```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_file_contents","arguments":{"owner":"octocat","repo":"Hello-World","path":"README"}},"id":4}' | npx -y @modelcontextprotocol/server-github
```

**Step 3:** Press Enter

**Expected Result:** You'll see the contents of the README file

✅ **Success!** You can read files from any public repository!

---

## Test 5: Using the Helper Script (Interactive)

**Step 1:** Navigate to your project directory:
```bash
cd /Users/shrutisonavane/bobager
```

**Step 2:** Run the helper script:
```bash
./test-github-mcp.sh
```

**Step 3:** You'll see a menu:
```
Available commands:
1. List available tools
2. Search repositories
3. List your repositories
4. Get file contents
5. Create repository

Enter command number (1-5):
```

**Step 4:** Type `3` and press Enter to list your repositories

**Step 5:** Wait for the results

✅ **Success!** The interactive script makes it easy!

---

## Troubleshooting

### Problem: "command not found"
**Solution:** Make sure Node.js is installed:
```bash
node --version
npm --version
```

### Problem: "Permission denied"
**Solution:** Check your GitHub token has the right scopes

### Problem: "Rate limit exceeded"
**Solution:** Wait a few minutes and try again

### Problem: No output or hanging
**Solution:** 
1. Press Ctrl+C to stop
2. Check your internet connection
3. Try the command again

---

## What Each Test Does

1. **Test 1** - Verifies the MCP server is running and can list its capabilities
2. **Test 2** - Tests authentication and lists your repositories
3. **Test 3** - Tests the search functionality across all of GitHub
4. **Test 4** - Tests reading file contents from a repository
5. **Test 5** - Tests the interactive helper script

---

## Next Steps After Testing

Once all tests pass, you can:

1. **Analyze any repository:**
   ```bash
   echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_file_contents","arguments":{"owner":"OWNER","repo":"REPO","path":"FILE"}},"id":5}' | npx -y @modelcontextprotocol/server-github
   ```

2. **Create an issue:**
   ```bash
   echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"create_issue","arguments":{"owner":"YOUR_USERNAME","repo":"YOUR_REPO","title":"Test Issue","body":"Testing MCP"}},"id":6}' | npx -y @modelcontextprotocol/server-github
   ```

3. **Build your own scripts** using the examples in `USING_GITHUB_MCP.md`

---

## Quick Reference

**Set token (do this first in each new terminal):**
```bash
export GITHUB_PERSONAL_ACCESS_TOKEN="YOUR_GITHUB_TOKEN_HERE"
```

**Basic command structure:**
```bash
echo 'JSON_REQUEST' | npx -y @modelcontextprotocol/server-github
```

**Interactive script:**
```bash
./test-github-mcp.sh
```

---

## Summary

✅ Test 1: List tools → Verify server works
✅ Test 2: List repos → Verify authentication
✅ Test 3: Search → Verify GitHub API access
✅ Test 4: Read file → Verify file operations
✅ Test 5: Helper script → Verify interactive mode

All tests should complete in under 1 minute total!