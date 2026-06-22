const form = document.getElementById('chatForm');
const messageWindow = document.getElementById('messageWindow');
const userInput = document.getElementById('userInput');
const API_HOST = window.location.hostname || 'localhost';
const API_PROTOCOL = window.location.protocol === 'https:' ? 'https:' : 'http:';
const CHAT_ENDPOINT = `${API_PROTOCOL}//${API_HOST}:8000/api/v1/chat`;

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function formatMessageText(text) {
  const escaped = escapeHtml(text.trim());
  const blocks = escaped.split(/\n{2,}/).filter(Boolean);

  return blocks.map((block) => {
    const lines = block.split('\n').map((line) => line.trim()).filter(Boolean);
    const isList = lines.every((line) => /^[-*]\s+/.test(line));

    if (isList) {
      const items = lines
        .map((line) => `<li>${formatInlineMarkdown(line.replace(/^[-*]\s+/, ''))}</li>`)
        .join('');
      return `<ul>${items}</ul>`;
    }

    const headingMatch = block.match(/^#{2,3}\s+(.+)$/);
    if (headingMatch) {
      return `<p class="message-heading">${formatInlineMarkdown(headingMatch[1])}</p>`;
    }

    return `<p>${formatInlineMarkdown(lines.join(' '))}</p>`;
  }).join('');
}

function formatInlineMarkdown(text) {
  return text
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
}

function appendMessage(role, text, options = {}) {
  const message = document.createElement('div');
  message.className = `message ${role}`;
  const content = document.createElement('div');
  content.className = 'message-content';
  content.innerHTML = options.html ? text : formatMessageText(text);
  message.appendChild(content);
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
    appendMessage('assistant', `**Bobager**\n\n${payload.response}`);
  } catch (error) {
    loading.remove();
    appendMessage(
      'assistant',
      `**Bobager**\n\nI could not reach the backend chat service (${error.message}). Start it with: \`python -m uvicorn app.main:app --reload --port 8000\``
    );
  }
});

// Initial welcome messages
appendMessage('assistant', '**Bobager**\n\nHello! I am your AI assistant connected to both Slack and GitHub.');
appendMessage('assistant', '**Bobager**\n\n**Slack Questions:** Ask about workspace discussions, experts, contributors, or code snippets. Example: "Who are experts in React?"');
appendMessage('assistant', '**Bobager**\n\n**GitHub Questions:** Ask about repositories, files, commits, and issues. Example: "Search for AI repositories" or "Show me facebook/react/README.md"');
