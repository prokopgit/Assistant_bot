import asyncpg
import config
from datetime import datetime

DATABASE_URL = config.DATABASE_URL

async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS facts (
            uid BIGINT,
            key TEXT,
            value TEXT
        );
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            uid BIGINT,
            text TEXT,
            time TIMESTAMP
        );
    """)
    await conn.close()

# ======== ФАКТИ =========

async def save_fact(uid: int, key: str, value: str):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(
        "INSERT INTO facts (uid, key, value) VALUES ($1, $2, $3)",
        uid, key, value
    )
    await conn.close()

async def get_fact(uid: int, key: str):
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow(
        "SELECT value FROM facts WHERE uid = $1 AND key = $2",
        uid, key
    )
    await conn.close()
    return row['value'] if row else None

async def delete_fact(uid: int, key: str):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(
        "DELETE FROM facts WHERE uid = $1 AND key = $2",
        uid, key
    )
    await conn.close()

# ======== НАГАДУВАННЯ =========

async def save_reminder(uid: int, text: str, time: datetime):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(
        "INSERT INTO reminders (uid, text, time) VALUES ($1, $2, $3)",
        uid, text, time
    )
    await conn.close()

async def get_due_reminders():
    conn = await asyncpg.connect(DATABASE_URL)
    now = datetime.utcnow()  # ← Фікс тут
    rows = await conn.fetch(
        "SELECT uid, text FROM reminders WHERE time <= $1",
        now
    )
    await conn.execute(
        "DELETE FROM reminders WHERE time <= $1",
        now
    )
    await conn.close()
    return [(row["uid"], row["text"]) for row in rows]

async def get_user_reminders(uid: int):
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch(
        "SELECT uid, text, time FROM reminders WHERE uid = $1 ORDER BY time ASC",
        uid
    )
    await conn.close()
    return [(row["uid"], row["text"], row["time"]) for row in rows]

async def delete_user_reminder(uid: int, text: str):
    conn = await asyncpg.connect(DATABASE_URL)
    result = await conn.execute(
        "DELETE FROM reminders WHERE uid = $1 AND text = $2",
        uid, text
    )
    await conn.close()
    return "DELETE 1" in result
