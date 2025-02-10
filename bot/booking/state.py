from aiogram.fsm.state import StatesGroup, State


class BookingState(StatesGroup):
    count = State()
    table = State()
    booking_date = State()
    booking_time = State()
    confirmed = State()
    table_description = State()
