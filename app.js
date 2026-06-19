const form = document.getElementById('chatForm');
const messageWindow = document.getElementById('messageWindow');
const userInput = document.getElementById('userInput');
const API_HOST = window.location.hostname || 'localhost';
const API_PROTOCOL = window.location.protocol === 'https:' ? 'https:' : 'http:';
const CHAT_ENDPOINT = `${API_PROTOCOL}//${API_HOST}:8000/api/v1/chat`;

function appendMessage(role, text) {
  const message = document.createElement('div');
  message.className = `message ${role}`;
  message.innerHTML = `<p>${text}</p>`;
  messageWindow.appendChild(message);
  messageWindow.scrollTop = messageWindow.scrollHeight;
}

async function askBackend(message) {
  const response = await fetch(CHAT_ENDPOINT, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    let detail = 'Unknown error';
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      // Keep default detail when response is not JSON.
    }
    throw new Error(detail);
  }

  return response.json();
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const text = userInput.value.trim();
  if (!text) return;

  appendMessage('user', text);
  userInput.value = '';
  userInput.focus();

  const loading = document.createElement('div');
  loading.className = 'message assistant';
  loading.innerHTML = '<p><strong>Bobager</strong> typing…</p>';
  messageWindow.appendChild(loading);
  messageWindow.scrollTop = messageWindow.scrollHeight;

  try {
    const payload = await askBackend(text);
    loading.remove();
    appendMessage('assistant', `<strong>Bobager</strong> ${payload.response}`);
  } catch (error) {
    loading.remove();
    appendMessage(
      'assistant',
      `<strong>Bobager</strong> I could not reach the backend chat service (${error.message}). Start it with: <code>python -m uvicorn app.main:app --reload --port 8000</code>`
    );
  }
});

// Initial welcome messages
appendMessage('assistant', '<strong>Bobager</strong> Hello! I am your AI assistant connected to the Bobager backend.');
appendMessage('assistant', 'Ask me about Slack discussions, experts, contributors, or code snippets posted in channels.');
