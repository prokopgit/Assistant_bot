import config
import httpx
import asyncio

API_KEY = config.GEMINI_API_KEY

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + API_KEY

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

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(BASE_URL, json=json_data, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"⚠️ Помилка Gemini API: {e}"
