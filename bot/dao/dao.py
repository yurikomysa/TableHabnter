from bot.dao.base import BaseDAO
from bot.dao.models import User, TimeSlot, Table


class UserDAO(BaseDAO[User]):
    model = User


class TimeSlotUserDAO(BaseDAO[TimeSlot]):
    model = TimeSlot


class TableDAO(BaseDAO[Table]):
    model = Table
