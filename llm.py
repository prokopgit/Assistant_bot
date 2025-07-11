import config
import httpx

API_KEY = config.GEMINI_API_KEY
MODEL = "models/gemini-1.5-flash"
BASE_URL = f"https://generativelanguage.googleapis.com/v1beta/{MODEL}:generateContent?key={API_KEY}"

async def get_llm_response(prompt: str) -> str:
    headers = {"Content-Type": "application/json"}
    json_data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(BASE_URL, headers=headers, json=json_data)
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"🤖 GPT шось завис... Помилка: {e}"
