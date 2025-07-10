import asyncpg
import config

_pool = None

async def init_db():
    global _pool
    _pool = await asyncpg.create_pool(config.DATABASE_URL)

async def save_fact(uid, key, value):
    async with _pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO facts (uid, key, value)
            VALUES ($1, $2, $3)
            ON CONFLICT (uid, key) DO UPDATE SET value = $3
        """, uid, key, value)

async def get_fact(uid, key):
    async with _pool.acquire() as conn:
        row = await conn.fetchrow("SELECT value FROM facts WHERE uid=$1 AND key=$2", uid, key)
        return row['value'] if row else None

async def delete_fact(uid, key):
    async with _pool.acquire() as conn:
        await conn.execute("DELETE FROM facts WHERE uid=$1 AND key=$2", uid, key)

async def save_reminder(uid, text, time):
    async with _pool.acquire() as conn:
        await conn.execute("INSERT INTO reminders (uid, text, time) VALUES ($1, $2, $3)", uid, text, time)

async def get_due_reminders():
    async with _pool.acquire() as conn:
        return await conn.fetch("SELECT uid, text FROM reminders WHERE time <= now()")

async def get_user_reminders(uid):
    async with _pool.acquire() as conn:
        return await conn.fetch("SELECT id, text, time FROM reminders WHERE uid=$1", uid)

async def delete_user_reminder(uid, text):
    async with _pool.acquire() as conn:
        result = await conn.execute("DELETE FROM reminders WHERE uid=$1 AND text=$2", uid, text)
        return "DELETE" in result
