from datetime import date, timedelta, timezone
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Group, ScrollingGroup, Select, Calendar, CalendarConfig, Back, Cancel
from aiogram_dialog.widgets.text import Const, Format, Jinja
from bot.booking.handlers import (process_add_count_capacity, on_table_selected, get_all_tables, process_date_selected,
                                  get_all_available_slots, process_slotes_selected, cancel_dialog)
from bot.booking.state import BookingState


def get_capacity_window() -> Window:
    """Окно выбора количества гостей."""
    return Window(
        Const("Выберите кол-во гостей:"),
        Group(
            *[Button(
                text=Const(str(i)),
                id=str(i),
                on_click=process_add_count_capacity
            ) for i in range(1, 7)],
            Cancel(on_click=cancel_dialog),
            width=2
        ),
        state=BookingState.count
    )


def get_table_window() -> Window:
    """Окно выбора стола."""
    return Window(
        Format("{dialog_data[text_table]}"),
        ScrollingGroup(
            Select(
                Format("Стол №{item[id]} - {item[description]}"),
                id="table_select",
                item_id_getter=lambda item: str(item["id"]),
                items="tables",
                on_click=on_table_selected,
            ),
            Back(Const("Назад")),
            Cancel(on_click=cancel_dialog),
            id="tables_scrolling",
            width=1,
            height=1,
        ),
        getter=get_all_tables,
        state=BookingState.table,
    )


def get_date_window() -> Window:
    """Окно выбора даты."""
    return Window(
        Const("На какой день бронируем столик?"),
        Calendar(
            id="cal",
            on_click=process_date_selected,
            config=CalendarConfig(
                firstweekday=0,
                timezone=timezone(timedelta(hours=3)),
                min_date=date.today()
            )
        ),
        Back(Const("Назад")),
        Cancel(on_click=cancel_dialog),
        state=BookingState.booking_date,
    )


def get_slots_window() -> Window:
    """Окно выбора слота."""
    return Window(
        Format("{dialog_data[text_slots]}"),
        ScrollingGroup(
            Select(
                Format("{item[start_time]} до {item[end_time]}"),
                id="slotes_select",
                item_id_getter=lambda item: str(item["id"]),
                items="slots",
                on_click=process_slotes_selected,
            ),
            id="slotes_scrolling",
            width=2,
            height=3,
        ),
        Back(Const("Назад")),
        Cancel(on_click=cancel_dialog),
        getter=get_all_available_slots,
        state=BookingState.booking_time,
    )


def get_confirmed_windows():
    return Window(
        Jinja("{dialog_data[confirmed_text]}"),
        Group(
            Button(Const("Все верно"), id="confirm"),
            Back(),
            Cancel(on_click=cancel_dialog),
        ),
        state=BookingState.confirmation
    )
