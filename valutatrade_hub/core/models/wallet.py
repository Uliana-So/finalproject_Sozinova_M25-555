from decimal import Decimal
from typing import Dict

from ..exceptions import InsufficientFundsError


class Wallet:

    def __init__(
        self,
        currency_code: str = 'USD',
        balance: Decimal = Decimal('0')
    ) -> None:
        self._currency_code = currency_code
        self._balance = balance

    @property
    def balance(self) -> Decimal:
        return Decimal(self._balance)

    @balance.setter
    def balance(self, balance: Decimal) -> None:
        self._check_amount(balance)
        self._balance = balance

    def deposit(self, amount: Decimal) -> None:
        self._check_amount(amount)
        self._balance += amount

    def withdraw(self, amount: Decimal) -> None:
        self._check_amount(amount)
        if amount > self._balance:
            raise InsufficientFundsError(self._balance, self._currency_code)
        self._balance -= amount

    def get_balance_info(self) -> Dict:
        return {
            'currency_code': self._currency_code,
            'balance': self._balance
        }
    
    @staticmethod
    def _check_amount(amount: Decimal) -> None:
        if amount <= Decimal('0'):
            raise ValueError('Баланс не может быть меньше 0.')
