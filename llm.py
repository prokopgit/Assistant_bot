import httpx
import config

async def get_llm_response(prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    params = {"key": config.GEMINI_API_KEY}

    async with httpx.AsyncClient() as client:
        r = await client.post(url, headers=headers, params=params, json=payload)
        try:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        except:
            return "⚠️ Сталася помилка при зверненні до AI."
