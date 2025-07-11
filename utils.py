from datetime import datetime, timedelta
import re

BAD_WORDS = ["хуй", "пізд", "єб", "бляд", "сука", "нах", "fuck", "shit"]

def parse_fact_command(text):
    text = text.replace("запам’ятай", "").replace("запамятай", "").strip()
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

def is_obscene(text):
    return any(bad in text for bad in BAD_WORDS)

def taksyst_reply(text, rude=False):
    if rude:
        return "😡 А ти чо такий дерзкий? Я ж з повагою, а ти матюкаєшся!"
    return f"🚖 Та шо я тобі скажу... {text.capitalize()}, як кажуть, як на маршрутці у годину пік."
