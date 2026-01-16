from decimal import Decimal, InvalidOperation
from typing import Dict, Optional

from ...cli.manager.rate import RateManager
from ...core.currencies import get_currency
from ...core.decorators import log_action
from ...core.exceptions import CurrencyNotFoundError
from ...core.models.portfolio import Portfolio
from ...core.models.wallet import Wallet
from ...core.utils import format_balance
from ..storage import FileStorageManager


class PortfolioManager:
    """Менеджер портфелей пользователей."""

    def __init__(self, file_path: str):
        self._storage = FileStorageManager(file_path)
        self._portfolios: Dict[int, Portfolio] = {}
        self._load()

    def get_by_user_id(self, user_id: int) -> Optional[Portfolio]:
        """Возвращает портфель пользователя по его id."""
        return self._portfolios.get(user_id)

    def create_portfolio(self, user_id: int) -> Portfolio:
        """Создает портфель пользователю."""
        if user_id in self._portfolios:
            raise ValueError("Портфель уже есть у пользователя.")

        portfolio = Portfolio(user_id)
        self._portfolios[user_id] = portfolio
        self.save()
        return portfolio

    def add_currency(self, user_id: int, currency_code: str) -> Wallet:
        """Добавляет новую валюту в портфель."""
        portfolio = self._get_or_create(user_id)
        return portfolio.add_currency(currency_code)
    
    def save(self) -> None:
        """Сохраняет текущее состояние в файл portfolios.json."""
        self._storage.save(self._serialize())

    @log_action("BUY", verbose=True)
    def buy_currency(
        self,
        user_id: int,
        rate_manager: RateManager,
        currency: str,
        amount: str,
        base_currency: str,
    ) -> Dict:
        """Покупает валюту и возвращает изменения баланса в кошельке."""
        currency_obj = get_currency(currency)

        try:
            amount = Decimal(amount)
        except InvalidOperation:
            raise ValueError("amount должен быть числом")

        if amount <= 0:
            raise ValueError("amount должен быть больше 0")

        rate_manager.is_expired()
        portfolio = self.get_by_user_id(user_id)

        if not portfolio.get_wallet(currency_obj.code):
            portfolio.add_currency(currency_obj.code)

        wallet = portfolio.get_wallet(currency_obj.code)
        old_balance = wallet.balance
        wallet.deposit(amount)
        rate = rate_manager.get_rate(currency_obj.code, base_currency)

        self.save()
        return {
            "rate": rate["rate"],
            "old_balance": old_balance,
            "new_balance": wallet.balance,
        }

    @log_action("SELL", verbose=True)
    def sell_currency(
        self,
        user_id: int,
        rate_manager: RateManager,
        currency: str,
        amount: str,
        base_currency: str,
    ) -> Dict:
        """Продает валюту и возвращает изменения баланса в кошельке."""
        currency_obj = get_currency(currency)

        try:
            amount = Decimal(amount)
        except InvalidOperation:
            raise ValueError("amount должен быть числом")

        if amount <= 0:
            raise ValueError("amount должен быть больше 0")

        rate_manager.is_expired()
        portfolio = self.get_by_user_id(user_id)
        wallet = portfolio.get_wallet(currency_obj.code)

        if not wallet:
            raise CurrencyNotFoundError(currency_obj.code)

        old_balance = wallet.balance
        wallet.withdraw(amount)
        rate = rate_manager.get_rate(currency_obj.code, base_currency)

        self.save()
        return {
            "rate": rate["rate"],
            "old_balance": old_balance,
            "new_balance": wallet.balance,
        }

    def _get_or_create(self, user_id: int) -> Portfolio:
        """Создает или возвращает портфолио пользователя."""
        portfolio = self._portfolios.get(user_id)
        if portfolio is None:
            portfolio = self.create_portfolio(user_id)
        return portfolio

    def _load(self) -> None:
        """Загружает файл portfolios.json"""
        raw = self._storage.load()

        for item in raw:
            portfolio = Portfolio(item["user_id"])

            for code, balance in item["wallets"].items():
                wallet = Wallet(code, Decimal(balance))
                portfolio._wallets[code] = wallet

            self._portfolios[portfolio.user] = portfolio

    def _serialize(self) -> list[dict]:
        data = []

        for portfolio in self._portfolios.values():
            data.append(
                {
                    "user_id": portfolio.user,
                    "wallets": {
                        code: format_balance(wallet.balance)
                        for code, wallet in portfolio.wallets.items()
                    },
                }
            )

        return data
