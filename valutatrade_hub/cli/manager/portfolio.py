from decimal import Decimal
from typing import Dict, Optional

from ...core.models.portfolio import Portfolio
from ...core.models.wallet import Wallet
from ..storage import FileStorageManager


class PortfolioManager:
    """Менеджер портфелей пользователей."""

    def __init__(self, file_path: str):
        self._storage = FileStorageManager(file_path)
        self._portfolios: Dict[int, Portfolio] = {}
        self._load()

    def get_by_user_id(self, user_id: int) -> Optional[Portfolio]:
        print(self._portfolios)
        return self._portfolios.get(user_id)

    def create_portfolio(self, user_id: int) -> Portfolio:
        if user_id in self._portfolios:
            raise ValueError("Portfolio already exists for this user")

        portfolio = Portfolio(user_id=user_id)
        self._portfolios[user_id] = portfolio
        self.save()
        return portfolio

    def add_currency(self, user_id: int, currency_code: str) -> Wallet:
        portfolio = self._get_or_create(user_id)
        return portfolio.add_currency(currency_code)
    
    def save(self) -> None:
        self._storage.save(self._serialize())

    def _get_or_create(self, user_id: int) -> Portfolio:
        portfolio = self._portfolios.get(user_id)
        if portfolio is None:
            portfolio = self.create_portfolio(user_id)
        return portfolio

    def _load(self) -> None:
        raw = self._storage.load()

        for item in raw:
            portfolio = Portfolio(item["user_id"])

            for code, balance in item["wallets"].items():
                wallet = Wallet(code, Decimal(balance))
                portfolio._wallets[code] = wallet

            self._portfolios[portfolio._user_id] = portfolio

    def _serialize(self) -> list[dict]:
        data = []

        for portfolio in self._portfolios.values():
            data.append(
                {
                    "user_id": portfolio._user_id,
                    "wallets": {
                        code: str(wallet._balance)
                        for code, wallet in portfolio._wallets.items()
                    },
                }
            )

        return data
