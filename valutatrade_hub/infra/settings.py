from __future__ import annotations

from typing import Any

class SettingsLoader:
    """
    Singleton для хранения настроек проекта.
    Настройки жестко зашиты в коде, файл конфигурации не требуется.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_defaults()
        return cls._instance

    def _load_defaults(self):
        """
        Загружаем дефолтные настройки.
        """
        self._config = {
            "users_file": "data/users.json",
            "portfolios_file": "data/portfolios.json",
            "rates_file": "data/rates.json",
            "rates_ttl_seconds": 300,       # TTL курсов в секундах
            "base_currency": "USD",         # Базовая валюта
            "logs_path": "logs/actions.log" # путь к логам
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Получение значения по ключу.
        """
        return self._config.get(key, default)

    def reload(self):
        """
        Сброс и перезагрузка дефолтных настроек.
        """
        self._load_defaults()
