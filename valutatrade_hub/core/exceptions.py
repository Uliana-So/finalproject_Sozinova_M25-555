class InsufficientFundsError(Exception):
    def __init__(self, available, code: str):
        self.available = available
        self.code = code

        super().__init__(
            f'Недостаточно средств: '
            f'доступно {available} {code}, '
        )


class CurrencyNotFoundError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(f'Неизвестная валюта {code}')


class ApiRequestError(Exception):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(
            f'Ошибка при обращении к внешнему API: {reason}'
        )
