import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import os

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Инициализируем бота и диспетчер
BOT_TOKEN = os.getenv("BOT_TOKEN") or "7948123186:AAEsauVwTD7N4XV9BOYwFVi1tfQCPCMwTgY"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Главное меню
menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📚 Уроки", callback_data="lessons")],
    [InlineKeyboardButton(text="🧠 Задания", callback_data="tasks")],
    [InlineKeyboardButton(text="📈 Прогресс", callback_data="progress")],
    [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")],
])

# Обработка команды /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! 👋 Я бот-помощник для изучения ИИ.
Выбери действие ниже ⬇️",
        reply_markup=menu_keyboard,
    )

# Обработка inline-кнопок
@dp.callback_query()
async def handle_callbacks(callback: types.CallbackQuery):
    data = callback.data

    responses = {
        "lessons": "📚 Вот список уроков:
1. Введение в ИИ
2. Машинное обучение
3. Нейронные сети
(в разработке)",
        "tasks": "🧠 Задания:
1. Пройди курс 'Основы Python'
2. Выполни мини-проект",
        "progress": "📈 Отслеживание прогресса пока не реализовано, но скоро будет!",
        "help": "ℹ️ Я могу:
- Показывать уроки
- Давать задания
- Отслеживать прогресс
Просто выбери пункт в меню!",
    }

    await callback.message.edit_text(responses.get(data, "Неизвестная команда."), reply_markup=menu_keyboard)
    await callback.answer()

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())