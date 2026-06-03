from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.schemas import ApiResponse, api_response
from app.core.security import create_access_token
from app.features.auth.dependencies import get_current_user
from app.features.auth.models import User
from app.features.auth.schemas import AuthToken, LoginRequest, RegisterRequest, UserPublic
from app.features.auth.service import authenticate_user, register_user

router = APIRouter()


def _auth_payload(user: User) -> AuthToken:
    return AuthToken(
        access_token=create_access_token(str(user.id)),
        user=UserPublic.model_validate(user),
    )


@router.post("/register", response_model=ApiResponse[AuthToken])
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(db, request)
    return api_response(_auth_payload(user))


@router.post("/login", response_model=ApiResponse[AuthToken])
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, request)
    return api_response(_auth_payload(user))


@router.get("/me", response_model=ApiResponse[UserPublic])
def me(current_user: User = Depends(get_current_user)):
    return api_response(UserPublic.model_validate(current_user))

