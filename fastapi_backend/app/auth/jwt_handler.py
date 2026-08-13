from datetime import datetime, timedelta

from jose import jwt


# =========================================================
# JWT CONFIGURATION
# =========================================================

SECRET_KEY = "mysecretkey123"
ALGORITHM = "HS256"


# =========================================================
# ACCESS TOKEN
# =========================================================

def create_access_token(data: dict):

    payload = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=30
    )

    payload.update({
        "exp": expire
    })

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# =========================================================
# REFRESH TOKEN
# =========================================================

def create_refresh_token(data: dict):

    payload = data.copy()

    expire = datetime.utcnow() + timedelta(
        days=7
    )

    payload.update({
        "exp": expire
    })

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token