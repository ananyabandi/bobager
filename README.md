# bobager

A static frontend for the Bobager AI chatbot.

## Features

- IBM Bob-inspired chatbot layout
- Blue / purple gradient theme matching the icon
- Included robot icon as `logo.svg`
- Local chat UI ready for backend integration

## Files

- `index.html` — main chatbot UI
- `styles.css` — theme and layout styles
- `app.js` — chat behavior and simulated responses
- `logo.svg` — custom robot icon asset

## Getting started

### Run the chatbot frontend

Open `index.html` in your browser, or serve the folder with a local static server.

Example using Python:

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

### Set up Ollama (Required for AI responses)

1. **Install Ollama** from [ollama.ai](https://ollama.ai)
2. **Start the Ollama server**:
   ```bash
   ollama serve
   ```
3. **Pull a model** (in another terminal):
   ```bash
   ollama pull llama2
   # Or choose another model:
   # ollama pull neural-chat
   # ollama pull mistral
   ```
4. **Configure the model** in `app.js`:
   - Open `app.js` and change `OLLAMA_MODEL` to match the model you pulled
   - The default is `llama2`

The chatbot will now use Ollama to generate responses. If Ollama is unavailable, it falls back to rule-based local responses.

## Configuration

In `app.js`, you can customize:
- `API_URL` — Ollama endpoint (default: `http://localhost:11434/api/generate`)
- `OLLAMA_MODEL` — LLM model name (default: `llama2`)
