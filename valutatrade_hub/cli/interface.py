import shlex

from ..core.exceptions import (
    ApiRequestError,
    CurrencyNotFoundError,
    InsufficientFundsError,
    InvalidCommandFormatError,
    RatesExpiredError,
)
from ..infra.settings import SettingsLoader
from ..parser.config import ParserConfig
from ..parser.updater import RateUpdater
from .constants import (
    COMMAND_DESCRIPTIONS,
    COMMAND_EXAMPLES,
    INPUT_PROMT,
)
from .manager.portfolio import PortfolioManager
from .manager.rate import RateManager
from .manager.user import UserManager

settings = SettingsLoader()


class CLIInterface:
    """Командный интерфейс приложения."""

    def __init__(self) -> None:
        self._user = None
        self.user_manager = UserManager(settings.get("users_file"))
        self.portfolio_manager = PortfolioManager(settings.get("portfolios_file"))
        self.rate_manager = RateManager(
            settings.get("rates_file"),
            ttl=settings.get("rates_ttl_seconds")
        )
        self.rate_updater = RateUpdater(ParserConfig.EXCHANGE_FILE_PATH)

    def run(self) -> None:
        """Основной цикл."""
        self.show_help()

        while True:
            try:
                user_input = input(INPUT_PROMT).strip()
                self.proses_command(user_input)
            except (
                ValueError,
                PermissionError,
                InsufficientFundsError,
                CurrencyNotFoundError,
                ApiRequestError,
                RatesExpiredError,
                InvalidCommandFormatError,
            ) as e:
                print("\033[3m\033[31m{}\033[0m".format(e))
            except (KeyboardInterrupt, EOFError):
                break

    def proses_command(self, user_input: str) -> None:
        """Обрабатывает пользовательскую команду и вызывает необходимый метод."""
        if not user_input:
            raise ValueError("Введите команду (help - список команд).")

        cmd = shlex.split(user_input)

        match cmd[0].lower():
            case "register":
                if len(cmd) == 5 and cmd[1] == "--username" and cmd[3] == "--password":
                    self.register(cmd[2], cmd[4])
                else:
                    raise InvalidCommandFormatError(user_input)

            case "login":
                if len(cmd) == 5 and cmd[1] == "--username" and cmd[3] == "--password":
                    self.login(cmd[2], cmd[4])
                else:
                    raise InvalidCommandFormatError(user_input)

            case "show-portfolio":
                if len(cmd) == 3 and cmd[1] == "--base":
                    self.show_portfolio(cmd[2])
                elif len(cmd) == 1:
                    self.show_portfolio()
                else:
                    raise InvalidCommandFormatError(user_input)

            case "buy":
                if len(cmd) == 5 and cmd[1] == "--currency" and cmd[3] == "--amount":
                    self.buy(cmd[2], cmd[4])
                else:
                    raise InvalidCommandFormatError(user_input)
            
            case "sell":
                if len(cmd) == 5 and cmd[1] == "--currency" and cmd[3] == "--amount":
                    self.sell(cmd[2], cmd[4])
                else:
                    raise InvalidCommandFormatError(user_input)
            
            case "get-rate":
                if len(cmd) == 5 and cmd[1] == "--from" and cmd[3] == "--to":
                    self.get_rate(cmd[2], cmd[4])
                else:
                    raise InvalidCommandFormatError(user_input)

            case "update-rates":
                if len(cmd) == 3 and cmd[1] == "--source":
                    self.update_rates(cmd[2])
                elif len(cmd) == 1:
                    self.update_rates()
                else:
                    raise InvalidCommandFormatError(user_input)

            case "show-rates":
                try:
                    self.show_rates(cmd[1:])
                except (IndexError, TypeError, ValueError):
                    raise InvalidCommandFormatError(user_input)

            case "help":
                self.show_help()

            case "exit":
                exit()

            case _:
                raise InvalidCommandFormatError(user_input)

    def register(self, username: str, password: str) -> None:
        """Регистрация пользователя."""
        self.user_manager.create(username, password)
        print(f"Пользователь {self._user.username} зарегистрирован.")
        self.portfolio_manager.create_portfolio(self._user.user_id)

    def login(self, username: str, password: str) -> None:
        """Аутентификация пользователя."""
        self._user = self.user_manager.authenticate(username, password)
        print(f"Вы вошли как {self._user.username}")

    def show_portfolio(self, base_currency: str | None = "USD") -> None:
        """Отображает портфель пользователя."""
        if self._user is None:
            raise PermissionError("Сначала выполните login.")

        portfolio = self.portfolio_manager.get_by_user_id(self._user.user_id)
        print(portfolio.format_portfolio(
            self._user.username, self.rate_manager, base_currency
        ))

    def buy(self, currency, amount) -> None:
        """Покупка валюты."""
        if self._user is None:
            raise PermissionError("Сначала выполните login.")

        base_currency = settings.get("base_currency")
        result = self.portfolio_manager.buy_currency(
            self._user.user_id,
            self.rate_manager,
            currency,
            amount,
            base_currency
        )

        print(
            f"Покупка выполнена: {amount} {currency} "
            f"по курсу {result["rate"]} {base_currency}/{currency}\n"
            f"Изменения в портфеле:\n"
            f"- {currency}: {result["old_balance"]} -> {result["new_balance"]}"
        )

    def sell(self, currency, amount) -> None:
        """Продажа валюты."""
        if self._user is None:
            raise PermissionError("Сначала выполните login.")
    
        base_currency = settings.get("base_currency")
        result = self.portfolio_manager.sell_currency(
            self._user.user_id,
            self.rate_manager,
            currency,
            amount,
            base_currency
        )
        print(
            f"Продажа выполнена: {amount} {currency} "
            f"по курсу {result["rate"]} {base_currency}/{currency}\n"
            f"Изменения в портфеле:\n"
            f"- {currency}: {result["old_balance"]} -> {result["new_balance"]}"
        )
    
    def get_rate(self, from_currency, to_currency) -> None:
        """Возвращает курс валюты."""
        rate = self.rate_manager.format_rate(from_currency, to_currency)
        print(rate)

    def update_rates(self, source: str | None = None):
        """Обновляет курсы валют."""
        print("Курсы начали обновляться...")
        rates = self.rate_updater.run_update(source)
        self.rate_manager.update(rates=rates,source="")
        formatted = self.rate_manager.last_refresh.strftime("%d-%m-%Y %H:%M")
        print(f"Курсы успешно обновлены. Всего обновлено: {len(rates)}. "
              f"Последнее обновление: {formatted}")

    def show_rates(self, arg: list | None):
        """Возвращает курс валюты с возможностью фильтрации."""
        currency = arg[arg.index("--currency") + 1] if "--currency" in arg else None
        top = int(arg[arg.index("--top") + 1]) if "--top" in arg else None
        base = arg[arg.index("--base") + 1] if "--base" in arg else None

        rates = self.rate_manager.get_rates_filter(currency, top, base)
        if not rates:
            print("Курсы не найдены.")
            return
        
        formatted = self.rate_manager.last_refresh.strftime("%d-%m-%Y %H:%M")
        print(f"Курсы валют из кэша (от {formatted}):")
        for r in rates:
            print(f"- {r['pair']}: {r['rate']}")

    def show_help(self) -> None:
        """Отображает доступные команды и примеры их использования."""
        print("\tДоступные команды:")
        for i, v in COMMAND_DESCRIPTIONS.items():
            print(f"{i:<16} — {v}")

        print("\n\tПримеры команд:")
        print("\n".join(COMMAND_EXAMPLES))
