from datetime import date
from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from app.dao.base import BaseDAO
from app.dao.models import User, TimeSlot, Table, Booking


class UserDAO(BaseDAO[User]):
    model = User


class TimeSlotUserDAO(BaseDAO[TimeSlot]):
    model = TimeSlot


class TableDAO(BaseDAO[Table]):
    model = Table


class BookingDAO(BaseDAO[Booking]):
    model = Booking

    async def check_available_bookings(self,
                                       table_id: int,
                                       booking_date: date,
                                       time_slot_id: int):
        """Проверяет наличие существующих броней для стола на указанную дату и временной слот."""
        try:
            query = select(self.model).filter_by(
                table_id=table_id,
                date=booking_date,
                time_slot_id=time_slot_id
            )
            result = await self._session.execute(query)

            # Если результатов нет, стол свободен
            if not result.scalars().all():
                return True

            # Проверяем статус существующих бронирований
            for booking in result.scalars().all():
                if booking.status == "booked":
                    return False  # Стол занят

                # Для других статусов считаем стол свободным
                continue
            # Если все брони имеют неактивные статусы
            return True

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при проверке доступности брони: {e}")

    async def get_available_time_slots(self, table_id: int, booking_date: date):
        """Получает список доступных временных слотов для стола на указанную дату."""
        try:
            # Получаем все брони для данного стола и даты
            bookings_query = select(self.model).filter_by(
                table_id=table_id,
                date=booking_date
            )
            bookings_result = await self._session.execute(bookings_query)
            # Составляем набор занятых слотов (только с активными бронями)
            booked_slots = {booking.time_slot_id for booking in bookings_result.scalars().all() if
                            booking.status == "booked"}
            # Получаем все доступные слоты, исключая занятые
            available_slots_query = select(TimeSlot).filter(
                ~TimeSlot.id.in_(booked_slots)
            )
            available_slots_result = await self._session.execute(available_slots_query)
            return available_slots_result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении доступных временных слотов: {e}")

