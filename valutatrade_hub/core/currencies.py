from ..core.models.currency import (
    CryptoCurrency,
    Currency,
    FiatCurrency,
)
from .exceptions import CurrencyNotFoundError

_CURRENCY_REGISTRY: dict[str, Currency] = {
    "USD": FiatCurrency(
        name="US Dollar",
        code="USD",
        issuing_country="United States",
    ),
    "EUR": FiatCurrency(
        name="Euro",
        code="EUR",
        issuing_country="Eurozone",
    ),
    "BTC": CryptoCurrency(
        name="Bitcoin",
        code="BTC",
        algorithm="SHA-256",
        market_cap=1.12e12,
    ),
    "ETH": CryptoCurrency(
        name="Ethereum",
        code="ETH",
        algorithm="Ethash",
        market_cap=4.5e11,
    ),
}


def get_currency(code: str) -> Currency:
    if not isinstance(code, str):
        raise CurrencyNotFoundError(code)

    code = code.upper()

    try:
        return _CURRENCY_REGISTRY[code]
    except KeyError:
        raise CurrencyNotFoundError(code)
