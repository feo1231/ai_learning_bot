import logging
import asyncio
import aiofiles
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hbold
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

API_TOKEN = 'ТВОЙ_ТОКЕН'
ADMIN_ID = 123456789  # ← сюда вставь свой Telegram ID

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# Хранилище пользователей
user_data = {}

# Курс
COURSE = {
    "Python Базовый": [
        "Урок 1: Переменные и типы данных.",
        "Урок 2: Условия и циклы.",
        "Урок 3: Функции и модули."
    ],
    "ИИ для начинающих": [
        "Урок 1: Что такое ИИ?",
        "Урок 2: Основы машинного обучения.",
        "Урок 3: Применения ИИ в реальной жизни.",
        "Урок 4: Нейронные сети.",
        "Урок 5: ChatGPT и другие модели."
    ]
}

# Состояния
class UserState(StatesGroup):
    choosing_course = State()
    viewing_lesson = State()

# Инлайн-клавиатура главного меню
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Мой курс", callback_data="my_course")],
        [InlineKeyboardButton(text="➡️ Следующий урок", callback_data="next_lesson")],
        [InlineKeyboardButton(text="🔄 Сменить курс", callback_data="change_course")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")]
    ])

# Старт
@dp.message(F.text == "/start")
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data[user_id] = {"name": message.from_user.first_name, "course": None, "lesson": 0}

    await message.answer(
        f"Привет, {hbold(user_data[user_id]['name'])}! 👋\n"
        f"Я бот-помощник для изучения ИИ и Python.\n\n"
        "Выбери курс для начала:",
        reply_markup=course_keyboard()
    )
    await state.set_state(UserState.choosing_course)

# Клавиатура выбора курса
def course_keyboard():
    buttons = [
        [InlineKeyboardButton(text=course, callback_data=f"course_{course}")]
        for course in COURSE
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Выбор курса
@dp.callback_query(F.data.startswith("course_"))
async def choose_course(callback: types.CallbackQuery, state: FSMContext):
    course_name = callback.data.split("course_")[1]
    user_id = callback.from_user.id
    user_data[user_id]["course"] = course_name
    user_data[user_id]["lesson"] = 0

    await callback.message.edit_text(
        f"Ты выбрал курс: <b>{course_name}</b>\n\nГотов начать?",
        reply_markup=main_menu()
    )
    await state.set_state(UserState.viewing_lesson)

# Показать текущий курс
@dp.callback_query(F.data == "my_course")
async def show_course(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    course = user_data[user_id].get("course")
    lesson = user_data[user_id].get("lesson", 0)

    if not course:
        await callback.answer("Сначала выбери курс.")
        return

    progress = int((lesson / len(COURSE[course])) * 100)
    text = f"📘 Курс: <b>{course}</b>\n" \
           f"📍 Урок: {lesson + 1} из {len(COURSE[course])}\n" \
           f"📊 Прогресс: {progress}%"

    await callback.message.edit_text(text, reply_markup=main_menu())

# Следующий урок
@dp.callback_query(F.data == "next_lesson")
async def next_lesson(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    course = user_data[user_id].get("course")
    lesson = user_data[user_id].get("lesson", 0)

    if course is None:
        await callback.answer("Сначала выбери курс.")
        return

    lessons = COURSE[course]
    if lesson >= len(lessons):
        await callback.message.edit_text(
            "🎉 Поздравляю! Ты завершил курс.",
            reply_markup=main_menu()
        )
        return

    await callback.message.edit_text(
        f"<b>{lessons[lesson]}</b>",
        reply_markup=main_menu()
    )
    user_data[user_id]["lesson"] += 1

# Сменить курс
@dp.callback_query(F.data == "change_course")
async def change_course(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Выбери новый курс:", reply_markup=course_keyboard())
    await state.set_state(UserState.choosing_course)

# Помощь
@dp.callback_query(F.data == "help")
async def help_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🧠 <b>Чем я могу помочь:</b>\n"
        "- /start — начать сначала\n"
        "- Переключаться между курсами\n"
        "- Переходить по урокам\n"
        "- Отслеживать прогресс\n"
        "- Обратная связь через разработчика",
        reply_markup=main_menu()
    )

# Обработка всех ошибок
@dp.errors()
async def error_handler(event, error):
    logging.error(f"Ошибка: {error}")
    if hasattr(event, 'from_user'):
        await bot.send_message(ADMIN_ID, f"⚠️ Ошибка у пользователя {event.from_user.id}: {error}")

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


