import json
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import inspect, TIMESTAMP, func, insert
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
from bot.config import settings

engine = create_async_engine(url=settings.DB_URL)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )

    def to_dict(self, exclude_none: bool = False):
        """
        Преобразует объект модели в словарь.

        Args:
            exclude_none (bool): Исключать ли None значения из результата

        Returns:
            dict: Словарь с данными объекта
        """
        result = {}
        for column in inspect(self.__class__).columns:
            value = getattr(self, column.key)

            # Преобразование специальных типов данных
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, Decimal):
                value = float(value)
            elif isinstance(value, uuid.UUID):
                value = str(value)

            # Добавляем значение в результат
            if not exclude_none or value is not None:
                result[column.key] = value

        return result


async def add_tables_to_db(conn, table_model):
    with open(settings.TABLES_JSON, 'r') as file:
        tables_data = json.load(file)
        print(tables_data)
        stmt = insert(table_model).values(tables_data)
        await conn.execute(stmt)


async def add_time_slots_to_db(conn, slot_model):
    start_date = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=30)

    time_slots = []
    current_date = start_date.date()  # Используем только дату без времени

    while current_date < end_date.date():
        slot_start_time = datetime.combine(current_date, datetime.min.time()).replace(hour=6)

        while slot_start_time.hour < 24:
            slot_end_time = slot_start_time + timedelta(hours=2)

            time_slots.append({
                "start_time": slot_start_time,
                "end_time": slot_end_time,
                "booking_status": False
            })

            slot_start_time += timedelta(hours=2)  # Увеличиваем время начала следующего слота

        current_date += timedelta(days=1)

    if time_slots:  # Проверка на пустой список данных
        stmt = insert(slot_model).values(time_slots)
        await conn.execute(stmt)


async def initialize_db(table_model, slot_model, drop=False, add_tables=False, add_slots=False):
    async with engine.begin() as conn:
        if drop:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    if add_tables or add_slots:
        async with async_session_maker as session:
            if add_tables:
                await add_tables_to_db(session, table_model)
            if add_slots:
                await add_time_slots_to_db(session, slot_model)
            await session.commit()
