from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from fastapi.security import OAuth2PasswordRequestForm

from jose import jwt, JWTError

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User
from app.schemas import UserRegister

from .security import (
    hash_password,
    verify_password
)

from .auth0 import (
    verify_auth0_token,
    get_or_create_user,
    create_social_login_token
)

from .jwt_handler import (
    create_access_token,
    create_refresh_token
)

from app.dependencies import (
    get_current_user
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# =========================================================
# JWT CONFIGURATION
# =========================================================

SECRET_KEY = "mysecretkey123"
ALGORITHM = "HS256"


# =========================================================
# DATABASE SESSION
# =========================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# =========================================================
# REGISTER
# =========================================================

@router.post("/register")
def register(
    user: UserRegister,
    db: Session = Depends(get_db)
):

    existing = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role="customer"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User Registered Successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role
        }
    }


# =========================================================
# LOGIN
# =========================================================

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    db_user = (
        db.query(User)
        .filter(User.email == form_data.username)
        .first()
    )

    if not db_user:

        raise HTTPException(
            status_code=401,
            detail="Invalid Email"
        )

    if not verify_password(
        form_data.password,
        db_user.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid Password"
        )

    # Create access token
    access_token = create_access_token(
        {
            "sub": db_user.email,
            "role": db_user.role
        }
    )

    # Create refresh token
    refresh_token = create_refresh_token(
        {
            "sub": db_user.email,
            "role": db_user.role
        }
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "role": db_user.role
        }
    }


# =========================================================
# REFRESH TOKEN
# =========================================================

@router.post("/refresh")
def refresh_token_endpoint(
    refresh_token: str,
    db: Session = Depends(get_db)
):

    try:

        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = payload.get("sub")

        if not email:

            raise HTTPException(
                status_code=401,
                detail="Invalid Refresh Token"
            )

        # Find user
        user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if user is None:

            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        # Create new access token
        access_token = create_access_token(
            {
                "sub": user.email,
                "role": user.role
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid Refresh Token"
        )


# =========================================================
# CURRENT USER
# =========================================================

@router.get("/me")
def me(
    current_user: User = Depends(get_current_user)
):

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role
    }


# =========================================================
# AUTH0 SOCIAL LOGIN
# =========================================================

@router.post("/social-login")
def social_login(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Google/Facebook
        ↓
    Auth0
        ↓
    Verify Token
        ↓
    Create User
        ↓
    Return JWT
    """

    social_user = verify_auth0_token(
        token
    )

    user = get_or_create_user(
        email=social_user["email"],
        name=social_user["name"],
        db=db
    )

    jwt_token = create_social_login_token(
        user
    )

    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }