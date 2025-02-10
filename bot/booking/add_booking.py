from typing import Any
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.common import ManagedScroll, Scroll
from aiogram_dialog.widgets.kbd import Button, Group, PrevPage, NextPage, Cancel, ListGroup, SwitchInlineQuery, \
    ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format
from bot.booking.state import BookingState
from bot.dao.dao import TableDAO
from bot.dao.database import async_session_maker


async def get_all_tables(**kwargs):
    async with async_session_maker() as session:
        tables = await TableDAO(session).find_all()
    return {"tables": [i.to_dict() for i in tables]}


async def on_table_selected(
        callback: CallbackQuery,
        select: Select,
        manager: DialogManager,
        item_id: str
):
    # Обработка выбора стола
    await callback.answer(f"Вы выбрали стол с ID: {item_id}")


# get_count = Window(
#     Const("Выберите стол:"),
#     ScrollingGroup(
#         Select(
#             Format("Стол {item[id]} ({item[capacity]} мест)"),
#             id="table_select",
#             item_id_getter=lambda item: str(item["id"]),
#             items="tables",
#             on_click=on_table_selected,
#         ),
#         id="tables_scrolling",
#         width=2,
#         height=5,
#     ),
#     getter=get_all_tables,
#     state=BookingState.count,
# )

get_count = Window(
    Const("Выберите стол:"),
    Group(
        Select(
            Format("Стол {item[id]} ({item[capacity]} мест)"),
            id="table_select",
            item_id_getter=lambda item: str(item["id"]),
            items="tables",
            on_click=on_table_selected,
        ),
        width=2,
    ),
    getter=get_all_tables,
    state=BookingState.count,
)

dialog = Dialog(get_count)
