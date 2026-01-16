from abc import ABC, abstractmethod

from .exceptions import CurrencyNotFoundError


class Currency(ABC):
    """
    Абстрактная валюта. Определяет единый интерфейс
    для всех типов валют (фиатных и крипто).
    """

    def __init__(self, name: str, code: str):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Имя валюты не может быть пустым.")

        if (
            not isinstance(code, str)
            or not code.isupper()
            or not (2 <= len(code) <= 5)
            or " " in code
        ):
            raise ValueError(
                "Код валюты должен быть большими буквами, "
                "без пробелов, длинна 2-5 символов."
            )

        self.name: str = name
        self.code: str = code

    @abstractmethod
    def get_display_info(self) -> str:
        """Строковое представление валюты для UI/логов."""
        pass


class FiatCurrency(Currency):
    """Фиатные валюты."""

    def __init__(self, name: str, code: str, issuing_country: str):
        super().__init__(name, code)

        if not isinstance(issuing_country, str) or not issuing_country.strip():
            raise ValueError("Страна использования не может быть пустой.")

        self.issuing_country: str = issuing_country

    def get_display_info(self) -> str:
        return (
            f"[FIAT] {self.code} — {self.name} "
            f"(Issuing: {self.issuing_country})"
        )


class CryptoCurrency(Currency):
    """Криптовалюты."""

    def __init__(
        self,
        name: str,
        code: str,
        algorithm: str,
        market_cap: float,
    ):
        super().__init__(name, code)

        if not isinstance(algorithm, str) or not algorithm.strip():
            raise ValueError("Алгоритм не должен быть пустым.")

        if not isinstance(market_cap, (int, float)) or market_cap < 0:
            raise ValueError("Рыночная капитализация должна быть числом "
                             "и не может быть меньше 0.")

        self.algorithm: str = algorithm
        self.market_cap: float = float(market_cap)

    def get_display_info(self) -> str:
        return (
            f"[CRYPTO] {self.code} — {self.name} "
            f"(Algo: {self.algorithm}, MCAP: {self.market_cap:.2e})"
        )


_CURRENCY_REGISTRY: dict[str, Currency] = {
    "USD": FiatCurrency("US Dollar", "USD", "United States"),
    "EUR": FiatCurrency("Euro", "EUR", "Eurozone"),
    "RUB": FiatCurrency("Russian Ruble", "RUB", "Russia"),
    "BTC": CryptoCurrency("Bitcoin", "BTC", "SHA-256", 1.12e12),
    "ETH": CryptoCurrency("Ethereum", "ETH", "Ethash", 3.5e11),
}

def get_currency(code: str) -> Currency:
    code = code.upper()

    try:
        return _CURRENCY_REGISTRY[code]
    except KeyError:
        raise CurrencyNotFoundError(code)
