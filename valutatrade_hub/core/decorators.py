import logging
from functools import wraps
from inspect import signature

logger = logging.getLogger(__name__)

def log_action(action: str, verbose: bool = False):
    """Декоратор для логирования бизнес-операций."""

    def decorator(func):
        sig = signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()

            params = bound.arguments

            context = {
                "action": action,
                "user": getattr(params.get("user"), "username", None)
                        or params.get("user_id"),
                "currency": params.get("currency"),
                "amount": params.get("amount"),
                "base": params.get("base_currency"),
            }

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
