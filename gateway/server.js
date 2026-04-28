const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();

// Route /chat et /voice/* → services correspondants
app.use('/chat', createProxyMiddleware({
  target: 'http://chat-service:5001',
  changeOrigin: true,
  pathRewrite: { '^/chat': '' }
}));

app.use('/voice', createProxyMiddleware({
  target: 'http://voice-service:5002',
  changeOrigin: true,
  pathRewrite: { '^/voice': '' }
}));

app.use('/audio', createProxyMiddleware({
  target: 'http://voice-service:5002',
  changeOrigin: true
}));

// Page d'accueil du portail
app.get('/', (req, res) => {
  res.send(`
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Réceptionniste IA</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg: #0d0f14; --surface: #161922; --border: #252830;
      --accent: #5cffb0; --accent2: #3d8eff; --text: #e8eaf0; --muted: #6b7080;
    }
    body {
      background: var(--bg); color: var(--text);
      font-family: 'DM Sans', sans-serif;
      min-height: 100dvh;
      display: flex; flex-direction: column;
      align-items: center; justify-content: center; gap: 3rem;
    }
    .logo { font-family: 'Syne', sans-serif; font-size: 2.2rem; font-weight: 800; letter-spacing: -0.01em; }
    .logo span { color: var(--accent); }
    .subtitle { color: var(--muted); font-size: 0.95rem; }
    .cards { display: flex; gap: 1.5rem; flex-wrap: wrap; justify-content: center; }
    .card {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 1.5rem; padding: 2rem 2.5rem;
      text-align: center; text-decoration: none; color: var(--text);
      width: 200px; transition: border-color 0.2s, transform 0.15s, box-shadow 0.2s;
      display: flex; flex-direction: column; gap: 1rem; align-items: center;
    }
    .card:hover { border-color: var(--accent2); transform: translateY(-4px); box-shadow: 0 12px 40px rgba(61,142,255,0.15); }
    .card-icon { font-size: 2.5rem; }
    .card-title { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 1rem; }
    .card-desc { color: var(--muted); font-size: 0.8rem; }
  </style>
</head>
<body>
  <div>
    <div class="logo">Récep<span>IA</span></div>
    <p class="subtitle">Votre réceptionniste virtuel intelligent</p>
  </div>
  <div class="cards">
    <a class="card" href="/chat">
      <div class="card-icon">💬</div>
      <div class="card-title">Chat</div>
      <div class="card-desc">Discutez par écrit avec le réceptionniste</div>
    </a>
    <a class="card" href="/voice">
      <div class="card-icon">🎙</div>
      <div class="card-title">Vocal</div>
      <div class="card-desc">Parlez directement à voix haute</div>
    </a>
  </div>
</body>
</html>
  `);
});

app.listen(3000, () => {
  console.log('Gateway démarrée sur le port 3000');
});
