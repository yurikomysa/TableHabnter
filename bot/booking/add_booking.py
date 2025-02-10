from typing import Any
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.common import ManagedScroll, Scroll
from aiogram_dialog.widgets.kbd import Button, Group, PrevPage, NextPage, Cancel, ListGroup, SwitchInlineQuery, \
    ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format

from bot.booking.schemas import SCapacity
from bot.booking.state import BookingState
from bot.dao.dao import TableDAO
from bot.dao.database import async_session_maker


async def get_all_tables(**kwargs):
    manager = kwargs['dialog_manager']
    session = manager.middleware_data.get("session_without_commit")
    capacity = manager.dialog_data["capacity"]
    tables = await TableDAO(session).find_all(SCapacity(capacity=capacity))
    tables = [i.to_dict() for i in tables]
    msg_text = (
        f"Всего для {capacity} человек найдено {len(tables)} столов.\n\n"
        "Пожалуйста, выберите подходящий стол из списка ниже, "
        "ориентируясь на его описание."
    )
    return {"tables": tables, "msg_text": msg_text}


async def on_table_selected(
        callback: CallbackQuery,
        select: Select,
        manager: DialogManager,
        item_id: str
):
    table_id = int(item_id)
    tables = manager.dialog_data["tables"]
    selected_table = next((table for table in tables if table["id"] == table_id), None)
    if selected_table:
        description = selected_table["description"]
        await callback.answer(f"Вы выбрали стол с ID: {item_id}\nОписание: {description}")
    else:
        await callback.answer(f"Стол с ID: {item_id} не найден.")


async def process_add_count_capacity(callback: CallbackQuery, button: Button, manager: DialogManager):
    selected_capacity = button.widget_id
    await callback.answer(f'Выбрано: {selected_capacity} гостей.')
    manager.dialog_data["capacity"] = int(selected_capacity)
    await callback.answer(f"Вы выбрали количество гостей: {selected_capacity}")
    await manager.next()


capacity_window = Window(
    Const("Выберите кол-во гостей:"),
    Group(*[Button(text=Const(str(i)),
                   id=str(i),
                   on_click=process_add_count_capacity) for i in range(1, 7)],
          width=2),
    state=BookingState.count
)

get_table = Window(
    Format("{dialog_data[msg_text]}"),
    ScrollingGroup(
        Select(
            Format("Стол №{item[id]} - {item[description]}"),
            id="table_select",
            item_id_getter=lambda item: str(item["id"]),
            items="tables",
            on_click=on_table_selected,
        ),
        id="tables_scrolling",
        width=1,
        height=1,
    ),
    getter=get_all_tables,
    state=BookingState.table,
)

dialog = Dialog(capacity_window, get_table)