# Install Node.js to Use GitHub MCP Server

The GitHub MCP server requires Node.js and npm. Here's how to install them on macOS.

## Option 1: Using Homebrew (Recommended)

### Step 1: Install Homebrew (if not already installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install Node.js
```bash
brew install node
```

### Step 3: Verify Installation
```bash
node --version
npm --version
```

You should see version numbers like:
```
v20.x.x
10.x.x
```

---

## Option 2: Direct Download from nodejs.org

1. Visit: https://nodejs.org/
2. Download the macOS installer (LTS version recommended)
3. Run the installer
4. Follow the installation wizard
5. Restart your terminal
6. Verify with: `node --version` and `npm --version`

---

## After Installing Node.js

Once Node.js is installed, you can use the GitHub MCP server:

### Test the GitHub MCP Server:
```bash
export GITHUB_PERSONAL_ACCESS_TOKEN="YOUR_GITHUB_TOKEN_HERE"
npx -y @modelcontextprotocol/server-github
```

### Or use it in your project:
```bash
cd /Users/shrutisonavane/bobager
npm init -y
npm install @modelcontextprotocol/server-github
```

---

## Quick Install Command

Run this in your terminal:
```bash
# Install Homebrew (if needed) and Node.js
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" && brew install node
```

---

## Alternative: Use Claude Desktop Instead

If you don't want to install Node.js for command-line use, you can:

1. Download Claude Desktop: https://claude.ai/download
2. Claude Desktop has built-in MCP support
3. Configure it with your `mcp-config.json` settings
4. Use GitHub MCP through Claude's interface

This way, Claude Desktop handles the Node.js requirements internally.

---

## Next Steps After Installation

1. ✅ Install Node.js (using one of the methods above)
2. ✅ Verify installation: `node --version`
3. ✅ Test GitHub MCP server
4. ✅ Start using it to analyze GitHub repositories

---

## Need Help?

If you encounter issues:
- Make sure to restart your terminal after installation
- Check that Node.js is in your PATH
- Try running `which node` to verify the installation location