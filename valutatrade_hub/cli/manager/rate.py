from decimal import Decimal
from datetime import datetime
from typing import Dict

from ..storage import FileStorageManager


class RateManager:
    """Менеджер курсов валют."""

    def __init__(self, file_path: str):
        self._storage = FileStorageManager(file_path)
        self._rates: Dict[str, Dict[str, any]] = {}
        self.source: str = ""
        self.last_refresh: datetime | None = None
        self._load()

    def get_rate(self, from_currency: str, to_currency: str) -> Decimal:
        """Возвращает курс from_currency -> to_currency"""
        if from_currency == to_currency:
            return Decimal("1")

        key = f"{from_currency}_{to_currency}"
        if key not in self._rates:
            raise ValueError(f'Курс {from_currency}->{to_currency} недоступен. Повторите попытку позже.')

        return Decimal(str(self._rates[key]["rate"]))

    def update_rate(
        self, from_currency: str, to_currency: str, rate: Decimal
    ) -> None:
        """Обновляет курс и дату обновления"""
        key = f"{from_currency}_{to_currency}"
        self._rates[key] = {
            "rate": rate,
            "updated_at": datetime.now().isoformat(),
        }
        self.last_refresh = datetime.now()

    def save(self, source: str = "Unknown") -> None:
        """Сохраняет текущие курсы в файл"""
        data = {k: v for k, v in self._rates.items()}
        data["source"] = source
        data["last_refresh"] = self.last_refresh.isoformat() if self.last_refresh else datetime.now().isoformat()
        self._storage.save(data)

    def get_rate_pair(
        self, from_currency: str, to_currency: str
    ) -> dict:
        """
        Возвращает прямой и обратный курс.
        """
        key = f"{from_currency}_{to_currency}"
        if key not in self._rates:
            raise ValueError(f'Курс {from_currency}->{to_currency} недоступен. Повторите попытку позже.')

        rate_data = self._rates[key]

        direct_rate = Decimal("1") / rate_data["rate"]
        reverse_rate = rate_data["rate"]

        return {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "direct_rate": direct_rate,
            "reverse_rate": reverse_rate,
            "updated_at": rate_data["updated_at"],
        }

    def format_rate(
        self, from_currency: str, to_currency: str
    ) -> str:
        data = self.get_rate_pair(from_currency, to_currency)
        updated_at = datetime.fromisoformat(data["updated_at"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        return (
            f"Курс {data['from_currency']}->{data['to_currency']}: "
            f"{data['direct_rate']:.8f} "
            f"(обновлено: {updated_at})\n"
            f"Обратный курс {data['to_currency']}->{data['from_currency']}: "
            f"{data['reverse_rate']}"
        )
    
    def _load(self) -> None:
        raw = self._storage.load()
        self.source = raw.get("source", "Unknown")
        last_refresh_str = raw.get("last_refresh")
        self.last_refresh = datetime.fromisoformat(last_refresh_str) if last_refresh_str else None

        for key, value in raw.items():
            if key in ["source", "last_refresh"]:
                continue
            self._rates[key] = {
                "rate": Decimal(str(value["rate"])),
                "updated_at": value["updated_at"],
            }

    def __str__(self) -> str:
        lines = [f"Курс (источник: {self.source}, обновлено: {self.last_refresh}):"]
        for key, value in self._rates.items():
            lines.append(f"- {key}: {value['rate']} (обновлено {value['updated_at']})")
        return "\n".join(lines)
