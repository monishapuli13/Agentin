from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.features.auth.models import User
from app.features.auth.schemas import LoginRequest, RegisterRequest
from app.features.common.enums import UserRole


def register_user(db: Session, request: RegisterRequest) -> User:
    email = request.email.strip().lower()
    username = request.username.strip()

    existing_user = db.scalar(
        select(User).where(or_(User.email == email, User.username == username))
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with that email or username already exists.",
        )

    user = User(
        email=email,
        username=username,
        hashed_password=hash_password(request.password),
        role=UserRole.CLIENT,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, request: LoginRequest) -> User:
    email = request.email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user

