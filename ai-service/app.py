import os
from fastapi import FastAPI
import requests

app = FastAPI()

OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://ollama:11434") + "/api/generate"
MODEL_NAME = os.getenv("MODEL_NAME", "phi3:mini")
SYSTEM_PROMPT = open("prompt.txt").read()

@app.post("/ask")
async def ask_ai(data: dict):
    user_message = data.get("message")
    prompt = f"{SYSTEM_PROMPT}\nUtilisateur: {user_message}\nIA:"

    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    })

    result = response.json()
    return {
        "response": result["response"]
    }

@app.get("/health")
async def health():
    return {"status": "ok"}