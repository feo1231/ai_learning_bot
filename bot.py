import asyncio
import logging
import os
from datetime import datetime
from typing import List, Tuple

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramForbiddenError

# 🔐 Конфигурация
API_TOKEN = "7948123186:AAEsauVwTD7N4XV9BOYwFVi1tfQCPCMwTgY"
ADMIN_ID = 380134226

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

STAGES: List[Tuple[str, str]] = [
    ("Основы Python", "https://stepik.org/course/67"),
    ("Математика для ИИ", "https://www.khanacademy.org/math"),
    ("Машинное обучение", "https://www.coursera.org/learn/machine-learning"),
    ("Глубокое обучение", "https://www.coursera.org/specializations/deep-learning"),
    ("LLM и Chat-боты", "https://huggingface.co/learn/nlp-course/chapter1"),
    ("Деплой и облака", "https://render.com"),
    ("Портфолио и заказы", "https://github.com")
]

users_data = {}

class AdminState(StatesGroup):
    waiting_task_text = State()
    waiting_notify_time = State()

def get_user_data(user_id: int):
    if user_id not in users_data:
        users_data[user_id] = {"stage": 0, "notify": "", "stats": 0}
    return users_data[user_id]

def get_stage(user_id: int) -> int:
    return get_user_data(user_id)["stage"]

def set_stage(user_id: int, stage: int):
    get_user_data(user_id)["stage"] = stage

def set_notify_time(user_id: int, notify_time: str):
    get_user_data(user_id)["notify"] = notify_time

def get_notify_time(user_id: int) -> str:
    return get_user_data(user_id)["notify"]

def add_stat(user_id: int):
    get_user_data(user_id)["stats"] += 1

def get_stat(user_id: int) -> int:
    return get_user_data(user_id)["stats"]

main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📚 Прогресс"), KeyboardButton(text="🧠 Задание")],
    [KeyboardButton(text="🔔 Напоминание"), KeyboardButton(text="📈 Статистика")],
    [KeyboardButton(text="⚙️ Помощь")]
], resize_keyboard=True)

@router.message(F.text == "/start")
async def start_handler(message: Message):
    get_user_data(message.from_user.id)
    await message.answer("Привет! Я помогу тебе пройти курс по нейросетям.", reply_markup=main_kb)

@router.message(F.text == "📚 Прогресс")
async def progress_handler(message: Message):
    stage = get_stage(message.from_user.id)
    lines = [f"{'✅' if i < stage else '⬜'} {i + 1}. {title}" for i, (title, _) in enumerate(STAGES)]
    await message.answer("Твой прогресс:\n" + "\n".join(lines))

@router.message(F.text == "🧠 Задание")
async def task_handler(message: Message):
    stage = get_stage(message.from_user.id)
    if stage >= len(STAGES):
        await message.answer("🎉 Все этапы завершены!")
        return
    title, link = STAGES[stage]
    await message.answer(f"📌 Этап {stage + 1}: {title}\nСсылка: {link}\nКогда выполнишь — напиши 'готово'.")
    add_stat(message.from_user.id)

@router.message(F.text.lower().in_(["готово", "готов", "done"]))
async def done_handler(message: Message):
    stage = get_stage(message.from_user.id)
    set_stage(message.from_user.id, stage + 1)
    await message.answer("Молодец! Этап пройден. ✅")

@router.message(F.text == "🔔 Напоминание")
async def reminder_handler(message: Message, state: FSMContext):
    await message.answer("Во сколько напоминать каждый день? (формат HH:MM по МСК)")
    await state.set_state(AdminState.waiting_notify_time)

@router.message(AdminState.waiting_notify_time)
async def save_notify(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text, "%H:%M")
        set_notify_time(message.from_user.id, message.text)
        await message.answer(f"Напоминание установлено на {message.text}")
        await state.clear()
    except ValueError:
        await message.answer("Формат должен быть HH:MM")

@router.message(F.text == "📈 Статистика")
async def stat_handler(message: Message):
    count = get_stat(message.from_user.id)
    await message.answer(f"Ты открывал задание {count} раз(а). Продолжай в том же духе! 💪")

@router.message(F.text == "⚙️ Помощь")
async def help_handler(message: Message):
    await message.answer("Я бот-трекер для изучения нейросетей. Прогресс хранится в памяти. Используй меню для обучения.")

async def scheduler():
    while True:
        now = datetime.now().strftime("%H:%M")
        for user_id, data in users_data.items():
            if data["notify"] == now:
                try:
                    await bot.send_message(user_id, "⏰ Напоминание: пора учиться!")
                except TelegramForbiddenError:
                    continue
        await asyncio.sleep(60)

async def main():
    dp.include_router(router)
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

