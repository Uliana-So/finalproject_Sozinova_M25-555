from decimal import Decimal, InvalidOperation

from ..cli.manager.rate import RateManager
from .models.portfolio import Portfolio


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
        raise ValueError(f'Кошелёк {currency} не найден')

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
