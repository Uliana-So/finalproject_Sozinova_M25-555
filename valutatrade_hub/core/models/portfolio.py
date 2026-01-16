from decimal import Decimal
from typing import Dict

from ...cli.manager.rate import RateManager
from .wallet import Wallet


class Portfolio:
    """Портфель пользователя - агрегатор всех валютных кошельков."""
    
    def __init__(self, user_id: int, wallets: Dict[str, Wallet] | None = None) -> None:
        self._user_id = user_id
        self._wallets: Dict[str, Wallet] = wallets or {}

    @property
    def user(self) -> int:
        return self._user_id

    @property
    def wallets(self) -> Dict[str, Wallet]:
        return self._wallets.copy()
    
    def add_currency(self, currency_code: str) -> None:
        """Добавление пользователю кошелька."""
        if self._wallets.get(currency_code, None):
            raise ValueError(
                f"У пользователя уже есть кошелек с валютой '{currency_code}'."
            )

        self._wallets[currency_code] = Wallet(currency_code)

    def get_wallet(self, currency_code: str):
        """Возвращает кошелек."""
        return self._wallets.get(currency_code, None)

    def format_portfolio(
        self,
        username: str,
        rate_manager: RateManager,
        base_currency: str
    ) -> str:
        """Возвращает строку с полной информацией по портфелю."""
        if not self.wallets:
            return "Портфель пуст."

        lines = [f"Портфель пользователя {username} (валюта: {base_currency}):"]
        total = Decimal("0")

        for wallet in self.wallets.values():
            amount = wallet.balance
            currency = wallet._currency_code

            if currency == base_currency:
                converted = amount
                rate_info = "без конвертации"
            else:
                rate = rate_manager.get_rate(currency.code, base_currency)
                converted = amount * Decimal(str(rate["rate"]))
                rate_info = f"курс {base_currency}->{currency.code}: {rate["rate"]:.4f}"

            total += converted

            lines.append(
                f"- {currency.code}: {amount:.2f} -> {converted:.2f} "
                f"{base_currency} ({rate_info})"
            )

        lines.append(f"\nИтого: {total:.2f} {base_currency}")
        return "\n".join(lines)
