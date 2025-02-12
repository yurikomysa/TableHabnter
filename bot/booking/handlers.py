from datetime import date
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select, Button
from bot.booking.schemas import SCapacity
from bot.dao.dao import TableDAO, BookingDAO
from bot.user.kbs import main_user_kb

'''ГЕТТЕРЫ'''


async def get_all_tables(**kwargs):
    """Получение списка столов с учетом выбранной вместимости."""
    manager = kwargs['dialog_manager']
    session = manager.middleware_data.get("session_without_commit")
    capacity = manager.dialog_data["capacity"]

    tables = await TableDAO(session).find_all(SCapacity(capacity=capacity))
    tables = [i.to_dict() for i in tables]

    manager.dialog_data.update({
        "tables": tables,
        "text_table": f'Всего для {capacity} человек найдено {len(tables)} столов. Выберите нужный по описанию'
    })
    return {"tables": tables}


async def get_all_available_slots(**kwargs):
    """Получение списка доступных временных слотов для выбранного стола и даты."""
    manager = kwargs['dialog_manager']
    session = manager.middleware_data.get("session_without_commit")
    booking_date = manager.dialog_data["booking_date"]
    selected_table = manager.dialog_data["selected_table"]

    # Получаем доступные слоты
    slots = await BookingDAO(session).get_available_time_slots(table_id=selected_table["id"], booking_date=booking_date)

    # Преобразуем объекты в словари
    slots = [i.to_dict() for i in slots]

    # Обновляем данные диалога
    manager.dialog_data.update({
        "slots": slots,
        "text_slots": (
            f'Для стола №{selected_table["id"]} найдено {len(slots)} '
            f'{"свободных слотов" if len(slots) != 1 else "свободный слот"}. '
            'Выберите удобное время'
        )
    })

    return {"slots": slots}


'''ОБРАБОТЧИКИ СОСТОЯНИЯ'''


async def cancel_dialog(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await callback.answer("Сценарий бронирования остановлен!")
    await callback.message.answer("Вы отменили сценарий бронирования.",
                                  reply_markup=main_user_kb(callback.from_user.id))
    await dialog_manager.done()


async def on_table_selected(callback: CallbackQuery, select: Select, manager: DialogManager, item_id: str):
    """Обработчик выбора стола."""
    table_id = int(item_id)
    tables = manager.dialog_data["tables"]
    selected_table = next((table for table in tables if table["id"] == table_id), None)
    manager.dialog_data['selected_table'] = selected_table
    await callback.answer(f"Вы выбрали стол с ID: {item_id}")
    await manager.next()


async def process_add_count_capacity(callback: CallbackQuery, button: Button, manager: DialogManager):
    """Обработчик выбора количества гостей."""
    selected_capacity = button.widget_id
    manager.dialog_data["capacity"] = int(selected_capacity)
    await callback.answer(f"Выбрано {selected_capacity} гостей")
    await manager.next()


async def process_date_selected(callback: CallbackQuery, widget, manager: DialogManager, selected_date: date):
    """Обработчик выбора даты."""
    await callback.answer(str(selected_date))
    manager.dialog_data["booking_date"] = selected_date
    await callback.answer(f"Выбрана дата: {selected_date}")
    await manager.next()


async def process_slotes_selected(callback: CallbackQuery, select: Select, manager: DialogManager, item_id: str):
    """Обработчик выбора слота."""
    slot_id = int(item_id)
    slots = manager.dialog_data["slots"]
    selected_slot = next((slot for slot in slots if slot["id"] == slot_id), None)
    await callback.answer(f"Выбрано время С {selected_slot['start_time']} до {selected_slot['end_time']}")
    selected_table = manager.dialog_data["selected_table"]
    manager.dialog_data['selected_slot'] = selected_slot
    booking_date = manager.dialog_data["booking_date"]
    msg_text = (
        "<b>Подтверждение бронирования</b>\n\n"
        f"<b>Дата:</b> {booking_date}\n\n"
        f"<b>Информация о столике:</b>\n"
        f"  - Описание: {selected_table['description']}\n"
        f"  - Кол-во мест: {selected_table['capacity']}\n"
        f"  - Номер столика: {selected_table['capacity']}\n\n"
        f"<b>Время бронирования:</b>\n"
        f"  - С {selected_slot['start_time']} до {selected_slot['end_time']}\n\n"
        "Все ли верно?"
    )
    manager.dialog_data['confirmed_text'] = msg_text
    await manager.next()
