import hashlib
import secrets
import string


def generate_salt(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

def hash_password(password: str, salt: str) -> str:
    value = password + salt
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
