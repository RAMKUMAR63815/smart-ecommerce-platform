from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

def create_refresh_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(days=7)

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )