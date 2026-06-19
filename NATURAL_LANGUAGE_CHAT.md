# 🗣️ Natural Language Chat with Your Slack Data

## What This Is

A **command-line chat interface** that lets you query your Slack workspace using natural language, powered by Ollama (your local LLM).

## How It Works

```
You: "Find Python experts from the last 30 days"
  ↓
Ollama: Understands query → Converts to tool call
  ↓
Your Code: Executes find_experts(topic="Python", timeframe_days=30)
  ↓
Slack API: Returns matching messages
  ↓
Ollama: Analyzes results → Formats nicely
  ↓
You: See beautiful, conversational response!
```

## Quick Start

```bash
source venv/bin/activate
python chat_with_slack.py
```

## Example Conversation

```
💬 You: Find Python experts from the last 30 days

🤔 Thinking...
🔧 Using tool: find_experts
📋 Parameters: {
  "topic": "Python",
  "timeframe_days": 30
}

⚙️  Executing...
📊 Analyzing results...

🤖 Assistant:
Based on the analysis of Slack messages from the past 30 days, I found 3 Python experts:

1. **John Doe** (@john_doe) - Expertise Score: 0.92
   - Highly active in Python discussions
   - Frequently helps others with async/await patterns
   - Strong knowledge of FastAPI and Django

2. **Jane Smith** (@jane_smith) - Expertise Score: 0.87
   - Expert in data science with Python
   - Regularly shares pandas and numpy tips
   - Active in code reviews

3. **Bob Johnson** (@bob_j) - Expertise Score: 0.81
   - DevOps automation with Python
   - Maintains several internal Python tools
   - Knowledgeable about testing frameworks

Would you like more details about any of these experts?
```

## What You Can Ask

### Find Experts
- "Find Python experts"
- "Who knows about Kubernetes?"
- "Find React experts from the last 60 days"
- "Show me people who understand microservices"

### Find Contributors
- "Who are the top contributors in #engineering?"
- "Show me the 5 most active people in #backend"
- "List contributors in the frontend channel"

### Custom Analysis
- "What are people saying about the new API?"
- "Who has been discussing database performance?"
- "Summarize conversations about security"
- "What are the main concerns about the deployment process?"

## The Magic: Ollama as Your Translator

### Step 1: Understanding Your Query
Ollama reads your natural language and converts it to a structured tool call:

```
"Find Python experts" 
→ 
{
  "tool": "find_experts",
  "params": {"topic": "Python", "timeframe_days": 30}
}
```

### Step 2: Executing the Tool
Your code calls the appropriate analysis service with the extracted parameters.

### Step 3: Formatting Results
Ollama takes the raw JSON results and formats them into a conversational, easy-to-read response.

## Why This is Better Than MCP Inspector

| Feature | MCP Inspector | Natural Language Chat |
|---------|---------------|----------------------|
| Input | Manual JSON | Natural language |
| Understanding | You translate | Ollama translates |
| Output | Raw JSON | Conversational |
| Follow-ups | Start over | Continue conversation |
| Learning curve | Need to know tools | Just ask naturally |

## Architecture

```
┌─────────────────┐
│   You (Human)   │
│  Natural Lang.  │
└────────┬────────┘
         │
┌────────▼────────┐
│  Ollama LLM     │ ← Understands intent
│  (Translation)  │    Extracts parameters
└────────┬────────┘
         │
┌────────▼────────┐
│ chat_with_slack │ ← Orchestrates
│     .py         │    tool calls
└────────┬────────┘
         │
    ┌────┴─────┐
    │          │
┌───▼──┐  ┌───▼────┐
│Slack │  │Analysis│
│ API  │  │Service │
└───┬──┘  └───┬────┘
    │         │
    └────┬────┘
         │
┌────────▼────────┐
│  Ollama LLM     │ ← Analyzes data
│  (Analysis)     │    Formats response
└────────┬────────┘
         │
┌────────▼────────┐
│   You (Human)   │
│  Get Answer!    │
└─────────────────┘
```

## Requirements

✅ Ollama running locally  
✅ Slack tokens in `.env`  
✅ Virtual environment activated  

## Tips for Best Results

### Be Specific
❌ "Find experts"  
✅ "Find Python experts from the last 30 days"

### Use Natural Language
❌ `{"tool": "find_experts", "params": {"topic": "Python"}}`  
✅ "Find Python experts"

### Ask Follow-up Questions
```
You: Find Python experts
Bot: [Shows 3 experts]
You: Tell me more about the first one
Bot: [Provides details]
```

## Troubleshooting

### "Could not understand the query"
- Try rephrasing more clearly
- Be more specific about what you want
- Use simpler language

### "Ollama connection error"
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve
```

### "Slack connection failed"
```bash
# Check your .env file
cat .env | grep SLACK

# Make sure tokens are set
```

## Comparison: Three Ways to Use Your Tools

### 1. MCP Inspector (Testing)
```bash
./test_mcp_ui.sh
# Manual JSON input in web UI
```

### 2. Natural Language Chat (This!)
```bash
python chat_with_slack.py
# Just talk naturally
```

### 3. Claude Desktop (Production)
```
# Add to Claude config
# Use in Claude Desktop app
```

## What Makes This Special

🎯 **No Claude Desktop needed** - Works standalone  
🤖 **Your own LLM** - Uses Ollama locally  
🔒 **Privacy** - Everything runs on your machine  
💬 **Conversational** - Natural back-and-forth  
🎨 **Custom** - You control the prompts and logic  

## Next Steps

1. ✅ Run `python chat_with_slack.py`
2. ✅ Ask a question in natural language
3. ✅ See Ollama translate and execute
4. ✅ Get conversational results
5. ✅ Keep chatting!

---

**This is what you wanted!** Natural language queries with Ollama, no Claude Desktop required! 🎉