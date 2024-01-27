from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from modules.jwt_crypt_engine import (
    JWTCryptEngine,
)
from sqlalchemy.orm import Session
import models
from schemas.auth import UserRegistration
from config import Settings
from db_crud.auth import register_user, get_user_by_email


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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/users/")
def create_user(user: UserRegistration, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    register_user(db, jwt_crypt_engine, user.email, user.password)
    return "ok"
