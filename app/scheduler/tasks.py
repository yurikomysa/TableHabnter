from app.bot.create_bot import bot
from app.config import broker, settings


@broker.subscriber("new_booking")
async def send_booking_msg(msg: str):
    for admin in settings.ADMIN_IDS:
        await bot.send_message(admin, text=msg)
