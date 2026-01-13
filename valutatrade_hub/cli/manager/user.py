from datetime import datetime
from typing import List, Optional

from ...core.models.user import User
from ...core.utils import generate_salt, hash_password
from ..storage import FileStorageManager


class UserManager:
    """Менеджер пользователей."""

    def __init__(self, file_path: str):
        self._storage = FileStorageManager(file_path)
        self._users : List[User] = []
        self._load()

    def get_all(self) -> List[User]:
        """Возвращает всех пользователей."""
        return list(self._users)

    def get_by_username(self, username: str) -> Optional[User]:
        """Ищет пользователя по username."""
        for user in self._users:
            if user._username == username:
                return user
        return None

    def create(self, username: str, password: str) -> User:
        """Создаёт и добавляет нового пользователя."""
        if self.get_by_username(username):
            raise ValueError(f'Имя пользователя {username} уже занято.')

        if len(password) < 4:
            raise ValueError('Пароль должен быть не короче 4 символов.')

        user_id = self._generate_user_id()
        salt = generate_salt()
        hashed_password = hash_password(password, salt)

        user = User(
            user_id=user_id,
            username=username,
            hashed_password=hashed_password,
            salt=salt,
            registration_date=datetime.now(),
        )

        self._users.append(user)
        self.save()
        return user

    def save(self) -> None:
        """Сохраняет текущее состояние в файл."""
        self._storage.save(self._serialize())

    def authenticate(self, username: str, password: str) -> User:
        """Аутентификация пользователя."""
        user = self.get_by_username(username)
        if user is None:
            raise ValueError('Неверный логин или пароль.')

        hashed_input = hash_password(password, user._salt)
        if hashed_input != user._hashed_password:
            raise ValueError('Неверный логин или пароль.')

        return user

    def _load(self) -> None:
        raw_users = self._storage.load()
        for data in raw_users:
            self._users.append(self._deserialize(data))

    def _generate_user_id(self) -> int:
        if not self._users:
            return 1
        return max(user.user_id for user in self._users) + 1

    @staticmethod
    def _deserialize(data: dict) -> User:
        return User(
            user_id=data['user_id'],
            username=data['username'],
            hashed_password=data['hashed_password'],
            salt=data['salt'],
            registration_date=datetime.fromisoformat(
                data['registration_date']
            ),
        )

    def _serialize(self) -> list[dict]:
        return [
            {
                'user_id': user._user_id,
                'username': user._username,
                'hashed_password': user._hashed_password,
                'salt': user._salt,
                'registration_date': user._registration_date.isoformat(),
            }
            for user in self._users
        ]
