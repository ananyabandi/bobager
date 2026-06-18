#!/bin/bash

# GitHub MCP Server Test Script
# This script helps you interact with the GitHub MCP server

export GITHUB_PERSONAL_ACCESS_TOKEN="YOUR_GITHUB_TOKEN_HERE"

echo "Starting GitHub MCP Server..."
echo ""
echo "Available commands:"
echo "1. List available tools"
echo "2. Search repositories"
echo "3. List your repositories"
echo "4. Get file contents"
echo "5. Create repository"
echo ""
read -p "Enter command number (1-5): " choice

case $choice in
  1)
    echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | npx -y @modelcontextprotocol/server-github
    ;;
  2)
    read -p "Enter search query: " query
    echo "{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"search_repositories\",\"arguments\":{\"query\":\"$query\"}},\"id\":2}" | npx -y @modelcontextprotocol/server-github
    ;;
  3)
    echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_repositories","arguments":{}},"id":3}' | npx -y @modelcontextprotocol/server-github
    ;;
  4)
    read -p "Enter owner/repo: " repo
    read -p "Enter file path: " filepath
    echo "{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"get_file_contents\",\"arguments\":{\"owner\":\"${repo%/*}\",\"repo\":\"${repo#*/}\",\"path\":\"$filepath\"}},\"id\":4}" | npx -y @modelcontextprotocol/server-github
    ;;
  5)
    read -p "Enter repository name: " reponame
    read -p "Enter description: " desc
    read -p "Private? (true/false): " private
    echo "{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"create_repository\",\"arguments\":{\"name\":\"$reponame\",\"description\":\"$desc\",\"private\":$private}},\"id\":5}" | npx -y @modelcontextprotocol/server-github
    ;;
  *)
    echo "Invalid choice"
    ;;
esac

# Made with Bob
