from typing import List

from app.database.memory import fake_db
from app.errors import EntityNotFoundError
from app.models import User, UserCreate


class UserService:
    @staticmethod
    def list_users() -> List[User]:
        return fake_db

    @staticmethod
    def create_user(user_create: UserCreate) -> User:
        new_id = len(fake_db) + 1
        user = User(id=new_id, **user_create.model_dump())
        fake_db.append(user)
        return user

    @staticmethod
    def _find_user_or_raise(user_id: int) -> User:
        user = next((u for u in fake_db if u.id == user_id), None)
        if not user:
            raise EntityNotFoundError(entity="User", identifier=str(user_id))
        return user

    @staticmethod
    def get_user(user_id: int) -> User:
        return UserService._find_user_or_raise(user_id)

    @staticmethod
    def update_user(user_id: int, user_create: UserCreate) -> User:
        user = UserService._find_user_or_raise(user_id)

        user.name = user_create.name
        user.age = user_create.age
        user.music_preferences = user_create.music_preferences

        return user

    @staticmethod
    def delete_user(user_id: int) -> None:
        user = UserService._find_user_or_raise(user_id)
        fake_db.remove(user)
