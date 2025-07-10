import config
import httpx
import asyncio

API_KEY = config.GEMINI_API_KEY

BASE_URL = "https://gemini.api.url/v1/chat/completions"  # Заміни на актуальний URL Gemini API

async def get_llm_response(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "gemini-1.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(BASE_URL, json=json_data, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"⚠️ Помилка Gemini API: {e}"
