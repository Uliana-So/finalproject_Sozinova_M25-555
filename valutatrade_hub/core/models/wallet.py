from decimal import Decimal
from typing import Dict

from ..exceptions import InsufficientFundsError


class Wallet:
    """Кошелек пользователя для одной валюты."""

    def __init__(
        self,
        currency_code: str = "USD",
        balance: Decimal = Decimal("0")
    ) -> None:
        self._currency_code = currency_code
        self._balance = balance

    @property
    def balance(self) -> Decimal:
        return Decimal(self._balance)

    @balance.setter
    def balance(self, balance: Decimal) -> None:
        self._balance = balance

    def deposit(self, amount: Decimal) -> None:
        """Пополнение кошелька."""
        self._balance += amount

    def withdraw(self, amount: Decimal) -> None:
        """Снятие средств с кошелька."""
        if amount > self._balance:
            raise InsufficientFundsError(self._balance, self._currency_code)
        self._balance -= amount

    def get_balance_info(self) -> Dict:
        """Возвращает информацию о кошельке."""
        return {
            "currency_code": self._currency_code,
            "balance": self._balance
        }
