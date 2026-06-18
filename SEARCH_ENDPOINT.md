# Search Endpoint Documentation

## Overview
The `/api/v1/search` endpoint searches all Slack channels for messages about a specific topic and provides a natural language analysis of who discussed it the most.

## Endpoint Details

**URL:** `POST /api/v1/search`

**Content-Type:** `application/json`

## Request Body

```json
{
  "query": "pizza",
  "timeframe_days": 30,
  "channels": ["general", "random"]
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Topic or keyword to search for (e.g., "pizza", "React", "deployment") |
| `timeframe_days` | integer | No | 30 | Number of days to look back (1-365) |
| `channels` | array[string] | No | null | Specific channels to search. If null, searches all channels |

## Response

```json
{
  "query": "pizza",
  "answer": "Based on 50 messages, John (15 messages) and Sarah (12 messages) talked about pizza the most. John primarily discussed different pizza toppings and his favorite local pizzerias, while Sarah focused on pizza delivery services and comparing prices. Mike also contributed 8 messages, mainly about making homemade pizza dough.",
  "total_messages_found": 50,
  "timeframe_days": 30,
  "channels_searched": ["general", "random"],
  "timestamp": "2026-06-18T22:45:00Z"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `query` | string | The search query that was used |
| `answer` | string | Natural language answer about who discussed the topic |
| `total_messages_found` | integer | Total number of messages found matching the query |
| `timeframe_days` | integer | Number of days that were searched |
| `channels_searched` | array[string] or null | Channels that were searched |
| `timestamp` | string | ISO 8601 timestamp of when the analysis was performed |

## Example Usage

### cURL

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/search' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "pizza",
  "timeframe_days": 30,
  "channels": null
}'
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/search",
    json={
        "query": "pizza",
        "timeframe_days": 30,
        "channels": None
    }
)

result = response.json()
print(result["answer"])
```

### JavaScript

```javascript
const response = await fetch('http://localhost:8000/api/v1/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'pizza',
    timeframe_days: 30,
    channels: null
  })
});

const result = await response.json();
console.log(result.answer);
```

## How It Works

1. **Search Phase**: The endpoint uses Slack's search API to find all messages containing the query term across specified channels (or all channels if none specified)

2. **Data Aggregation**: Messages are grouped by user, counting how many times each person mentioned the topic

3. **AI Analysis**: Ollama (LLM) analyzes the messages to:
   - Identify who talked about the topic most
   - Understand what aspects they focused on
   - Detect patterns and insights
   - Generate a natural, conversational answer

4. **Caching**: Results are cached to improve performance for repeated queries

## Use Cases

- **"Who knows about X?"** - Find subject matter experts
  ```json
  {"query": "kubernetes deployment"}
  ```

- **"Who's interested in Y?"** - Identify interested parties
  ```json
  {"query": "machine learning"}
  ```

- **"Who discussed Z?"** - Track conversations
  ```json
  {"query": "Q4 planning"}
  ```

## Error Responses

### 500 Internal Server Error

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common causes:
- Slack API connection issues
- Missing user token (required for search API)
- Ollama service unavailable
- Invalid channel names

## Requirements

- **Slack User Token**: This endpoint requires a Slack user token (xoxp-) with `search:read` scope
- **Ollama**: Must have Ollama running locally or accessible at configured URL
- **Model**: Default model is `llama2`, configurable via `OLLAMA_MODEL` environment variable

## Performance Notes

- First request may take 30-60 seconds as Ollama analyzes the messages
- Subsequent identical requests are served from cache (default: 1 hour TTL)
- Large result sets (100+ messages) may take longer to process
- Consider using specific channels to narrow search scope for faster results

## Tips

1. **Be specific**: Use specific terms for better results
   - Good: "React hooks performance"
   - Less good: "React"

2. **Use channels**: Narrow search to relevant channels
   ```json
   {"query": "deployment", "channels": ["devops", "engineering"]}
   ```

3. **Adjust timeframe**: Recent discussions may be more relevant
   ```json
   {"query": "bug fix", "timeframe_days": 7}
   ```

4. **Clear cache**: Use `/api/v1/cache/clear` to force fresh analysis