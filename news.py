import httpx
from bs4 import BeautifulSoup
import random

async def get_funny_archaeo_news():
    try:
        url = "https://www.archaeology.org/news"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            headlines = soup.select("h3 a")

            if not headlines:
                return "🦴 Сьогодні новин немає — тиша, як у кургані."

            item = random.choice(headlines[:5])
            title = item.text.strip()
            link = item.get("href")

            funny_intro = random.choice([
                "📯 Поки ти копав яму — ось що трапилось:",
                "🔍 Археологи не сплять! Ось свіженьке:",
                "🤣 Знайшли щось цікавіше за твої тапки:",
                "🏺 Прямо з розкопок — новинка:",
            ])

            return f"{funny_intro}\n\n<b>{title}</b>\n<a href='{link}'>Читати далі</a>"

    except Exception as e:
        return f"⚠️ Шось пішло не так із новинами: {e}"
