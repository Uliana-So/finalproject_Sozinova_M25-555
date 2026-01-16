from datetime import datetime
from decimal import Decimal
from typing import Dict

from ..cli.storage import FileStorageManager
from ..core.exceptions import ApiRequestError
from .api_clients import CoinGeckoClient, ExchangeRateApiClient
from .config import ParserConfig


class RateUpdater:
    def __init__(self, file_path: str):
        self._storage = FileStorageManager(file_path)
        self._clients = {
            "CoinGecko": CoinGeckoClient(ParserConfig.BASE_CURRENCY),
            "ExchangeRate-API": ExchangeRateApiClient(ParserConfig.BASE_CURRENCY)
        }

    def run_update(self, source: str | None = None) -> int:
        """Обновляет курсы. Если source указан — обновляет только его."""
        collected: Dict[str, Decimal] = {}
        
        if source and source not in self._clients.keys():
            raise ValueError(f"Неизвестный источник '{source}'")

        for name, client in self._clients.items():
            if source and name != source:
                continue

            try:
                rates = client.fetch_rates()
            except Exception as exc:
                raise ApiRequestError(str(exc))

            for pair, rate in rates.items():
                from_currency, to_currency = pair.split("_")

                rate_decimal = str(rate)
                self._append_journal(
                    from_currency=from_currency,
                    to_currency=to_currency,
                    rate=rate_decimal,
                    source=name,
                )

                collected[pair] = rate_decimal
            print(f"Обновлены курсы из {name}: {len(rates)}")

        return collected

    def _append_journal(self,
        from_currency: str,
        to_currency: str,
        rate: str,
        source: str,
        meta: dict | None = None
    ) -> None:
        """Добавляет новую запись в exchange-rate.json."""
        timestamp = datetime.now().isoformat()
        entry_id = f"{from_currency}_{to_currency}_{timestamp}"

        entry = {
            "id": entry_id,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": float(rate),
            "timestamp": timestamp,
            "source": source,
            "meta": meta or {},
        }

        try:
            journal = self._storage.load()
        except FileNotFoundError:
            journal = []

        journal.append(entry)
        self._storage.save(journal)
