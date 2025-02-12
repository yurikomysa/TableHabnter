from app.dao.dao import BookingDAO
from app.dao.database import async_session_maker


async def disable_booking():
    async with async_session_maker() as session:
        await BookingDAO(session).complete_past_bookings()