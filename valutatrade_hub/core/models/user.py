import datetime
from typing import Dict

from ..utils import hash_password


class User:

    def __init__(
        self,
        user_id: int,
        username: str,
        hashed_password: str, 
        salt: str,
        registration_date: datetime
    ) -> None:
        self._user_id = user_id
        self._username = username
        self._hashed_password = hashed_password
        self._salt = salt
        self._registration_date = registration_date

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username
    
    @username.setter
    def username(self, username: str) -> None:
        if not username.strip():
            raise ValueError('Имя не может быть пустым.')
        self._username = username.strip()

    @property
    def registration_date(self) -> datetime:
        return self._registration_date

    def check_password(self, password: str) -> bool:
        if not self._hashed_password or not self._salt:
            return False
        return (
            hash_password(password, self._salt)
            == self._hashed_password
        )

    def change_password(self, new_password) -> None:
        if self.check_password():
            pass

    def get_user_info(self) -> Dict:
        return {
            'user_id': self._user_id,
            'username': self._username,
            'registration_date': self._registration_date,
        }
