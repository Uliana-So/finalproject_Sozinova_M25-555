import logging
from functools import wraps

logger = logging.getLogger(__name__)

def log_action(action: str, verbose: bool = False):
    """
    Декоратор для логирования бизнес-операций.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            context = {}

            context["action"] = action
            context["user"] = getattr(kwargs.get("user"), "username", None)
            context["currency"] = kwargs.get("currency")
            context["amount"] = kwargs.get("amount")
            context["base"] = kwargs.get("base_currency")

            try:
                result = func(*args, **kwargs)

                logger.info(
                    "%s user=%s currency=%s amount=%s base=%s result=OK",
                    action,
                    context["user"],
                    context["currency"],
                    context["amount"],
                    context["base"],
                )

                return result

            except Exception as exc:
                logger.error(
                    "%s user=%s currency=%s amount=%s result=ERROR "
                    "error_type=%s error_message=%s",
                    action,
                    context["user"],
                    context["currency"],
                    context["amount"],
                    type(exc).__name__,
                    str(exc),
                )
                raise

        return wrapper

    return decorator
