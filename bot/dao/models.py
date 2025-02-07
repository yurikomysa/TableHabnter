from datetime import datetime
from sqlalchemy import BigInteger, Integer, ForeignKey, TIMESTAMP, Date, text, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from bot.dao.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None]
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="user")


class Table(Base):
    __tablename__ = "tables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    capacity: Mapped[int]
    description: Mapped[str | None]
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="table")


class TimeSlot(Base):
    __tablename__ = "time_slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    start_time: Mapped[datetime] = mapped_column(TIMESTAMP)
    end_time: Mapped[datetime] = mapped_column(TIMESTAMP)
    booking_status: Mapped[bool] = mapped_column(default=True, server_default=text("false"))
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="time_slot")


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    table_id: Mapped[int] = mapped_column(Integer, ForeignKey("tables.id"))
    time_slot_id: Mapped[int] = mapped_column(Integer, ForeignKey("time_slots.id"))
    date: Mapped[datetime] = mapped_column(Date)
    status: Mapped[str]
    user: Mapped["User"] = relationship("User", back_populates="bookings")
    table: Mapped["Table"] = relationship("Table", back_populates="bookings")
    time_slot: Mapped["TimeSlot"] = relationship("TimeSlot", back_populates="bookings")
