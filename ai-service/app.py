from fastapi import FastAPI
import requests

app = FastAPI()

OLLAMA_URL = "http://ollama:11434/api/generate"

SYSTEM_PROMPT = open("prompt.txt").read()

@app.post("/ask")
async def ask_ai(data: dict):
    user_message = data.get("message")

    prompt = f"{SYSTEM_PROMPT}\nUtilisateur: {user_message}\nIA:"

    response = requests.post(OLLAMA_URL, json={
        "model": "phi3-mini",
        "prompt": prompt,
        "stream": False
    })

    result = response.json()

    return {
        "response": result["response"]
    }