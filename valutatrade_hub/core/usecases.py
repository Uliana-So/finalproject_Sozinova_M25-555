from decimal import Decimal, InvalidOperation

from ..cli.manager.rate import RateManager
from ..infra.settings import SettingsLoader
from ..core.decorators import log_action
from .currencies import get_currency
from .exceptions import ApiRequestError, CurrencyNotFoundError
from .models.portfolio import Portfolio

settings = SettingsLoader()

BASE_CURRENCY = settings.get("default_base_currency", "USD")


@log_action("BUY", verbose=True)
def buy_currency(
    portfolio: Portfolio,
    rate_manager: RateManager,
    currency: str,
    amount: str,
    base_currency: str = 'USD',
) -> str:
    if not currency.isalpha() or len(currency) != 3:
        raise ValueError(f'Неверный код валюты {currency}')

    currency = currency.upper()

    try:
        amount = Decimal(amount)
    except InvalidOperation:
        raise ValueError('amount должен быть числом')

    if amount <= 0:
        raise ValueError('amount должен быть больше 0')

    if not portfolio.get_wallet(currency):
        portfolio.add_currency(currency)

    wallet = portfolio.get_wallet(currency)

    wallet.deposit(amount)

    rate = rate_manager.get_rate(currency, base_currency)
    cost = amount * rate

    return (
        f'Куплено {amount} {currency}\n'
        f'Курс {currency}->{base_currency}: {rate}\n'
        f'Стоимость: {cost:.2f} {base_currency}'
    )


@log_action("SELL", verbose=True)
def sell_currency(
    portfolio: Portfolio,
    rate_manager: RateManager,
    currency: str,
    amount: str,
    base_currency: str = 'USD',
) -> str:
    if not currency or not currency.isalpha() or len(currency) != 3:
        raise ValueError(f'Неверный код валюты {currency}')

    currency = currency.upper()

    try:
        amount = Decimal(amount)
    except InvalidOperation:
        raise ValueError('amount должен быть числом')

    if amount <= 0:
        raise ValueError('amount должен быть больше 0')

    wallet = portfolio.get_wallet(currency)
    if not wallet:
        raise CurrencyNotFoundError(currency)

    wallet.withdraw(amount)

    rate = rate_manager.get_rate(currency, base_currency)
    credited = amount * rate

    if not portfolio.get_wallet(base_currency):
        portfolio.add_currency(base_currency)

    portfolio.get_wallet(base_currency).deposit(credited)

    if credited:
        return (
            f'Продано {amount} {currency}\n'
            f'Начислено: {credited:.2f} {base_currency}'
        )

    return f'Продано {amount} {currency}'


def get_rate(from_code: str, to_code: str, rate_manager):
    from_currency = get_currency(from_code)
    to_currency = get_currency(to_code)

    settings = SettingsLoader()
    ttl = settings.get("RATES_TTL_SECONDS")

    rate = rate_manager.get_rate(from_currency.code, to_currency.code)

    if rate.is_expired(ttl):
        try:
            rate_manager.refresh()  # заглушка / API
            rate = rate_manager.get_rate(from_currency.code, to_currency.code)
        except Exception as exc:
            raise ApiRequestError(str(exc))

    return rate
