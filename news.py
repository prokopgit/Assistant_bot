import httpx
from bs4 import BeautifulSoup
import random
import re

async def get_funny_archaeo_news():
    try:
        url = "https://www.archaeology.org/news"  # або інше джерело
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            headlines = soup.select("h3 a")

            if not headlines:
                return "🦴 Сьогодні в новинах — тиша, як у кургані. Всі в полі."

            item = random.choice(headlines[:5])
            title = item.text.strip()
            link = item.get("href")

            funny_intro = random.choice([
                "📯 Поки ти копав яму — сталося ось що:",
                "🔍 Археологи не сплять! Ось новинка:",
                "🤣 Знайшли щось цікавіше за твої тапки:",
                "🏺 Прямо з розкопок — свіжа байка:",
            ])

            return f"{funny_intro}\n\n<b>{title}</b>\n<a href='{link}'>Читати далі</a>"

    except Exception as e:
        return f"⚠️ Шось пішло не так з новинами: {e}"
