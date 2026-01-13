from decimal import Decimal
from typing import Dict

from .wallet import Wallet


class Portfolio:
    
    def __init__(self, user_id: int, wallets: Dict[str, Wallet] | None = None) -> None:
        self._user_id = user_id
        self._wallets: Dict[str, Wallet] = wallets or {}

    @property
    def user(self) -> int:
        return self._user_id

    @property
    def wallets(self) -> int:
        return self._wallets.copy()
    
    def add_currency(self, currency_code: str) -> None:
        if not self._wallets.get(currency_code, None):
            raise ValueError(f'У пользователя уже есть кошелек с валютой {currency_code}.')
        self._wallets[currency_code] = Wallet(currency_code)

    def get_total_value(base_currency: str) -> Decimal:
        # Реализовать метод get_total_value,
        # который конвертирует балансы всех валют в base_currency
        # (для упрощения можно задать фиксированные курсы в словаре exchange_rates).
        pass

    def get_wallet(self, currency_code: str):
        return self._wallets.get(currency_code, None)

    def buy_currency():
        pass

    def sell_currency():
        pass

    def __str__(self) -> str:
        if not self._wallets:
            return "Portfolio is empty."

        lines = [f"Portfolio for user {self._user_id}:"]

        for wallet in self._wallets.values():
            lines.append(
                f"- {wallet._currency_code}: {wallet._balance}"
            )

        return "\n".join(lines)
