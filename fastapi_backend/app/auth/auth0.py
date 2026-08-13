from sqlalchemy.orm import Session

from app.models import User
from .jwt_handler import create_access_token


# =========================================================
# AUTH0 TOKEN VERIFICATION
# =========================================================

def verify_auth0_token(token: str):
    """
    Verify Auth0 token.

    Currently this is a placeholder.
    Real Auth0 verification can be added later.
    """

    return {
        "email": "socialuser@gmail.com",
        "name": "Social User"
    }


# =========================================================
# GET OR CREATE SOCIAL USER
# =========================================================

def get_or_create_user(
    email: str,
    name: str,
    db: Session
):

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:

        user = User(
            name=name,
            email=email,
            password="social_login",
            role="customer"
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    return user


# =========================================================
# CREATE SOCIAL LOGIN TOKEN
# =========================================================

def create_social_login_token(user):

    token = create_access_token(
        {
            "sub": user.email,
            "role": user.role
        }
    )

    return token