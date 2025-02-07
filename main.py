from aiogram_dialog.widgets.input import MessageInput

TOKEN = "7978016344:AAEC7rrETsrPOhSvVw7BTRBw0HwU3b9fd04"

from aiogram.types import CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager, DialogProtocol
from aiogram_dialog.widgets.kbd import Button, Back
from aiogram_dialog.widgets.text import Const, Format
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters.state import StatesGroup, State
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import StartMode
from aiogram_dialog import setup_dialogs

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)


class MySG(StatesGroup):
    name = State()
    age = State()
    job = State()
    about = State()


async def on_input_name(message: Message, dialog: DialogProtocol, manager: DialogManager,):
    manager.dialog_data["name"] = message.text
    await manager.switch_to(MySG.age)


async def on_input_age(message: Message, dialog: DialogProtocol, manager: DialogManager):
    manager.dialog_data["age"] = int(message.text)
    await manager.switch_to(MySG.job)


dialog = Dialog(
    Window(
        Format("Привет, {event.from_user.first_name}! Твой ID: {event.from_user.id}"),
        Format("Язык интерфейса: {event.from_user.language_code}"),
        Format("Тип чата: {event.chat.type}"),
        Const("Как боту к тебе обращаться?"),
        MessageInput(on_input_name),
        state=MySG.name
    ),
    Window(
        Format("{dialog_data[name]}, теперь укажи возраст"),
        MessageInput(on_input_age),
        Back(Const("Назад")),
        state=MySG.age
    )
)

dp.include_router(dialog)


@dp.message(Command("start"))
async def start(message: Message, dialog_manager: DialogManager):
    user_data = {"full_name": message.from_user.full_name,
                 "username": message.from_user.username,
                 "telegram_id": message.from_user.id}
    await dialog_manager.start(MySG.name, mode=StartMode.RESET_STACK, data=user_data)


setup_dialogs(dp)

if __name__ == '__main__':
    dp.run_polling(bot)
