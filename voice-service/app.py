from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
import requests
import tempfile
import os
from faster_whisper import WhisperModel
from gtts import gTTS

app = FastAPI()

AI_SERVICE_URL = "http://ai-service:5000/ask"

# Chargement du modèle Whisper (tiny = léger, base = meilleur)
whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")

HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Réceptionniste IA – Vocal</title>
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
      gap: 2rem;
    }

    h1 {
      font-family: 'Syne', sans-serif;
      font-size: 1.4rem;
      font-weight: 800;
      letter-spacing: 0.02em;
    }

    .orb {
      width: 120px; height: 120px;
      border-radius: 50%;
      background: radial-gradient(circle at 35% 35%, var(--accent2), #0a1628);
      box-shadow: 0 0 40px rgba(61,142,255,0.3);
      cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      font-size: 2.5rem;
      transition: transform 0.15s, box-shadow 0.2s;
      user-select: none;
    }

    .orb:hover { transform: scale(1.05); box-shadow: 0 0 60px rgba(61,142,255,0.5); }
    .orb.recording {
      animation: recordPulse 1s infinite;
      background: radial-gradient(circle at 35% 35%, #ff4d6d, #2a0010);
      box-shadow: 0 0 60px rgba(255,77,109,0.5);
    }

    @keyframes recordPulse {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.08); }
    }

    .status {
      font-size: 0.85rem;
      color: var(--muted);
      min-height: 1.2em;
    }

    .transcript-box {
      width: 340px;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 1rem;
      padding: 1rem 1.2rem;
      font-size: 0.9rem;
      line-height: 1.55;
      color: var(--text);
      min-height: 60px;
      display: none;
    }

    .transcript-box.visible { display: block; animation: fadeUp 0.2s ease; }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(6px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    .label {
      font-family: 'Syne', sans-serif;
      font-size: 0.68rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin-bottom: 0.4rem;
    }

    .label.user { color: var(--accent); }
    .label.ai   { color: var(--accent2); }

    audio { display: none; }
  </style>
</head>
<body>
  <h1>🎙 Réceptionniste Vocal</h1>

  <div class="orb" id="orb" onclick="toggleRecord()">🎤</div>
  <div class="status" id="status">Appuyez pour parler</div>

  <div class="transcript-box" id="userBox">
    <div class="label user">Vous</div>
    <div id="userText"></div>
  </div>

  <div class="transcript-box" id="aiBox">
    <div class="label ai">Réceptionniste</div>
    <div id="aiText"></div>
  </div>

  <audio id="audioPlayer" autoplay></audio>

<script>
  let mediaRecorder, chunks = [], recording = false;

  async function toggleRecord() {
    if (!recording) await startRecord();
    else stopRecord();
  }

  async function startRecord() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    chunks = [];
    mediaRecorder.ondataavailable = e => chunks.push(e.data);
    mediaRecorder.start();
    recording = true;
    document.getElementById('orb').classList.add('recording');
    document.getElementById('status').textContent = 'Enregistrement… Appuyez pour arrêter';
  }

  function stopRecord() {
    mediaRecorder.stop();
    recording = false;
    document.getElementById('orb').classList.remove('recording');
    document.getElementById('status').textContent = 'Traitement en cours…';

    mediaRecorder.onstop = async () => {
      const blob = new Blob(chunks, { type: 'audio/webm' });
      const fd = new FormData();
      fd.append('audio', blob, 'recording.webm');

      try {
        const res = await fetch('/voice', { method: 'POST', body: fd });
        const data = await res.json();

        document.getElementById('userText').textContent = data.transcript || '(non reconnu)';
        document.getElementById('aiText').textContent = data.response || '';
        document.getElementById('userBox').classList.add('visible');
        document.getElementById('aiBox').classList.add('visible');

        if (data.audio_url) {
          document.getElementById('audioPlayer').src = data.audio_url;
        }

        document.getElementById('status').textContent = 'Appuyez pour parler';
      } catch {
        document.getElementById('status').textContent = 'Erreur – réessayez';
      }
    };
  }
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML

@app.post("/voice")
async def voice(audio: UploadFile = File(...)):
    # Sauvegarde du fichier audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    # Transcription STT avec Whisper
    try:
        segments, _ = whisper_model.transcribe(tmp_path, language="fr")
        transcript = " ".join(seg.text for seg in segments).strip()
    except Exception as e:
        os.unlink(tmp_path)
        return {"transcript": "", "response": f"Erreur STT : {str(e)}"}

    os.unlink(tmp_path)

    if not transcript:
        return {"transcript": "", "response": "Je n'ai pas compris, pouvez-vous répéter ?"}

    # Envoi à l'AI service
    try:
        ai_resp = requests.post(AI_SERVICE_URL, json={"message": transcript}, timeout=60)
        response_text = ai_resp.json().get("response", "")
    except Exception as e:
        return {"transcript": transcript, "response": f"Erreur IA : {str(e)}"}

    # TTS avec gTTS
    tts_path = tempfile.mktemp(suffix=".mp3")
    try:
        tts = gTTS(text=response_text, lang="fr")
        tts.save(tts_path)
        # Stocker le chemin pour le servir
        app.state.last_tts = tts_path
        audio_url = "/audio"
    except Exception:
        audio_url = None

    return {
        "transcript": transcript,
        "response": response_text,
        "audio_url": audio_url
    }

@app.get("/audio")
async def get_audio():
    path = getattr(app.state, "last_tts", None)
    if path and os.path.exists(path):
        return FileResponse(path, media_type="audio/mpeg")
    return {"error": "Pas d'audio disponible"}
