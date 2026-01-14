import shlex

from valutatrade_hub.infra.settings import SettingsLoader

from ..core.usecases import buy_currency, sell_currency
from .constants import (
    COMMAND_DESCRIPTIONS,
    INPUT_PROMT,
)
from .manager.portfolio import PortfolioManager
from .manager.rate import RateManager
from .manager.user import UserManager

settings = SettingsLoader()


class CLIInterface:

    def __init__(self) -> None:
        self._user = None
        self.user_manager = UserManager(settings.get("users_file"))
        self.portfolio_manager = PortfolioManager(settings.get("portfolios_file"))
        self.rate_manager = RateManager(
            settings.get("rates_file"),
            ttl=settings.get("rates_ttl_seconds")
        )

    def run(self) -> None:
        self.show_help()

        while True:
            try:
                user_input = input(INPUT_PROMT).strip()
                self.proses_command(user_input)
            except (ValueError, PermissionError) as e:
                print('\033[3m\033[31m{}\033[0m'.format(e))
            except (KeyboardInterrupt, EOFError):
                break

    def proses_command(self, user_input: str) -> None:
        if not user_input:
            raise ValueError('Введите команду (help - список команд).')

        cmd = shlex.split(user_input)

        match cmd[0].lower():
            case 'register':
                if len(cmd) == 5 and cmd[1] == '--username' and cmd[3] == '--password':
                    self.register(cmd[2], cmd[4])
                else:
                    raise ValueError(
                        'Неверный формат команды.\nИспользование: '
                        'register --username <USERNAME> --password <PASSWORD>'
                    )

            case 'login':
                if len(cmd) == 5 and cmd[1] == '--username' and cmd[3] == '--password':
                    self.login(cmd[2], cmd[4])
                else:
                    raise ValueError(
                        'Неверный формат команды.\nИспользование: '
                        'login --username <USERNAME> --password <PASSWORD>'
                    )

            case 'show-portfolio':
                if len(cmd) == 3 and cmd[1] == '--base':
                    self.show_portfolio(cmd[2])
                elif len(cmd) == 1:
                    self.show_portfolio()
                else:
                    raise ValueError(
                        'Неверный формат команды.\nИспользование: '
                        'show-portfolio --base <CURRENCY>'
                    )

            case 'buy':
                if len(cmd) == 5 and cmd[1] == '--currency' and cmd[3] == '--amount':
                    self.buy(cmd[2], cmd[4])
                else:
                    raise ValueError(
                        'Неверный формат команды.\nИспользование: '
                        'buy --currency <CURRENCY> --amount <AMOUNT>'
                    )
            
            case 'sell':
                if len(cmd) == 5 and cmd[1] == '--currency' and cmd[3] == '--amount':
                    self.sell(cmd[2], cmd[4])
                else:
                    raise ValueError(
                        'Неверный формат команды.\nИспользование: '
                        'sell --currency <CURRENCY> --amount <AMOUNT>'
                    )
            
            case 'get-rate':
                if len(cmd) == 5 and cmd[1] == '--from' and cmd[3] == '--to':
                    self.get_rate(cmd[2], cmd[4])
                else:
                    raise ValueError(
                        'Неверный формат команды.\nИспользование: '
                        'get-rate --from <CURRENCY> --to <CURRENCY>'
                    )

            case 'help':
                self.show_help()

            case 'exit':
                exit()

            case _:
                raise ValueError(
                    f'Неверный формат команды: {user_input}\n'
                    'Введите команду (help - список команд).'
                )

    def register(self, username: str, password: str) -> None:
        self.user_manager.create(username, password)
        print(f'Пользователь {self._user.username} зарегистрирован.')
        self.portfolio_manager.create_portfolio(self._user.user_id)

    def login(self, username: str, password: str) -> None:
        self._user = self.user_manager.authenticate(username, password)
        print(f'Вы вошли как {self._user.username}')

    def show_portfolio(self, base_currency: str | None = 'USD') -> None:
        if self._user is None:
            raise PermissionError('Сначала выполните login.')

        portfolio = self.portfolio_manager.get_by_user_id(self._user._user_id)
        print(portfolio.format_portfolio(
            self._user.username, self.rate_manager, base_currency
        ))

    def buy(self, currency, amount) -> None:
        if self._user is None:
            raise PermissionError('Сначала выполните login.')

        portfolio = self.portfolio_manager.get_by_user_id(self._user._user_id)
        result = buy_currency(
            portfolio=portfolio,
            rate_manager=self.rate_manager,
            currency=currency,
            amount=amount,
        )
        self.portfolio_manager.save()
        print(result)

    def sell(self, currency, amount) -> None:
        if self._user is None:
            raise PermissionError('Сначала выполните login.')
    
        portfolio = self.portfolio_manager.get_by_user_id(self._user._user_id)
        result = sell_currency(
            portfolio=portfolio,
            rate_manager=self.rate_manager,
            currency=currency,
            amount=amount,
        )
        self.portfolio_manager.save()
        print(result)

    def get_rate(self, from_currency, to_currency) -> None:
        rate = self.rate_manager.format_rate(from_currency, to_currency)
        print(rate)

    def show_help(self) -> None:
        print('\tДоступные команды:')
        for i, v in COMMAND_DESCRIPTIONS.items():
            print(f'{i:<16} — {v}')
