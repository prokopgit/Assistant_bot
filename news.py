import httpx
from bs4 import BeautifulSoup
import random

async def get_funny_archaeo_news():
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("https://www.livescience.com/archaeology")
            soup = BeautifulSoup(r.text, "html.parser")
            articles = soup.select("article h3 a")

            if not articles:
                return "😴 Сьогодні археологи нічого не знайшли, всі копають мовчки."

            article = random.choice(articles)
            title = article.get_text(strip=True)
            link = article["href"]
            if not link.startswith("http"):
                link = "https://www.livescience.com" + link

            # Стиль таксиста
            return (
                f"🗿 <b>Архео-новина від дяді Моргана</b>\n\n"
                f"Ото щойно викопали щось цікаве: <b>{title}</b>.\n"
                f"Я б сам туди поїхав із совком і пивком, якби не спина...\n"
                f"👉 <a href='{link}'>Читайте самі, бо я вже в дорозі!</a>"
            )
    except Exception as e:
        return f"⚠️ Новин не буде — щось пішло не так: {e}"
