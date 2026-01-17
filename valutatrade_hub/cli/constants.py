INPUT_PROMT = "\033[35mvalutatrade> \033[0m"

COMMAND_DESCRIPTIONS = {
    "register": "Зарегистрироваться",
    "login": "Войти в систему",
    "show-portfolio": "Посмотреть свой портфель и балансы",
    "buy": "Купить валюту",
    "sell": "Продать валюту",
    "get-rate": "Получить курс валюты",
    "update-rates": "Обновить курсы валют",
    "show-rates": "Курсы валют с фильтрацией",
    "exit": "Выйти из программы",
}

COMMAND_EXAMPLES = [
    "register --username <str> --password <str>",
    "login --username <str> --password <str>",
    "show-portfolio [--base <str>]",
    "buy --currency <str> --amount <float>",
    "sell --currency <str> --amount <float>",
    "get-rate --from <str> --to <str>",
    "update-rates [--source <str>]",
    "show-rates [--top <int>] [--base <str>] [--currency <str>]",
]
