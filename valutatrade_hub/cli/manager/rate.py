from datetime import datetime
from decimal import Decimal
from typing import Dict

from ...core.currencies import get_currency
from ...core.exceptions import CurrencyNotFoundError, RatesExpiredError
from ..storage import FileStorageManager


class RateManager:
    """Менеджер курсов валют."""

    def __init__(self, file_path: str, ttl: int):
        self._storage = FileStorageManager(file_path)
        self._ttl = ttl
        self._rates: Dict[str, Dict[str, any]] = {}
        self.source: str = ""
        self.last_refresh: datetime | None = None
        self._load()

    def get_rate(self, from_currency: str, to_currency: str) -> Decimal:
        """Возвращает курс from_currency -> to_currency."""
        self.is_expired()
        from_currency_obj = get_currency(from_currency)
        to_currency_obj = get_currency(to_currency)
        key = f"{from_currency_obj.code}_{to_currency_obj.code}"
        if key not in self._rates:
            raise ValueError(
                f"Курс для {from_currency_obj.code}->{to_currency_obj.code} не найден."
            )
        return self._rates[key]

    def update(self, rates: dict[str, Decimal], source: str) -> None:
        """Обновляет курс и дату обновления."""
        self.source = source

        for pair, rate in rates.items():
            self._rates[pair] = {
                "rate": float(rate),
                "updated_at": datetime.now().isoformat(),
            }

        self.save()

    def save(self, source: str = "ParserService") -> None:
        """Сохраняет текущие курсы в файл rates.json"""
        data = {k: v for k, v in self._rates.items()}
        data["source"] = source
        data["last_refresh"] = datetime.now().isoformat()
        self._storage.save(data)
        self.last_refresh = datetime.now()
        self.source = data["source"]

    def get_rate_pair(self, from_currency: str, to_currency: str) -> dict:
        """Возвращает прямой и обратный курс."""
        self.is_expired()
        from_currency_obj = get_currency(from_currency)
        to_currency_obj = get_currency(to_currency)
        key = f"{from_currency_obj.code}_{to_currency_obj.code}"
        if key not in self._rates:
            raise ValueError(
                f"Курс для {from_currency_obj.code}->{to_currency_obj.code} не найден."
            )
        rate_data = self._rates[key]

        direct_rate = Decimal("1") / Decimal(str(rate_data["rate"]))
        reverse_rate = rate_data["rate"]

        return {
            "from_currency": from_currency_obj.code,
            "to_currency": to_currency_obj.code,
            "direct_rate": direct_rate,
            "reverse_rate": reverse_rate,
            "updated_at": rate_data["updated_at"],
        }

    def format_rate(self, from_currency: str, to_currency: str) -> str:
        data = self.get_rate_pair(from_currency, to_currency)
        updated_at = datetime.fromisoformat(data["updated_at"]).strftime(
            "%d-%m-%Y %H:%M"
        )

        return (
            f"Курс (от {updated_at})\n"
            f"{data["from_currency"]}->{data["to_currency"]}: "
            f"{data["direct_rate"]:.8f}\n"
            f"{data["to_currency"]}->{data["from_currency"]}: "
            f"{data["reverse_rate"]}"
        )
    
    def _load(self) -> None:
        """Загружает файл rates.json"""
        raw = self._storage.load()
        self.source = raw.get("source", "Unknown")
        last_refresh_str = raw.get("last_refresh")
        self.last_refresh = datetime.fromisoformat(last_refresh_str) \
            if last_refresh_str else None

        for key, value in raw.items():
            if key in ["source", "last_refresh"]:
                continue
            self._rates[key] = {
                "rate": Decimal(str(value["rate"])),
                "updated_at": value["updated_at"],
            }

    def is_expired(self):
        """Проверяет актуальность курсов валют"""
        elapsed_seconds = (datetime.now() - self.last_refresh).total_seconds()
        if elapsed_seconds > self._ttl:
            raise RatesExpiredError()
    
    def get_rates_filter(
        self,
        currency: str | None = None,
        top: int | None = None,
        base: str | None = "USD",
    ) -> list[dict]:
        self.is_expired()
        base = (base or "USD").upper()

        if base != "USD":
            base_key = f"{base}_USD"
            if base_key not in self._rates:
                raise CurrencyNotFoundError(f"Базовая валюта {base} недоступна")
            base_rate = Decimal(str(self._rates[base_key]["rate"]))
        else:
            base_rate = Decimal("1")

        rates = []

        for pair, info in self._rates.items():
            from_code, _ = pair.split("_")

            if currency and from_code != currency.upper():
                continue

            rate_usd = Decimal(str(info["rate"]))
            rate_in_base = rate_usd / base_rate

            rates.append({
                "pair": f"{from_code}_{base}",
                "rate": rate_in_base,
                "updated_at": info["updated_at"],
            })

        if top:
            rates.sort(key=lambda x: x["rate"], reverse=True)
            rates = rates[:top]

        return rates

    def __str__(self) -> str:
        formatted = self.last_refresh.strftime("%d-%m-%Y %H:%M")
        lines = [f"Курс (источник: {self.source}, обновлено: {formatted}):"]
        for key, value in self._rates.items():
            updated_at = datetime.fromisoformat(value["updated_at"]).strftime(
                "%d-%m-%Y %H:%M"
            )
            lines.append(f"- {key}: {value["rate"]} (от {updated_at})")
        return "\n".join(lines)
