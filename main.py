# Файл: main.py
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from llm import get_llm_response
from database import (
    init_db, save_fact, get_fact, delete_fact,
    save_reminder, get_due_reminders,
    get_user_reminders, delete_user_reminder
)
from utils import parse_fact_command, parse_reminder_command, get_fallback_response
import config
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=config.TELEGRAM_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

async def post_daily_content():
    if not config.CHANNEL_ID:
        return
        
    topics = [
        "Цікавий факт дня:",
        "Питання для обговорення:",
        "Новина технологій:"
    ]
    try:
        response = await get_llm_response(f"Придумай короткий {random.choice(topics)}")
        await bot.send_message(config.CHANNEL_ID, response)
    except Exception as e:
        logger.error(f"Failed to post daily content: {e}")

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("👋 Привіт! Я твій персональний асистент. Напиши /help, щоб дізнатися, що я вмію.")

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        "🧠 Я вмію:\n"
        "• Відповідати на питання\n"
        "• Запам'ятовувати факти\n"
        "• Нагадувати про важливе\n"
        "• Створювати обговорення\n\n"
        "💬 Спробуй:\n"
        "• Запам'ятай, моє ім'я — Дмитро\n"
        "• Нагадай купити молоко о 18:00\n"
        "• Що ти знаєш про моє ім'я?\n"
        "• /обговорення — нові теми\n"
        "• /нагадування — список\n"
        "• /видалити_нагадування [текст] — видалити"
    )

@dp.message(Command("обговорення"))
async def start_discussion(message: types.Message):
    try:
        topics = await get_llm_response("Придумай 3 теми для обговорення в чаті")
        await message.answer(f"💬 Давайте обговоримо:\n{topics}")
    except Exception as e:
        logger.error(f"Discussion error: {e}")
        await message.answer("Не вдалося створити теми. Спробуйте пізніше.")

@dp.message(Command("нагадування"))
async def list_reminders(message: types.Message):
    uid = message.from_user.id
    reminders = await get_user_reminders(uid)
    if reminders:
        reply = "🔔 Твої нагадування:\n" + "\n".join(
            [f"• {r[1]} — {r[2].strftime('%Y-%m-%d %H:%M')}" for r in reminders])
    else:
        reply = "📭 У тебе немає активних нагадувань."
    await message.answer(reply)

@dp.message(Command("видалити_нагадування"))
async def delete_reminder(message: types.Message):
    uid = message.from_user.id
    args = message.text.split(maxsplit=1)
    if len(args) == 2:
        deleted = await delete_user_reminder(uid, args[1])
        if deleted:
            await message.answer("🗑️ Нагадування видалено.")
        else:
            await message.answer("⚠️ Не знайшов такого нагадування.")
    else:
        await message.answer("❗ Приклад: /видалити_нагадування купити молоко")

@dp.message()
async def handle_message(message: types.Message):
    text = message.text.lower()
    uid = message.from_user.id

    if text.startswith("запам'ятай") or text.startswith("запамятай"):
        key, value = parse_fact_command(text)
        await save_fact(uid, key, value)
        await message.answer(f"✅ Запам'ятав: {key} — {value}")

    elif text.startswith("що ти знаєш") or text.startswith("як мене") or text.startswith("яка моя"):
        key = text.split("про")[-1].strip()
        value = await get_fact(uid, key)
        if value:
            await message.answer(f"📌 Ти сказав: {key} — {value}")
        else:
            await message.answer("🤔 Я цього не знаю.")

    elif text.startswith("забудь"):
        key = text.split("про")[-1].strip()
        await delete_fact(uid, key)
        await message.answer(f"🗑️ Забув про '{key}'.")

    elif text.startswith("нагадай"):
        rem = await parse_reminder_command(message.text, uid)
        if rem:
            await save_reminder(*rem)
            await message.answer("⏰ Нагадування збережено!")
        else:
            await message.answer("⚠️ Не вдалося розпізнати час для нагадування.")

    else:
        reply = await get_llm_response(message.text)
        await message.answer(reply)

async def notify_reminders():
    due = await get_due_reminders()
    for uid, text in due:
        try:
            await bot.send_message(uid, f"🔔 Нагадую: {text}")
        except Exception as e:
            logger.error(f"Reminder error for {uid}: {e}")

async def main():
    await init_db()
    scheduler.add_job(notify_reminders, 'interval', minutes=1)
    scheduler.add_job(post_daily_content, 'interval', hours=6)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
