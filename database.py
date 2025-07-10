import asyncpg
import config
from datetime import datetime, timezone

conn = None

async def init_db():
    global conn
    conn = await asyncpg.connect(config.DATABASE_URL)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS user_facts (
            user_id BIGINT,
            key TEXT,
            value TEXT
        );
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            text TEXT,
            remind_at TIMESTAMPTZ
        );
    """)

async def save_fact(user_id, key, value):
    await conn.execute("INSERT INTO user_facts VALUES ($1, $2, $3)", user_id, key, value)

async def get_fact(user_id, key):
    row = await conn.fetchrow("SELECT value FROM user_facts WHERE user_id = $1 AND key = $2", user_id, key)
    return row["value"] if row else None

async def delete_fact(user_id, key):
    await conn.execute("DELETE FROM user_facts WHERE user_id = $1 AND key = $2", user_id, key)

async def save_reminder(user_id, text, remind_at):
    await conn.execute("INSERT INTO reminders (user_id, text, remind_at) VALUES ($1, $2, $3)", user_id, text, remind_at)

async def get_due_reminders():
    now = datetime.now(timezone.utc)
    rows = await conn.fetch("DELETE FROM reminders WHERE remind_at <= $1 RETURNING user_id, text", now)
    return [(r["user_id"], r["text"]) for r in rows]

async def get_user_reminders(user_id):
    rows = await conn.fetch("SELECT id, text, remind_at FROM reminders WHERE user_id = $1", user_id)
    return [(r["id"], r["text"], r["remind_at"]) for r in rows]

async def delete_user_reminder(user_id, keyword):
    row = await conn.fetchrow("DELETE FROM reminders WHERE user_id = $1 AND text ILIKE '%' || $2 || '%' RETURNING id", user_id, keyword)
    return row is not None
