from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from modules.jwt_crypt_engine import (
    JWTCryptEngine,
)
from sqlalchemy.orm import Session
import models
from schemas.auth import Token
from schemas.auth import UserRegistration
from config import Settings
from db_crud.auth import register_user, get_user_by_username, authenticate_user


from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

settings = Settings()
jwt_crypt_engine = JWTCryptEngine(settings.AUTH_SECRET_KEY)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(prefix="")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="signin")


async def validate_token_and_get_active_user(
    token: Annotated[str, Depends(oauth2_scheme)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt_crypt_engine.validate_token(token)
    except:
        raise credentials_exception

    return payload["sub"]


@router.post("/signin", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = authenticate_user(
        db, jwt_crypt_engine, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = jwt_crypt_engine.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/signup")
def create_user(user: UserRegistration, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    register_user(db, jwt_crypt_engine, user.username, user.password)
    return "ok"


@router.get("/check_authentication")
async def synchronize_account(
    username: Annotated[str, Depends(validate_token_and_get_active_user)]
) -> dict:
    return {"status": "ok"}
