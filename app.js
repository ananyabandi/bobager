const form = document.getElementById('chatForm');
const messageWindow = document.getElementById('messageWindow');
const userInput = document.getElementById('userInput');

// Ollama API endpoint and model configuration
const API_URL = 'http://localhost:11434/api/generate';
const OLLAMA_MODEL = 'llama2'; // Change this to your preferred Ollama model (e.g., 'neural-chat', 'mistral')
const repoFiles = ['README.md', 'index.html', 'styles.css', 'app.js'];
const repoContent = {};
let repoLoaded = false;
const githubCache = {};
let activeGithubData = null;
let activeGithubRepo = null;

function appendMessage(role, text) {
  const message = document.createElement('div');
  message.className = `message ${role}`;
  message.innerHTML = `<p>${text}</p>`;
  messageWindow.appendChild(message);
  messageWindow.scrollTop = messageWindow.scrollHeight;
}

function normalize(text) {
  return text.trim().replace(/\s+/g, ' ').toLowerCase();
}

function summarizeRepo() {
  const files = Object.keys(repoContent).join(', ');
  return `I am analyzing the local repository. I have loaded the following files: ${files}. Ask about a file path or repository behavior.`;
}

function getFileContent(fileName) {
  const key = fileName.toLowerCase();
  return repoContent[key] || null;
}

function getFileSnippet(fileName, contentOverride) {
  const content = contentOverride || getFileContent(fileName);
  if (!content) {
    return `I could not find ${fileName} in the local repository.`;
  }

  const lines = content.split('\n').slice(0, 40);
  return `Contents of ${fileName}:\n\n${lines.join('\n')}`;
}

function extractExplicitFileName(prompt, files) {
  const lower = normalize(prompt);
  const explicitMatch = lower.match(/(?:show|open|read|display|get)(?:\s+(?:the|a|my|this|repo|remote|local))?(?:\s+me)?\s+(.+)$/);
  const target = explicitMatch ? explicitMatch[1].trim() : null;
  if (!target) return null;

  const cleanTarget = target
    .replace(/^\.?\//, '')
    .replace(/(?:\s+from\s+.*|\s+in\s+.*|\s+file|\s+document|\s+script|\s+please)$/g, '')
    .replace(/[?.!]$/, '')
    .trim();

  if (!cleanTarget) {
    return null;
  }

  const exact = files.find((file) => file.toLowerCase() === cleanTarget.toLowerCase());
  if (exact) return exact;

  const tokens = cleanTarget.split(/\s+/).filter(Boolean);
  for (const token of tokens.reverse()) {
    const match = files.find((file) => file.toLowerCase() === token.toLowerCase());
    if (match) return match;
    const pathMatch = files.find((file) => file.toLowerCase().endsWith('/' + token.toLowerCase()));
    if (pathMatch) return pathMatch;
  }

  const endMatch = files.find((file) => {
    const f = file.toLowerCase();
    const c = cleanTarget.toLowerCase();
    return f === c || f.endsWith('/' + c) || f.endsWith(c);
  });
  return endMatch || null;
}

function isExplicitFileRequest(prompt) {
  const lower = normalize(prompt);
  return /(?:show|open|read|display|get)(?:\s+(?:the|a|my|this|repo|remote|local))?(?:\s+me)?\s+/.test(lower);
}

function searchRepo(prompt) {
  const terms = normalize(prompt).split(/\s+/).filter(Boolean);
  const scores = repoFiles.map((file) => {
    const content = getFileContent(file);
    if (!content) return { file, score: 0 };
    const norm = normalize(content);
    const score = terms.reduce((sum, term) => sum + (norm.includes(term) ? 1 : 0), 0);
    return { file, score };
  });

  scores.sort((a, b) => b.score - a.score);
  const top = scores[0];
  if (!top || top.score === 0) {
    return null;
  }

  const content = getFileContent(top.file).split('\n').slice(0, 25).join('\n');
  return `I found relevant information in ${top.file}:\n\n${content}`;
}

function parseGithubRepo(prompt) {
  const githubUrl = prompt.match(/github\.com\/(?:@?)([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+)/i);
  if (githubUrl) {
    return { owner: githubUrl[1], repo: githubUrl[2] };
  }
  const ownerRepo = prompt.match(/([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+)/);
  if (ownerRepo) {
    return { owner: ownerRepo[1], repo: ownerRepo[2] };
  }
  return null;
}

function getGithubCacheKey(owner, repo) {
  return `${owner.toLowerCase()}/${repo.toLowerCase()}`;
}

async function fetchGithubFile(owner, repo, file, branch = 'main') {
  const url = `https://raw.githubusercontent.com/${owner}/${repo}/${branch}/${file}`;
  try {
    const response = await fetch(url);
    if (!response.ok) {
      return null;
    }
    return await response.text();
  } catch (error) {
    return null;
  }
}

async function loadGithubRepo(owner, repo) {
  const key = getGithubCacheKey(owner, repo);
  if (githubCache[key]) {
    return githubCache[key];
  }

  const filesToTry = [
    'README.md', 'package.json', 'index.html', 'styles.css', 'app.js',
    'src/app.js', 'src/index.js', 'src/main.js',
    'client/app.js', 'client/index.js',
    'public/index.html', 'src/styles.css'
  ];
  const content = {};

  for (const file of filesToTry) {
    let text = await fetchGithubFile(owner, repo, file, 'main');
    if (text === null) {
      text = await fetchGithubFile(owner, repo, file, 'master');
    }
    if (text !== null) {
      content[file.toLowerCase()] = text;
    }
  }

  const loaded = Object.keys(content).length > 0;
  githubCache[key] = { owner, repo, content, loaded };
  return githubCache[key];
}

function getGithubSnippet(fileName, githubData) {
  const content = githubData.content[fileName.toLowerCase()];
  if (!content) {
    return `I could not find ${fileName} in the remote repository ${githubData.owner}/${githubData.repo}.`;
  }

  const lines = content.split('\n').slice(0, 40);
  return `Contents of ${fileName} from ${githubData.owner}/${githubData.repo}:\n\n${lines.join('\n')}`;
}

function searchGithubRepo(prompt, githubData) {
  const terms = normalize(prompt).split(/\s+/).filter(Boolean);
  const scores = Object.keys(githubData.content).map((file) => {
    const content = githubData.content[file];
    const norm = normalize(content);
    const score = terms.reduce((sum, term) => sum + (norm.includes(term) ? 1 : 0), 0);
    return { file, score };
  });

  scores.sort((a, b) => b.score - a.score);
  const top = scores[0];
  if (!top || top.score === 0) {
    return null;
  }

  const content = githubData.content[top.file].split('\n').slice(0, 25).join('\n');
  return `I found relevant information in ${top.file} from ${githubData.owner}/${githubData.repo}:\n\n${content}`;
}

function summarizeGithubRepo(githubData) {
  const files = Object.keys(githubData.content).join(', ');
  return `I loaded the remote GitHub repository ${githubData.owner}/${githubData.repo}. Available files: ${files}. Ask about a file or request a summary.`;
}

async function answerGithubPrompt(prompt) {
  const repoInfo = parseGithubRepo(prompt);
  if (!repoInfo) {
    return null;
  }

  const githubData = await loadGithubRepo(repoInfo.owner, repoInfo.repo);
  if (!githubData.loaded) {
    return `I could not load the remote repository ${repoInfo.owner}/${repoInfo.repo}. Make sure the owner and repository name are correct.`;
  }

  activeGithubData = githubData;
  activeGithubRepo = `${repoInfo.owner}/${repoInfo.repo}`;

  const lower = normalize(prompt);
  if (lower.includes('summary') || lower.includes('overview') || lower.includes('describe')) {
    return summarizeGithubRepo(githubData);
  }

  const explicitFile = extractExplicitFileName(prompt, Object.keys(githubData.content));
  if (explicitFile) {
    return getGithubSnippet(explicitFile, githubData);
  }

  if (isExplicitFileRequest(prompt)) {
    const availableFiles = Object.keys(githubData.content).map(f => f.split('/').pop()).join(', ');
    return `I could not find the exact file requested in ${githubData.owner}/${githubData.repo}. Available files: ${availableFiles}.`;
  }

  const fileMatch = Object.keys(githubData.content).find((file) => lower.includes(file.toLowerCase()));
  if (fileMatch && (lower.includes('show') || lower.includes('open') || lower.includes('read') || lower.includes('content'))) {
    return getGithubSnippet(fileMatch, githubData);
  }

  const searchResult = searchGithubRepo(prompt, githubData);
  if (searchResult) {
    return searchResult;
  }

  return `I loaded remote repository ${githubData.owner}/${githubData.repo}. Ask me for README.md, app.js, styles.css, or index.html.`;
}

async function answerFromRepo(prompt) {
  const lower = normalize(prompt);

  if (!repoLoaded) {
    return 'Repository is still loading. Please try again in a moment.';
  }

  if (lower.includes('repo') || lower.includes('repository')) {
    if (lower.includes('summary') || lower.includes('overview') || lower.includes('describe')) {
      return summarizeRepo();
    }
  }

  const explicitFile = extractExplicitFileName(prompt, repoFiles);
  if (explicitFile) {
    return getFileSnippet(explicitFile);
  }

  if (isExplicitFileRequest(prompt)) {
    return 'I could not find the exact file requested in the local repository. Try another file name or ask for a different path.';
  }

  const fileMatch = repoFiles.find((file) => lower.includes(file.toLowerCase()));
  if (fileMatch) {
    if (lower.includes('show') || lower.includes('open') || lower.includes('read') || lower.includes('content')) {
      return getFileSnippet(fileMatch);
    }
  }

  if (lower.startsWith('show me') || lower.startsWith('open') || lower.startsWith('read')) {
    const tokens = lower.split(/\s+/);
    const path = tokens.slice(-1)[0];
    const file = repoFiles.find((name) => name.toLowerCase() === path);
    if (file) {
      return getFileSnippet(file);
    }
  }

  const searchResult = searchRepo(prompt);
  if (searchResult) {
    return searchResult;
  }

  return 'I can answer questions about the repository files in this folder. Try asking for index.html, styles.css, app.js, or README.md.';
}

async function loadRepo() {
  const loads = repoFiles.map(async (file) => {
    try {
      const response = await fetch(`./${file}`);
      if (!response.ok) {
        return;
      }
      const text = await response.text();
      repoContent[file.toLowerCase()] = text;
    } catch (error) {
      console.warn('Failed to load repo file', file, error);
    }
  });

  await Promise.all(loads);
  repoLoaded = Object.keys(repoContent).length > 0;
}

async function answerActiveGithubPrompt(prompt) {
  if (!activeGithubData) {
    return null;
  }

  const lower = normalize(prompt);
  if (lower.includes('summary') || lower.includes('overview') || lower.includes('describe') || lower.includes('summarize')) {
    return summarizeGithubRepo(activeGithubData);
  }

  const explicitFile = extractExplicitFileName(prompt, Object.keys(activeGithubData.content));
  if (explicitFile) {
    return getGithubSnippet(explicitFile, activeGithubData);
  }

  if (isExplicitFileRequest(prompt)) {
    const availableFiles = Object.keys(activeGithubData.content).map(f => f.split('/').pop()).join(', ');
    return `I could not find the exact file requested in ${activeGithubRepo}. Available files: ${availableFiles}.`;
  }

  const fileMatch = Object.keys(activeGithubData.content).find((file) => lower.includes(file.toLowerCase()));
  if (fileMatch && (lower.includes('show') || lower.includes('open') || lower.includes('read') || lower.includes('content'))) {
    return getGithubSnippet(fileMatch, activeGithubData);
  }

  const searchResult = searchGithubRepo(prompt, activeGithubData);
  if (searchResult) {
    return searchResult;
  }

  return null;
}

async function getLocalResponse(prompt) {
  const lower = prompt.toLowerCase();
  const githubRepoInfo = parseGithubRepo(prompt);

  if (githubRepoInfo) {
    return await answerGithubPrompt(prompt);
  }

  if (activeGithubData) {
    const githubAnswer = await answerActiveGithubPrompt(prompt);
    if (githubAnswer) {
      return githubAnswer;
    }
  }

  if (activeGithubData) {
    const githubAnswer = await answerActiveGithubPrompt(prompt);
    if (githubAnswer) {
      return githubAnswer;
    }
  }

  if (lower.includes('analyze') || lower.includes('repository') || lower.includes('repo') || lower.includes('file')) {
    return await answerFromRepo(prompt);
  }

  if (lower.includes('color') || lower.includes('theme')) {
    return 'This frontend uses a bold blue-to-purple palette with dark UI surfaces and clean rounded cards.';
  }

  if (lower.includes('logo') || lower.includes('icon')) {
    return 'The logo is loaded from logo.png, and the avatar card uses a solid dark background so it stands out.';
  }

  if (lower.includes('ibm') || lower.includes('bob')) {
    return 'The interface is modeled after IBM Bob with a calm chat panel, fresh rounded cards, and a modern assistant feel.';
  }

  if (lower.includes('help')) {
    return 'Ask me anything about the chat UI, repository files, or how to run the app locally.';
  }

  const cannedResponses = [
    'Hello! I am Bobager, your friendly AI helper. How can I assist you today?',
    'I can help you analyze the local repository or answer questions about the frontend files.',
    'Try asking about index.html, styles.css, app.js, or README.md.',
    'Ask me to show you a file or summarize the repository.',
  ];

  return cannedResponses[Math.floor(Math.random() * cannedResponses.length)];
}

async function getBotResponse(prompt) {
  if (!API_URL) {
    return await getLocalResponse(prompt);
  }

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        model: OLLAMA_MODEL,
        prompt: prompt,
        stream: false
      }),
    });

    if (!response.ok) {
      console.warn('Ollama API returned error status:', response.status);
      return await getLocalResponse(prompt);
    }

    const data = await response.json();
    return data.response || await getLocalResponse(prompt);
  } catch (error) {
    console.error('Error calling Ollama API:', error);
    console.warn('Falling back to local rule-based responses.');
    return await getLocalResponse(prompt);
  }
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

  const response = await getBotResponse(text);
  loading.remove();
  appendMessage('assistant', `<strong>Bobager</strong> ${response}`);
});

// Initial welcome messages
appendMessage('assistant', '<strong>Bobager</strong> Hello! I am your local assistant.');
appendMessage('assistant', 'Ask me anything about the repository files or the frontend UI.');

loadRepo();
