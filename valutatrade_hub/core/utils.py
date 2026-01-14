import hashlib
import secrets
import string
from decimal import ROUND_HALF_UP, Decimal


def generate_salt(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

def hash_password(password: str, salt: str) -> str:
    value = password + salt
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def format_balance(amount: Decimal) -> str:
    """Округляет Decimal до 2 знаков после точки и возвращает строку."""
    return str(amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
