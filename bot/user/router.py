from aiogram import F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.router import Router
from sqlalchemy.ext.asyncio import AsyncSession
from bot.dao.dao import UserDAO
from bot.user.kbs import main_user_kb
from bot.user.schemas import SUser

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session_with_commit: AsyncSession, state: FSMContext):
    await state.clear()
    user_data = message.from_user
    user_id = user_data.id
    user_info = await UserDAO(session_with_commit).find_one_or_none_by_id(user_id)
    if user_info is None:
        user_schema = SUser(id=user_id, first_name=user_data.first_name,
                            last_name=user_data.last_name, username=user_data.username)
        await UserDAO(session_with_commit).add(user_schema)
    text = ("👋 Добро пожаловать в Binary Bites! 🍽️\n\nЗдесь каждый байт вкуса закодирован в удовольствие. 😋💻\n"
            "Используйте клавиатуру ниже, чтобы зарезервировать свой столик и избежать переполнения буфера! 🔢🍴")
    await message.answer(text, reply_markup=main_user_kb(user_id))


@router.callback_query(F.data == "about_us")
async def cmd_about(call: CallbackQuery):
    await call.answer("О нас")
    about_text = ("🖥️ О Binary Bites 🍔\n\n"
                  "Мы - первый ресторан, где кулинария встречается с кодом! 👨‍💻👩‍💻\n\n"
                  "🍽️ Наше меню - это настоящий алгоритм вкуса:\n\n"
                  "• Закуски начинаются с 'Hello World' салата 🥗\n"
                  "• Основные блюда включают 'Full Stack' бургер 🍔\n"
                  "• Не забудьте про наш фирменный 'Python' кофе ☕\n\n"
                  "🏆 Наша миссия - оптимизировать ваше гастрономическое удовольствие!\n\n"
                  "📍 Мы находимся по адресу: ул. Программная, д. 404\n"
                  "🕐 Работаем 24/7, потому что настоящие разработчики не спят😉\n\n"
                  "Приходите к нам, чтобы отладить свой аппетит! 🍽️💻")
    await call.message.edit_text(about_text, reply_markup=main_user_kb(call.from_user.id))