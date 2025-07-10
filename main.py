import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from llm import get_llm_response
from database import (
    init_db, save_fact, get_fact, delete_fact,
    save_reminder, get_due_reminders,
    get_user_reminders, delete_user_reminder
)
from utils import parse_fact_command, parse_reminder_command
import config

bot = Bot(token=config.TELEGRAM_TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("👋 Привіт! Я твій персональний асистент. Напиши /help, щоб дізнатися, що я вмію.")


@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "🧠 Я вмію:\n"
        "• Відповідати на питання\n"
        "• Запам’ятовувати факти\n"
        "• Нагадувати про важливе\n\n"
        "💬 Спробуй:\n"
        "• Запам’ятай, моє ім’я — Дмитро\n"
        "• Нагадай купити молоко о 18:00\n"
        "• Що ти знаєш про моє ім’я?\n"
        "• /нагадування — список\n"
        "• /видалити_нагадування [текст] — видалити"
    )


@dp.message(Command("нагадування"))
async def list_reminders(message: Message):
    uid = message.from_user.id
    reminders = await get_user_reminders(uid)
    if reminders:
        reply = "🔔 Твої нагадування:\n" + "\n".join(
            [f"• {r[1]} — {r[2].strftime('%Y-%m-%d %H:%M')}" for r in reminders])
    else:
        reply = "📭 У тебе немає активних нагадувань."
    await message.answer(reply)


@dp.message(Command("видалити_нагадування"))
async def delete_reminder(message: Message):
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


@dp.message(F.text)
async def handle_message(message: Message):
    text = message.text.lower()
    uid = message.from_user.id

    if text.startswith("запам’ятай") or text.startswith("запамятай"):
        key, value = parse_fact_command(text)
        await save_fact(uid, key, value)
        await message.answer(f"✅ Запам’ятав: {key} — {value}")

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
        rem = parse_reminder_command(message.text, uid)
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
        except:
            pass


async def main():
    await init_db()
    scheduler.add_job(notify_reminders, 'interval', minutes=1)
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
