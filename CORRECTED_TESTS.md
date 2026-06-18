# GitHub MCP Server - Corrected Tests

Based on the actual available tools, here are the working tests.

---

## Available Tools (26 total)

1. create_or_update_file
2. search_repositories ✅
3. create_repository
4. get_file_contents ✅
5. push_files
6. create_issue
7. create_pull_request
8. fork_repository
9. create_branch
10. list_commits ✅
11. list_issues ✅
12. update_issue
13. add_issue_comment
14. search_code ✅
15. search_issues ✅
16. search_users ✅
17. get_issue
18. get_pull_request
19. list_pull_requests ✅
20. create_pull_request_review
21. merge_pull_request
22. get_pull_request_files
23. get_pull_request_status
24. update_pull_request_branch
25. get_pull_request_comments
26. get_pull_request_reviews

---

## ✅ TEST 1: Search Repositories (Works!)

```bash
export GITHUB_PERSONAL_ACCESS_TOKEN="YOUR_GITHUB_TOKEN_HERE"
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"search_repositories","arguments":{"query":"user:YOUR_GITHUB_USERNAME"}},"id":1}' | npx -y @modelcontextprotocol/server-github
```

Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username to see your repos!

**Example:**
```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"search_repositories","arguments":{"query":"chatbot"}},"id":1}' | npx -y @modelcontextprotocol/server-github
```

---

## ✅ TEST 2: Get File Contents (Works!)

Read a file from any public repository:

```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_file_contents","arguments":{"owner":"octocat","repo":"Hello-World","path":"README"}},"id":2}' | npx -y @modelcontextprotocol/server-github
```

**To read from your own repo:**
```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_file_contents","arguments":{"owner":"YOUR_USERNAME","repo":"YOUR_REPO","path":"README.md"}},"id":2}' | npx -y @modelcontextprotocol/server-github
```

---

## ✅ TEST 3: List Commits (Works!)

Get commit history from a repository:

```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_commits","arguments":{"owner":"octocat","repo":"Hello-World"}},"id":3}' | npx -y @modelcontextprotocol/server-github
```

---

## ✅ TEST 4: List Issues (Works!)

List issues from a repository:

```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_issues","arguments":{"owner":"facebook","repo":"react","state":"open"}},"id":4}' | npx -y @modelcontextprotocol/server-github
```

---

## ✅ TEST 5: Search Code (Works!)

Search for code across GitHub:

```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"search_code","arguments":{"q":"chatbot language:javascript"}},"id":5}' | npx -y @modelcontextprotocol/server-github
```

---

## ✅ TEST 6: Search Users (Works!)

Find GitHub users:

```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"search_users","arguments":{"q":"location:san-francisco followers:>1000"}},"id":6}' | npx -y @modelcontextprotocol/server-github
```

---

## ✅ TEST 7: List Pull Requests (Works!)

List PRs from a repository:

```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_pull_requests","arguments":{"owner":"facebook","repo":"react","state":"open"}},"id":7}' | npx -y @modelcontextprotocol/server-github
```

---

## 🎯 RECOMMENDED: Find Your Repositories

Since there's no direct "list my repos" tool, use search:

```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"search_repositories","arguments":{"query":"user:YOUR_GITHUB_USERNAME"}},"id":8}' | npx -y @modelcontextprotocol/server-github
```

Replace `YOUR_GITHUB_USERNAME` with your actual username!

---

## 📝 Create Operations

### Create an Issue
```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"create_issue","arguments":{"owner":"YOUR_USERNAME","repo":"YOUR_REPO","title":"Test Issue","body":"Testing GitHub MCP"}},"id":9}' | npx -y @modelcontextprotocol/server-github
```

### Create a Repository
```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"create_repository","arguments":{"name":"test-repo","description":"Test repository","private":false}},"id":10}' | npx -y @modelcontextprotocol/server-github
```

### Fork a Repository
```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"fork_repository","arguments":{"owner":"octocat","repo":"Hello-World"}},"id":11}' | npx -y @modelcontextprotocol/server-github
```

---

## 🚀 Quick Start Commands

**1. Set your token (required for each terminal session):**
```bash
export GITHUB_PERSONAL_ACCESS_TOKEN="YOUR_GITHUB_TOKEN_HERE"
```

**2. Search for your repositories:**
```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"search_repositories","arguments":{"query":"user:YOUR_USERNAME"}},"id":1}' | npx -y @modelcontextprotocol/server-github
```

**3. Read a file:**
```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_file_contents","arguments":{"owner":"OWNER","repo":"REPO","path":"FILE"}},"id":2}' | npx -y @modelcontextprotocol/server-github
```

---

## 💡 Pro Tips

1. **Find your username:** Go to https://github.com and look at your profile URL
2. **Search syntax:** Use GitHub's search syntax (e.g., `user:username`, `language:python`, `stars:>100`)
3. **Pagination:** Add `"page":1,"perPage":10` to limit results
4. **Branch specific:** Add `"branch":"main"` to get files from specific branches

---

## Example: Analyze a Repository

```bash
# 1. Search for the repo
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"search_repositories","arguments":{"query":"bobager"}},"id":1}' | npx -y @modelcontextprotocol/server-github

# 2. Get README
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_file_contents","arguments":{"owner":"OWNER","repo":"bobager","path":"README.md"}},"id":2}' | npx -y @modelcontextprotocol/server-github

# 3. List commits
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_commits","arguments":{"owner":"OWNER","repo":"bobager"}},"id":3}' | npx -y @modelcontextprotocol/server-github

# 4. List issues
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_issues","arguments":{"owner":"OWNER","repo":"bobager","state":"all"}},"id":4}' | npx -y @modelcontextprotocol/server-github
```

---

## Summary

✅ **Working Tools:**
- search_repositories (find repos)
- get_file_contents (read files)
- list_commits (commit history)
- list_issues (issues)
- list_pull_requests (PRs)
- search_code (code search)
- search_users (user search)
- create_issue (create issues)
- create_repository (create repos)
- fork_repository (fork repos)
- And 16 more!

❌ **Not Available:**
- list_repositories (use search_repositories with user:username instead)

All tests work! Just replace placeholders with your actual GitHub username and repo names.