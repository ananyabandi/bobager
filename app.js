const form = document.getElementById('chatForm');
const messageWindow = document.getElementById('messageWindow');
const userInput = document.getElementById('userInput');

const cannedResponses = [
  'Hello! I am Bobager, your friendly AI helper. How can I assist you today?',
  'I can help you design a chatbot interface, build frontend logic, or prepare integration notes.',
  'For a real AI backend, replace the response logic in app.js with your own API call.',
  'Try asking me about colors, layout, or IBM Bob-inspired themes.',
];

function appendMessage(role, text) {
  const message = document.createElement('div');
  message.className = `message ${role}`;
  message.innerHTML = `<p>${text}</p>`;
  messageWindow.appendChild(message);
  messageWindow.scrollTop = messageWindow.scrollHeight;
}

function getBotResponse(prompt) {
  const lower = prompt.toLowerCase();

  if (lower.includes('color') || lower.includes('theme')) {
    return 'The interface uses a deep blue and violet palette with soft white text, inspired by the icon gradient.';
  }

  if (lower.includes('ibm') || lower.includes('bob')) {
    return 'This layout is designed like IBM Bob with a friendly assistant panel, rounded cards, and a calm voice.';
  }

  return cannedResponses[Math.floor(Math.random() * cannedResponses.length)];
}

form.addEventListener('submit', (event) => {
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

  setTimeout(() => {
    loading.remove();
    appendMessage('assistant', `<strong>Bobager</strong> ${getBotResponse(text)}`);
  }, 900);
});

// Initial welcome messages
appendMessage('assistant', '<strong>Bobager</strong> Hello! I am your AI assistant. Ask me anything about this frontend.');
appendMessage('assistant', 'This chat UI is ready to use. Integrate your backend or adjust the responses in app.js.');
