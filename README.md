# Bobager

Bobager is a Slack analysis backend powered by Ollama. It has two supported entrypoints:

- `chat_with_slack.py` for local natural-language chat against Slack data
- `app.main` for a FastAPI backend that a frontend can call later

## What It Does

- Finds people who appear knowledgeable about a topic
- Ranks contributors in a Slack channel
- Runs broader natural-language analysis over matching Slack messages
- Keeps LLM work local through Ollama

## Requirements

- Python 3.11+
- Ollama running locally
- A pulled Ollama model such as `llama2`
- Slack tokens configured in `.env`

## Setup

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Required `.env` values:

```env
SLACK_BOT_TOKEN=
SLACK_APP_TOKEN=
SLACK_SIGNING_SECRET=
SLACK_USER_TOKEN=
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

`SLACK_USER_TOKEN` is needed for Slack search-based queries.

## Run The Chat

```bash
source venv/bin/activate
python chat_with_slack.py
```

Example prompts:

- `I need help with HTML. Who can I go to?`
- `Who mentions devops the most?`
- `Who are the top contributors in engineering?`

## Run The API

```bash
source venv/bin/activate
python -m uvicorn app.main:app --reload
```

Docs will be available at `http://localhost:8000/docs`.

## Tests

```bash
pytest
```

## Project Layout

```text
bobager/
├── app/
│   ├── api/                # FastAPI routes
│   ├── config/             # Settings and env loading
│   ├── models/             # Pydantic schemas
│   ├── services/           # Slack, Ollama, and analysis logic
│   └── utils/              # Cache and logging helpers
├── chat_with_slack.py      # CLI chat entrypoint
├── requirements.txt
├── tests/
├── QUICKSTART.md
└── NATURAL_LANGUAGE_CHAT.md
```

## Notes

- The repo was trimmed to the Slack chat and FastAPI backend surface.
- Generated coverage and cache artifacts are intentionally not kept in the tree.
- Docker files are still present if you want containerization later.
