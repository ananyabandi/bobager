# GitHub MCP Server Setup Guide

This guide will help you set up and use the GitHub MCP (Model Context Protocol) server to access and analyze GitHub repositories.

## Prerequisites

- Node.js and npm installed
- A GitHub account
- A GitHub Personal Access Token

## Step 1: Create a GitHub Personal Access Token

1. Go to GitHub Settings: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a descriptive name (e.g., "MCP Server Access")
4. Select the following scopes based on what you need:

### Minimum Required Scopes (Read-Only Access):
   - ✅ `repo` → `public_repo` (Access public repositories only)
   - ✅ `read:user` (Read user profile data)
   - ✅ `user:email` (Access user email addresses)

### Recommended Scopes (Read & Analyze):
   - ✅ `repo` (Full control - needed to read private repos you own)
   - ✅ `read:org` (Read org and team membership)
   - ✅ `read:user` (Read user profile data)
   - ✅ `user:email` (Access user email addresses)

### Full Access Scopes (Read, Write, Create):
   - ✅ `repo` (Full control of repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
   - ✅ `read:org` (Read org and team membership)
   - ✅ `read:user` (Read user profile data)
   - ✅ `user:email` (Access user email addresses)

**Choose based on your needs:**
- **Just analyzing/reading repos?** → Use Minimum or Recommended scopes
- **Need to create issues, PRs, or push code?** → Use Full Access scopes

5. Click "Generate token"
6. **IMPORTANT**: Copy the token immediately (you won't see it again)

## Step 2: Configure the MCP Server

1. Open `mcp-config.json` in this project
2. Replace `<your-github-token-here>` with your actual GitHub token:

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
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_actual_token_here"
      }
    }
  }
}
```

## Step 3: Configure Cline to Use MCP

1. Open Cline settings in VS Code
2. Navigate to MCP Settings
3. Add the path to your `mcp-config.json` file:
   - Full path: `/Users/shrutisonavane/bobager/mcp-config.json`
4. Save and restart Cline if needed

## Step 4: Available GitHub MCP Tools

Once configured, you'll have access to these tools through Cline:

### Repository Operations
- **create_repository**: Create a new GitHub repository
- **get_file_contents**: Read file contents from a repository
- **push_files**: Push files to a repository
- **create_or_update_file**: Create or update a single file
- **search_repositories**: Search for repositories
- **create_issue**: Create an issue in a repository
- **create_pull_request**: Create a pull request
- **fork_repository**: Fork a repository
- **create_branch**: Create a new branch

### Repository Analysis
- **list_commits**: Get commit history
- **list_issues**: List repository issues
- **get_issue**: Get details of a specific issue
- **list_pull_requests**: List pull requests
- **get_pull_request**: Get PR details

## Usage Examples

### Example 1: Analyze a Repository
Ask Cline: "Use the GitHub MCP server to analyze the structure of the repository owner/repo-name"

### Example 2: Read File Contents
Ask Cline: "Get the contents of README.md from the repository owner/repo-name"

### Example 3: Search Repositories
Ask Cline: "Search GitHub for repositories related to 'chatbot AI' using the MCP server"

### Example 4: Create an Issue
Ask Cline: "Create an issue in my repository titled 'Add dark mode support' with a description"

### Example 5: List Commits
Ask Cline: "Show me the recent commits from the main branch of owner/repo-name"

## Security Best Practices

1. **Never commit your token**: Add `mcp-config.json` to `.gitignore`
2. **Use environment variables**: For production, use environment variables instead of hardcoding tokens
3. **Limit token scope**: Only grant necessary permissions
4. **Rotate tokens regularly**: Generate new tokens periodically
5. **Revoke unused tokens**: Remove tokens you're no longer using

## Troubleshooting

### Token Not Working
- Verify the token has the correct scopes
- Check if the token has expired
- Ensure there are no extra spaces in the token string

### MCP Server Not Found
- Ensure Node.js and npm are installed
- The server will be downloaded automatically on first use via `npx`

### Permission Denied
- Check that your token has access to the repository
- For organization repos, ensure your token has org access

## Alternative: Using Environment Variables

For better security, you can use environment variables:

1. Add to your shell profile (~/.bashrc, ~/.zshrc, etc.):
```bash
export GITHUB_PERSONAL_ACCESS_TOKEN="ghp_your_token_here"
```

2. Update `mcp-config.json`:
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    }
  }
}
```

The server will automatically read from the environment variable.

## Next Steps

1. Create your GitHub token
2. Update `mcp-config.json` with your token
3. Configure Cline to use the MCP config file
4. Start using GitHub MCP tools through Cline!

## Resources

- [GitHub MCP Server Documentation](https://github.com/modelcontextprotocol/servers/tree/main/src/github)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [GitHub Personal Access Tokens Guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)