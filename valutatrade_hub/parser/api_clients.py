from abc import ABC, abstractmethod

import requests

from ..core.exceptions import ApiRequestError
from .config import ParserConfig


class BaseApiClient(ABC):
    """
    Абстрактный клиент внешнего API курсов.
    Все реализации должны предоставлять fetch_rates() -> dict
    """
    
    @abstractmethod
    def fetch_rates(self) -> dict:
        """Возвращает словарь курсов в формате {"BTC_USD": 59337.21, ...}."""
        pass


class CoinGeckoClient(BaseApiClient):
    BASE_URL = ParserConfig.COINGECKO_URL

    def __init__(self, vs_currencies: list[str] = None):
        if vs_currencies is None:
            vs_currencies = ["usd"]
        self.vs_currencies = ",".join([c.lower() for c in vs_currencies])

    def fetch_rates(self) -> dict:
        ids = ",".join(ParserConfig.CRYPTO_ID_MAP.values())
        url = f"{self.BASE_URL}?ids={ids}&vs_currencies={self.vs_currencies}"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                raise ApiRequestError(response.status_code)
            data = response.json()
        except requests.exceptions.RequestException as e:
            raise ApiRequestError(e)

        # Приводим к стандартному формату {"BTC_USD": 59337.21}
        result = {}
        for code, coin_id in ParserConfig.CRYPTO_ID_MAP.items():
            for vs in self.vs_currencies.upper().split(","):
                rate = data.get(coin_id, {}).get(vs.lower())
                if rate is not None:
                    result[f"{code}_{vs.upper()}"] = rate
        return result


class ExchangeRateApiClient(BaseApiClient):
    BASE_URL = ParserConfig.EXCHANGERATE_API_URL

    def __init__(self, base_currency: str = "USD", api_key: str | None = None):
        self.base_currency = base_currency.upper()
        self.api_key = api_key

    def fetch_rates(self) -> dict:
        url = f"{self.BASE_URL}/{self.base_currency}"
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                raise ApiRequestError(response)
            data = response.json()
        except requests.exceptions.RequestException as e:
            raise ApiRequestError(e)

        rates = data.get("rates")
        if not rates:
            raise ApiRequestError("Неверный формат ответа от ExchangeRate API")

        # Приводим к стандартному формату {"EUR_USD": 1.0786, "BTC_USD": 59337.21}
        result = {}
        for code, rate in rates.items():
            result[f"{code.upper()}_{self.base_currency}"] = rate
        return result
