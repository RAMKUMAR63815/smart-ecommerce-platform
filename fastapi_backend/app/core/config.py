from dotenv import load_dotenv
import os

# Load variables from .env
load_dotenv()


# =========================
# DATABASE
# =========================

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")


# =========================
# JWT
# =========================

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
)


# =========================
# STRIPE
# =========================

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


# =========================
# VALIDATION
# =========================

if not DB_USER:
    raise ValueError("DB_USER is not configured")

if not DB_NAME:
    raise ValueError("DB_NAME is not configured")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not configured")

if not STRIPE_SECRET_KEY:
    raise ValueError("STRIPE_SECRET_KEY is not configured")

if STRIPE_SECRET_KEY == "your_stripe_secret_key":
    raise ValueError(
        "STRIPE_SECRET_KEY is still using the placeholder value"
    )