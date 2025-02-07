from bot.dao.base import BaseDAO
from bot.dao.models import User


class UserDAO(BaseDAO[User]):
    model = User
