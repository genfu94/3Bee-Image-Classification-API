from sqlalchemy.orm import Session
from models import User
from modules.jwt_crypt_engine import JWTCryptEngine


def get_user_by_username(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()


def register_user(
    db: Session, jwt_crypt_engine: JWTCryptEngine, username: str, password: str
) -> User:
    hashed_password = jwt_crypt_engine.get_password_hash(password)
    db_user = User(username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    return db.refresh(db_user)


def authenticate_user(
    db: Session, jwt_crypt_engine: JWTCryptEngine, username: str, password: str
) -> User:
    user = get_user_by_username(db, username)
    if not user:
        return False

    if not jwt_crypt_engine.verify_password(password, user.hashed_password):
        return False

    return user
