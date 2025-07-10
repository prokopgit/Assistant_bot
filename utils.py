from datetime import datetime, timedelta
import re

def parse_fact_command(text):
    text = text.replace("запам’ятай", "").replace("запамятай", "").strip()
    parts = text.split("—")
    if len(parts) != 2:
        parts = text.split("-")
    key = parts[0].strip()
    value = parts[1].strip() if len(parts) > 1 else ""
    return key, value

async def parse_reminder_command(text, user_id):
    pattern = r"нагадай (.*?)(через \d+ хвилин|через \d+ годин|о \d{1,2}:\d{2})"
    match = re.search(pattern, text)
    if not match:
        return None
    body, time_text = match.groups()
    now = datetime.now()
    if "через" in time_text:
        if "хвилин" in time_text:
            mins = int(re.findall(r"\d+", time_text)[0])
            remind_time = now + timedelta(minutes=mins)
        elif "годин" in time_text:
            hrs = int(re.findall(r"\d+", time_text)[0])
            remind_time = now + timedelta(hours=hrs)
    elif "о" in time_text:
        hour, minute = map(int, re.findall(r"\d+", time_text))
        remind_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if remind_time < now:
            remind_time += timedelta(days=1)
    else:
        return None
    return user_id, body.strip(), remind_time
