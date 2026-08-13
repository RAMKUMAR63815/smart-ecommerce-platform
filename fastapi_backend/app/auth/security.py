from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

pwd_context = PasswordHasher()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    try:
        return pwd_context.verify(
            hashed_password,
            plain_password
        )
    except VerifyMismatchError:
        return False
    except Exception:
        return False