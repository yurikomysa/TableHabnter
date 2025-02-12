from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config import settings


def main_user_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(text="🍽️ Забронировать столик", callback_data="book_table"))
    kb.add(InlineKeyboardButton(text="📅 Мои брони", callback_data="my_bookings"))
    kb.add(InlineKeyboardButton(text="ℹ️ О нас", callback_data="about_us"))

    if user_id in settings.ADMIN_IDS:
        kb.add(InlineKeyboardButton(text="🔐 Админ-панель", callback_data="admin_panel"))

    kb.adjust(1)  # Размещаем кнопки в один столбец
    return kb.as_markup()