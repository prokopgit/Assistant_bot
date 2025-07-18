# Файл: utils.py
from datetime import datetime, timedelta
import re
import random

FALLBACK_RESPONSES = [
    "Це цікаве питання, дайте мені хвилинку подумати...",
    "Зараз перевірю інформацію...",
    "Можливо, варто обговорити це детальніше?",
    "Що ви самі думаєте з цього приводу?"
]

def get_fallback_response(prompt: str) -> str:
    prompt_lower = prompt.lower()
    if any(w in prompt_lower for w in ["привіт", "хай", "hello"]):
        return "Привіт! Як справи?"
    elif "нагадування" in prompt_lower:
        return "Ви можете керувати нагадуваннями через команди /нагадування та /видалити_нагадування"
    elif any(w in prompt_lower for w in ["як справи", "що нового"]):
        return "Все добре! Готовий допомогти вам. А у вас що цікавого?"
    return random.choice(FALLBACK_RESPONSES)

def parse_fact_command(text):
    text = text.replace("запам'ятай", "").replace("запамятай", "").strip()
    if " — " in text:
        key, value = text.split(" — ", 1)
    elif "-" in text:
        key, value = text.split("-", 1)
    else:
        key, value = text, ""
    return key.strip(), value.strip()

def parse_reminder_command(text, uid):
    try:
        match = re.search(r"нагадай (.+) о (\d{1,2}:\d{2})", text.lower())
        if match:
            task = match.group(1)
            time_str = match.group(2)
            now = datetime.now()
            h, m = map(int, time_str.split(":"))
            dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
            if dt < now:
                dt += timedelta(days=1)
            return uid, task, dt
    except:
        return None
