from datetime import date, datetime
from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from bot.dao.base import BaseDAO
from bot.dao.models import User, TimeSlot, Table, Booking


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
                                       booking_date: datetime,
                                       time_slot_id: int):
        """Проверяет наличие существующих броней для стола на указанную дату и временной слот."""
        try:
            query = select(self.model).filter_by(
                table_id=table_id,
                date=booking_date,
                time_slot_id=time_slot_id
            )
            result = await self._session.execute(query)
            # Возвращаем True если бронь отсутствует (стол свободен)
            return not bool(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при проверке доступности брони: {e}")
            raise

    async def get_available_time_slots(self, table_id: int, booking_date: date):
        """Получает список доступных временных слотов для стола на указанную дату."""
        try:
            # Получаем все занятые слоты для данного стола и даты
            booked_slots_query = select(self.model.time_slot_id).filter_by(
                table_id=table_id,
                date=booking_date
            )
            booked_slots_result = await self._session.execute(booked_slots_query)
            booked_slots = {row[0] for row in booked_slots_result}

            # Получаем все доступные слоты, исключая занятые
            available_slots_query = select(TimeSlot).filter(
                ~TimeSlot.id.in_(booked_slots)
            )
            available_slots_result = await self._session.execute(available_slots_query)
            return available_slots_result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении доступных временных слотов: {e}")
            raise
