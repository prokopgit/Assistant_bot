import openai
import config

openai.api_key = config.OPENAI_API_KEY

async def get_llm_response(prompt: str) -> str:
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Сталася помилка: {e}"
