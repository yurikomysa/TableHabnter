import locale
from datetime import datetime, timedelta, timezone
from datetime import date
from zoneinfo import ZoneInfo
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Group, ScrollingGroup, Select, Calendar, CalendarConfig
from aiogram_dialog.widgets.text import Const, Format
from bot.booking.schemas import SCapacity
from bot.booking.state import BookingState
from bot.dao.dao import TableDAO





# Функция для получения текущей даты
async def get_date_data(**kwargs):
    return {"current_date": datetime.now().strftime("%Y-%m-%d")}


# Обработчик выбора даты
async def on_date_selected(callback: CallbackQuery, widget,
                           manager: DialogManager, selected_date: date):
    await callback.answer(str(selected_date))


async def get_all_tables(**kwargs):
    manager = kwargs['dialog_manager']
    session = manager.middleware_data.get("session_without_commit")
    capacity = manager.dialog_data["capacity"]
    tables = await TableDAO(session).find_all(SCapacity(capacity=capacity))
    tables = [i.to_dict() for i in tables]
    manager.dialog_data["tables"] = tables
    manager.dialog_data["description"] = (f'Всего для {capacity} человек найдено {len(tables)} столов. '
                                          f'Выберите нужный по описанию')
    return {"tables": tables}


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
        await manager.next()
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
    Format("{dialog_data[description]}"),
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

date_window = Window(
    Const("На какой день бронируем столик?"),
    Calendar(id="cal",
             on_click=on_date_selected,
             config=CalendarConfig(firstweekday=0, timezone=timezone(timedelta(hours=3)), min_date=date.today())),
    state=BookingState.date,
)
dialog = Dialog(capacity_window, get_table, date_window)
