from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import requests

app = FastAPI()

AI_SERVICE_URL = "http://ai-service:5000/ask"

HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Réceptionniste IA</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg: #0d0f14;
      --surface: #161922;
      --border: #252830;
      --accent: #5cffb0;
      --accent2: #3d8eff;
      --text: #e8eaf0;
      --muted: #6b7080;
      --user-bubble: #1e2333;
      --ai-bubble: #131a2a;
    }

    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'DM Sans', sans-serif;
      height: 100dvh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 1rem;
    }

    .wrapper {
      width: 100%;
      max-width: 700px;
      height: 90dvh;
      display: flex;
      flex-direction: column;
      border: 1px solid var(--border);
      border-radius: 1.5rem;
      overflow: hidden;
      background: var(--surface);
      box-shadow: 0 0 60px rgba(92,255,176,0.05);
    }

    header {
      padding: 1.2rem 1.8rem;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      gap: 1rem;
      background: var(--bg);
    }

    .avatar {
      width: 42px; height: 42px;
      border-radius: 50%;
      background: linear-gradient(135deg, var(--accent), var(--accent2));
      display: flex; align-items: center; justify-content: center;
      font-size: 1.2rem;
      flex-shrink: 0;
    }

    .header-info h1 {
      font-family: 'Syne', sans-serif;
      font-size: 1rem;
      font-weight: 700;
      letter-spacing: 0.02em;
    }

    .status {
      display: flex; align-items: center; gap: 6px;
      font-size: 0.75rem;
      color: var(--accent);
    }

    .status-dot {
      width: 7px; height: 7px;
      border-radius: 50%;
      background: var(--accent);
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.3; }
    }

    #messages {
      flex: 1;
      overflow-y: auto;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 1rem;
      scrollbar-width: thin;
      scrollbar-color: var(--border) transparent;
    }

    .msg {
      max-width: 80%;
      padding: 0.8rem 1.1rem;
      border-radius: 1.2rem;
      font-size: 0.92rem;
      line-height: 1.55;
      animation: fadeUp 0.25s ease;
    }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(8px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    .msg.user {
      background: var(--user-bubble);
      border: 1px solid var(--border);
      align-self: flex-end;
      border-bottom-right-radius: 4px;
    }

    .msg.ai {
      background: var(--ai-bubble);
      border: 1px solid #1e2d45;
      align-self: flex-start;
      border-bottom-left-radius: 4px;
      color: #c8e6ff;
    }

    .msg.ai .label {
      font-family: 'Syne', sans-serif;
      font-size: 0.7rem;
      font-weight: 700;
      color: var(--accent);
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin-bottom: 0.4rem;
    }

    .typing {
      display: flex; gap: 5px; align-items: center;
      padding: 0.9rem 1.1rem;
    }

    .typing span {
      width: 7px; height: 7px;
      border-radius: 50%;
      background: var(--muted);
      animation: bounce 1.2s infinite;
    }
    .typing span:nth-child(2) { animation-delay: 0.2s; }
    .typing span:nth-child(3) { animation-delay: 0.4s; }

    @keyframes bounce {
      0%, 80%, 100% { transform: translateY(0); }
      40% { transform: translateY(-6px); background: var(--accent2); }
    }

    footer {
      padding: 1rem 1.2rem;
      border-top: 1px solid var(--border);
      display: flex;
      gap: 0.75rem;
      background: var(--bg);
    }

    input {
      flex: 1;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 0.9rem;
      padding: 0.75rem 1.1rem;
      color: var(--text);
      font-family: 'DM Sans', sans-serif;
      font-size: 0.92rem;
      outline: none;
      transition: border-color 0.2s;
    }

    input:focus { border-color: var(--accent2); }
    input::placeholder { color: var(--muted); }

    button {
      background: linear-gradient(135deg, var(--accent), var(--accent2));
      border: none;
      border-radius: 0.9rem;
      width: 46px; height: 46px;
      cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      flex-shrink: 0;
      transition: opacity 0.2s, transform 0.1s;
    }

    button:hover { opacity: 0.85; }
    button:active { transform: scale(0.95); }

    button svg { width: 18px; height: 18px; fill: #0d0f14; }
  </style>
</head>
<body>
<div class="wrapper">
  <header>
    <div class="avatar">🤖</div>
    <div class="header-info">
      <h1>Réceptionniste IA</h1>
      <div class="status"><div class="status-dot"></div> En ligne</div>
    </div>
  </header>

  <div id="messages">
    <div class="msg ai">
      <div class="label">Réceptionniste</div>
      Bonjour ! Je suis votre réceptionniste virtuel. Comment puis-je vous aider aujourd'hui ?
    </div>
  </div>

  <footer>
    <input type="text" id="input" placeholder="Écrivez votre message…" autocomplete="off" />
    <button onclick="send()">
      <svg viewBox="0 0 24 24"><path d="M2 21l21-9L2 3v7l15 2-15 2v7z"/></svg>
    </button>
  </footer>
</div>

<script>
  const input = document.getElementById('input');
  const messages = document.getElementById('messages');

  input.addEventListener('keydown', e => { if (e.key === 'Enter') send(); });

  function addMsg(text, role) {
    const div = document.createElement('div');
    div.className = 'msg ' + role;
    if (role === 'ai') {
      div.innerHTML = '<div class="label">Réceptionniste</div>' + escHtml(text);
    } else {
      div.textContent = text;
    }
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
    return div;
  }

  function addTyping() {
    const div = document.createElement('div');
    div.className = 'msg ai typing';
    div.id = 'typing';
    div.innerHTML = '<span></span><span></span><span></span>';
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  function removeTyping() {
    const t = document.getElementById('typing');
    if (t) t.remove();
  }

  function escHtml(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  async function send() {
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    addMsg(text, 'user');
    addTyping();
    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      removeTyping();
      addMsg(data.response, 'ai');
    } catch {
      removeTyping();
      addMsg("Erreur de connexion au service IA.", 'ai');
    }
  }
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    message = body.get("message", "")
    try:
        resp = requests.post(AI_SERVICE_URL, json={"message": message}, timeout=60)
        return resp.json()
    except Exception as e:
        return {"response": f"Erreur : {str(e)}"}
