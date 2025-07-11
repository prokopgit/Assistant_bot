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
from utils import parse_fact_command, parse_reminder_command, is_obscene, archaeologist_reply
import config
from news import get_funny_archaeo_news

bot = Bot(token=config.TELEGRAM_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("🏺 Привіт! Я твій археолог-друг і колега. Запитай мене що завгодно або напиши /help — розкажу, що вмію!")

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        "🧭 Я вмію:\n"
        "• Відповідати на запитання (з гумором і досвідом)\n"
        "• Запам’ятовувати факти про тебе\n"
        "• Нагадувати про важливе\n"
        "• Розповідати байки, анекдоти й новини з археології\n"
        "• Щодня о 9:00 — кидаю свіжі архео-новини в @vseprokop\n\n"
        "💬 Приклади:\n"
        "• Запам’ятай, моя знахідка — римська монета\n"
        "• Нагадай перевірити прибор о 18:00\n"
        "• /нагадування — список\n"
        "• /видалити_нагадування [текст]"
    )

@dp.message(Command("нагадування"))
async def list_reminders(message: types.Message):
    uid = message.from_user.id
    reminders = await get_user_reminders(uid)
    if reminders:
        reply = "📜 Ось твої нагадування:\n" + "\n".join(
            [f"• {r[1]} — {r[2].strftime('%Y-%m-%d %H:%M')}" for r in reminders])
    else:
        reply = "🔕 У тебе наразі немає нагадувань."
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
            await message.answer("❗ Такого не знайшов.")
    else:
        await message.answer("⚠️ Приклад: /видалити_нагадування купити батарейки")

@dp.message()
async def handle_message(message: types.Message):
    text = message.text.lower()
    uid = message.from_user.id

    if is_obscene(text):
        await message.answer(archaeologist_reply(text, rude=True))
        return

    if text.startswith("запам’ятай") or text.startswith("запамятай"):
        key, value = parse_fact_command(text)
        await save_fact(uid, key, value)
        await message.answer(f"🧠 Запам’ятав: {key} — {value}")

    elif text.startswith("що ти знаєш") or text.startswith("як мене") or text.startswith("яка моя"):
        key = text.split("про")[-1].strip()
        value = await get_fact(uid, key)
        if value:
            await message.answer(f"📌 У тебе є таке: {key} — {value}")
        else:
            await message.answer("🤷‍♂️ Не пам’ятаю такого.")

    elif text.startswith("забудь"):
        key = text.split("про")[-1].strip()
        await delete_fact(uid, key)
        await message.answer(f"🧹 Все, забув про '{key}'.")

    elif text.startswith("нагадай"):
        rem = await parse_reminder_command(message.text, uid)
        if rem:
            await save_reminder(*rem)
            await message.answer("⏰ Готово, нагадаю як домовлялись.")
        else:
            await message.answer("⛔ Не зміг розпізнати час, попробуй ще раз.")

    else:
        reply = await get_llm_response(text)
        await message.answer(archaeologist_reply(reply))

async def notify_reminders():
    due = await get_due_reminders()
    for uid, text in due:
        try:
            await bot.send_message(uid, f"🔔 Нагадую: {text}")
        except:
            pass

async def post_news_to_channel():
    news = await get_funny_archaeo_news()
    await bot.send_message("@vseprokop", news, parse_mode="HTML")

async def main():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    scheduler.add_job(notify_reminders, 'interval', minutes=1)
    scheduler.add_job(post_news_to_channel, 'cron', hour=9, minute=0)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
