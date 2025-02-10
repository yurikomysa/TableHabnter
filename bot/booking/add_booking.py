from typing import Any
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.common import ManagedScroll, Scroll
from aiogram_dialog.widgets.kbd import Button, Group, PrevPage, NextPage, Cancel, ListGroup, SwitchInlineQuery, \
    ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format
from bot.booking.state import BookingState
from bot.dao.dao import TableDAO
from bot.dao.database import async_session_maker


async def get_all_tables():
    async with async_session_maker() as session:
        tables = await TableDAO(session).find_all()

    return [i.to_dict() for i in tables]


def create_count_table():
    list_group = [Button(Const(str(i)), id=str(i)) for i in range(1, 7)]
    list_group.append(Button(Const("Отмена"), id=""))

get_count = Window(
    Const("Выберите количество гостей: "),
    Group(*create_count_table(), width=2),
    state=BookingState.count
)

dialog = Dialog(get_count)
