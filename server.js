const express = require('express');
const { spawn } = require('child_process');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('.')); // Serve static files from current directory

// Call GitHub MCP Server
async function callMCP(method, params = null) {
  return new Promise((resolve, reject) => {
    // Create a fresh MCP process for each request
    const mcp = spawn('npx', ['-y', '@modelcontextprotocol/server-github'], {
      env: {
        ...process.env,
        GITHUB_PERSONAL_ACCESS_TOKEN: process.env.GITHUB_PERSONAL_ACCESS_TOKEN
      },
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    const request = {
      jsonrpc: '2.0',
      method: method,
      id: Date.now()
    };
    
    if (params) {
      request.params = params;
    }

    let responseData = '';
    let errorData = '';

    const timeout = setTimeout(() => {
      reject(new Error('MCP request timeout'));
    }, 30000);

    mcp.stdout.on('data', (data) => {
      responseData += data.toString();
      
      // Try to parse complete JSON responses
      const lines = responseData.split('\n');
      for (let i = 0; i < lines.length - 1; i++) {
        const line = lines[i].trim();
        if (line && line.startsWith('{')) {
          try {
            const response = JSON.parse(line);
            if (response.id === request.id) {
              clearTimeout(timeout);
              resolve(response);
              responseData = lines[lines.length - 1]; // Keep incomplete line
              return;
            }
          } catch (e) {
            // Not complete JSON yet
          }
        }
      }
      responseData = lines[lines.length - 1]; // Keep incomplete line
    });

    mcp.stderr.on('data', (data) => {
      errorData += data.toString();
    });

    mcp.on('error', (error) => {
      clearTimeout(timeout);
      reject(error);
    });

    mcp.on('exit', (code) => {
      if (code !== 0) {
        clearTimeout(timeout);
        reject(new Error(`MCP process exited with code ${code}`));
      }
    });

    // Send request
    mcp.stdin.write(JSON.stringify(request) + '\n');
    
    // Close stdin after writing to signal we're done
    mcp.stdin.end();
  });
}

// API endpoint to chat with GitHub MCP
app.post('/api/chat', async (req, res) => {
  try {
    const { message } = req.body;
    
    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Parse user intent
    const lowerMessage = message.toLowerCase();
    let response;

    // Search repositories
    if (lowerMessage.includes('search') && (lowerMessage.includes('repo') || lowerMessage.includes('repository'))) {
      const query = message.replace(/search|repo|repository|for|find/gi, '').trim();
      const mcpResponse = await callMCP('tools/call', {
        name: 'search_repositories',
        arguments: { query: query || 'chatbot', page: 1, perPage: 5 }
      });
      
      response = formatSearchResults(mcpResponse);
    }
    // Get file contents
    else if (lowerMessage.includes('read') || lowerMessage.includes('show') || lowerMessage.includes('get')) {
      // Try to extract owner/repo/path
      const match = message.match(/(\w+)\/(\w+)(?:\/(.+))?/);
      if (match) {
        const [, owner, repo, filepath] = match;
        const mcpResponse = await callMCP('tools/call', {
          name: 'get_file_contents',
          arguments: {
            owner,
            repo,
            path: filepath || 'README.md',
            branch: 'main'
          }
        });
        
        response = formatFileContents(mcpResponse);
      } else {
        response = "Please specify the repository in format: owner/repo/filepath";
      }
    }
    // List commits
    else if (lowerMessage.includes('commit')) {
      const match = message.match(/(\w+)\/(\w+)/);
      if (match) {
        const [, owner, repo] = match;
        const mcpResponse = await callMCP('tools/call', {
          name: 'list_commits',
          arguments: { owner, repo, page: 1, perPage: 5 }
        });
        
        response = formatCommits(mcpResponse);
      } else {
        response = "Please specify the repository in format: owner/repo";
      }
    }
    // List issues
    else if (lowerMessage.includes('issue')) {
      const match = message.match(/(\w+)\/(\w+)/);
      if (match) {
        const [, owner, repo] = match;
        const mcpResponse = await callMCP('tools/call', {
          name: 'list_issues',
          arguments: { owner, repo, state: 'open', page: 1, per_page: 5 }
        });
        
        response = formatIssues(mcpResponse);
      } else {
        response = "Please specify the repository in format: owner/repo";
      }
    }
    // Help
    else if (lowerMessage.includes('help') || lowerMessage.includes('what can you do')) {
      response = `I can help you with GitHub! Try asking me:
      
• "Search for chatbot repositories"
• "Show me facebook/react/README.md"
• "List commits from owner/repo"
• "Show issues in owner/repo"
• "Search for machine learning repos"

Just ask naturally and I'll help you explore GitHub!`;
    }
    // Default
    else {
      response = `I'm connected to GitHub! I can help you:

🔍 Search repositories
📄 Read files from repos
📝 List commits
🐛 View issues
🔀 And more!

Try: "Search for AI repositories" or "Show me octocat/Hello-World/README"`;
    }

    res.json({ response });

  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({ 
      error: 'Failed to process request',
      details: error.message 
    });
  }
});

// Format helpers
function formatSearchResults(mcpResponse) {
  if (mcpResponse.error) {
    return `Error: ${mcpResponse.error.message}`;
  }
  
  const content = mcpResponse.result?.content?.[0]?.text || '';
  return content || 'No repositories found.';
}

function formatFileContents(mcpResponse) {
  if (mcpResponse.error) {
    return `Error: ${mcpResponse.error.message}`;
  }
  
  const content = mcpResponse.result?.content?.[0]?.text || '';
  return content || 'File not found or empty.';
}

function formatCommits(mcpResponse) {
  if (mcpResponse.error) {
    return `Error: ${mcpResponse.error.message}`;
  }
  
  const content = mcpResponse.result?.content?.[0]?.text || '';
  return content || 'No commits found.';
}

function formatIssues(mcpResponse) {
  if (mcpResponse.error) {
    return `Error: ${mcpResponse.error.message}`;
  }
  
  const content = mcpResponse.result?.content?.[0]?.text || '';
  return content || 'No issues found.';
}

// Health check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString()
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Bobager server running on http://localhost:${PORT}`);
  console.log(`📡 GitHub MCP integration active`);
  console.log(`\nOpen http://localhost:${PORT} in your browser`);
});

// Cleanup on exit
process.on('SIGINT', () => {
  process.exit();
});

// Made with Bob
