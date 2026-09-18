from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserRead
from app.services import auth_service
from app.services.auth_service import EmailAlreadyRegisteredError, InvalidCredentialsError

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    try:
        user = auth_service.register_user(
            db,
            email=payload.email,
            password=payload.password,
            name=payload.name,
            birth_date=payload.birth_date,
            height_cm=payload.height_cm,
        )
    except EmailAlreadyRegisteredError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado.")
    return user


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    try:
        user = auth_service.authenticate_user(db, email=payload.email, password=payload.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha incorretos."
        )
    return Token(access_token=create_access_token(subject=user.id))


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return current_user
