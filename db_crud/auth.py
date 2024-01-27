from sqlalchemy.orm import Session
from models import User
from modules.jwt_crypt_engine import JWTCryptEngine


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def register_user(
    db: Session, jwt_crypt_engine: JWTCryptEngine, email: str, password: str
) -> User:
    hashed_password = jwt_crypt_engine.get_password_hash(password)
    db_user = User(email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    return db.refresh(db_user)


def authenticate_user(db: Session, username: str, password: str):
    pass
