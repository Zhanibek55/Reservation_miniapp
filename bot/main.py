import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import asyncio
import re
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from db.crud import get_user, add_user, list_reservations_for_user, RESERVATION_STATUS_LABELS
from db.models import User
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# FSM состояния для регистрации
class Registration(StatesGroup):
    first_name = State()
    last_name = State()
    phone = State()

# Логирование
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Валидация номера телефона (KZ, RU, +7, +77, 8...)
def validate_phone(phone: str) -> bool:
    p = re.sub(r"[^\d+]", "", phone)
    return bool(re.match(r"^(\+7|8)[0-9]{10}$", p)) or bool(re.match(r"^\+\d{11,15}$", p))

# Стартовая команда
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user = get_user(message.from_user.id)
    if user:
        await message.answer(f"Добро пожаловать, {user.first_name}! Вы уже зарегистрированы.")
        return
    await message.answer("Добро пожаловать! Давайте зарегистрируемся. Введите ваше имя:")
    await state.set_state(Registration.first_name)

@dp.message(Registration.first_name)
async def reg_first_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text.strip())
    await message.answer("Введите вашу фамилию:")
    await state.set_state(Registration.last_name)

@dp.message(Registration.last_name)
async def reg_last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text.strip())
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отправить номер телефона", request_contact=True)]],
        resize_keyboard=True
    )
    await message.answer("Отправьте ваш номер телефона:", reply_markup=kb)
    await state.set_state(Registration.phone)

@dp.message(Registration.phone)
async def reg_phone(message: types.Message, state: FSMContext):
    # 1. Если отправлен контакт (request_contact) и это сам пользователь
    if message.contact and message.contact.user_id == message.from_user.id:
        phone = message.contact.phone_number
    # 2. Если отправлен чужой контакт (визитка)
    elif message.contact:
        await message.answer("Пожалуйста, используйте кнопку для отправки именно своего номера телефона.")
        return
    # 3. Если написан текст — пробуем валидировать
    else:
        phone = message.text.strip()
        if not validate_phone(phone):
            await message.answer("Некорректный формат номера телефона. Введите номер в формате +77001112233 или используйте кнопку.")
            return
    data = await state.get_data()
    user = User(
        telegram_id=message.from_user.id,
        first_name=data["first_name"],
        last_name=data["last_name"],
        phone=phone,
        is_admin=False
    )
    add_user(user)
    await message.answer(f"Спасибо за регистрацию, {user.first_name}!", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()

# Команда /profile — просмотр профиля пользователя
@dp.message(Command("profile"))
async def cmd_profile(message: types.Message):
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("Вы не зарегистрированы. Пожалуйста, используйте /start для регистрации.")
        return
    text = (
        f"<b>Ваш профиль:</b>\n"
        f"Имя: <b>{user.first_name}</b>\n"
        f"Фамилия: <b>{user.last_name}</b>\n"
        f"Телефон: <b>{user.phone}</b>\n"
        f"Статус: {'Администратор' if user.is_admin else 'Пользователь'}"
    )
    await message.answer(text, parse_mode="HTML")

# Команда /mybookings — просмотр своих броней
@dp.message(Command("mybookings"))
async def cmd_mybookings(message: types.Message):
    reservations = list_reservations_for_user(message.from_user.id)
    if not reservations:
        await message.answer("У вас пока нет бронирований.")
        return
    lines = [
        f"Стол №{r.table_id} — {r.date.strftime('%d.%m.%Y')} {r.time_start.strftime('%H:%M')}–{r.time_end.strftime('%H:%M')}\nСтатус: <b>{RESERVATION_STATUS_LABELS.get(r.status, r.status)}</b>"
        for r in reservations
    ]
    await message.answer("\n\n".join(lines), parse_mode="HTML")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
