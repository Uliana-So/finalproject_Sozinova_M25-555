from abc import ABC, abstractmethod


class Currency(ABC):
    """
    Абстрактная валюта. Определяет единый интерфейс
    для всех типов валют (фиатных и крипто).
    """

    def __init__(self, name: str, code: str):
        # Валидация name
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Currency name must be a non-empty string")

        # Валидация code
        if (
            not isinstance(code, str)
            or not code.isupper()
            or not (2 <= len(code) <= 5)
            or " " in code
        ):
            raise ValueError(
                "Currency code must be uppercase, 2–5 characters, without spaces"
            )

        self.name: str = name
        self.code: str = code

    @abstractmethod
    def get_display_info(self) -> str:
        """Строковое представление валюты для UI/логов."""
        pass


class FiatCurrency(Currency):
    def __init__(self, name: str, code: str, issuing_country: str):
        super().__init__(name, code)

        if not isinstance(issuing_country, str) or not issuing_country.strip():
            raise ValueError("issuing_country must be a non-empty string")

        self.issuing_country: str = issuing_country

    def get_display_info(self) -> str:
        return (
            f"[FIAT] {self.code} — {self.name} "
            f"(Issuing: {self.issuing_country})"
        )


class CryptoCurrency(Currency):
    def __init__(
        self,
        name: str,
        code: str,
        algorithm: str,
        market_cap: float,
    ):
        super().__init__(name, code)

        if not isinstance(algorithm, str) or not algorithm.strip():
            raise ValueError("algorithm must be a non-empty string")

        if not isinstance(market_cap, (int, float)) or market_cap < 0:
            raise ValueError("market_cap must be a non-negative number")

        self.algorithm: str = algorithm
        self.market_cap: float = float(market_cap)

    def get_display_info(self) -> str:
        return (
            f"[CRYPTO] {self.code} — {self.name} "
            f"(Algo: {self.algorithm}, MCAP: {self.market_cap:.2e})"
        )
