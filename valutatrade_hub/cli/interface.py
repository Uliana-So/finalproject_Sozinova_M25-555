import shlex

from .constants import COMMAND_DESCRIPTIONS, INPUT_PROMT, USERS_FILE, PORTFOLIOS_FILE, RATES_FILE
from .manager.user import UserManager
from .manager.portfolio import PortfolioManager
from .manager.rate import RateManager
from ..core.models.portfolio import Portfolio
from ..core.models.wallet import Wallet


class CLIInterface:

    def __init__(self) -> None:
        self._user = None
        self.user_manager = UserManager(USERS_FILE)
        self.portfolio_manager = PortfolioManager(PORTFOLIOS_FILE)
        self.rate_manager = RateManager(RATES_FILE)

    def run(self):
        self.show_help()

        while True:
            try:
                user_input = input(INPUT_PROMT).strip()
                self.proses_command(user_input)
            except (ValueError) as e:
                print(e)
            except (KeyboardInterrupt, EOFError):
                break

    def proses_command(self, user_input: str):
        if not user_input:
            print("Введите команду (help - список команд)")
            return

        cmd = shlex.split(user_input)

        match cmd[0].lower():
            case 'register':
                if len(cmd) == 5 and cmd[1] == '--username' and cmd[3] == '--password':
                    self.register(cmd[2], cmd[4])
                else:
                    raise ValueError()

            case 'login':
                if len(cmd) == 5 and cmd[1] == '--username' and cmd[3] == '--password':
                    self.login(cmd[2], cmd[4])
                else:
                    raise ValueError('here login')

            case 'show-portfolio':
                self.show_portfolio()

            case 'buy':
                pass
            
            case 'sell':
                pass
            
            case 'get-rate':
                if len(cmd) == 5 and cmd[1] == '--from' and cmd[3] == '--to':
                    self.get_rate(cmd[2], cmd[4])
                else:
                    raise ValueError(f'Курс {cmd[2]}->{cmd[4]} недоступен. Повторите попытку позже.')
            
            case 'help':
                self.show_help()
            case 'exit' | 'quit':
                exit()
            case _:
                raise ValueError(user_input)

    def register(self, username: str, password: str):
        self.user_manager.create(username, password)
        print(f"Пользователь {self._user.username} зарегистрирован.")
        self.portfolio_manager.create_portfolio(self._user.user_id)

    def login(self, username: str, password: str):
        if not self.user_manager.get_by_username(username):
            raise ValueError("Неверный логин или пароль.")

        self._user = self.user_manager.authenticate(username, password)
        print(f"Вы вошли как {self._user.username}")

    def show_portfolio(self):
        if self._user is None:
            raise PermissionError("Сначала выполните login.")

        portfolio = self.portfolio_manager.get_by_user_id(
            self._user._user_id
        )
        print(portfolio)

    def buy(self):
        if self._user is None:
            raise PermissionError("Сначала выполните login.")

    def sell(self):
        if self._user is None:
            raise PermissionError("Сначала выполните login.")
    
    def get_rate(self, from_currency, to_currency):
        rate = self.rate_manager.format_rate(from_currency, to_currency)
        print(rate)

    def show_help(self):
        print("\tДоступные команды:")
        for i, v in COMMAND_DESCRIPTIONS.items():
            print(f"{i:<16} — {v}")
