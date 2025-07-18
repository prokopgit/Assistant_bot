# Файл: llm.py
import config
import httpx
import logging
from utils import get_fallback_response

API_KEY = config.GEMINI_API_KEY
MODEL = "models/gemini-1.5-flash"
BASE_URL = f"https://generativelanguage.googleapis.com/v1beta/{MODEL}:generateContent?key={API_KEY}"

async def get_llm_response(prompt: str) -> str:
    headers = {
        "Content-Type": "application/json"
    }
    json_data = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(BASE_URL, headers=headers, json=json_data)
            
            if response.status_code == 429:
                return "Забагато запитів, спробуйте через хвилину."
            
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
            
    except httpx.TimeoutException:
        logging.warning("Timeout when accessing Gemini API")
        return get_fallback_response(prompt)
    except Exception as e:
        logging.error(f"LLM Error: {str(e)}")
        fallback = get_fallback_response(prompt)
        return fallback if fallback else "⚠️ Технічні труднощі. Спробуйте інше питання."
