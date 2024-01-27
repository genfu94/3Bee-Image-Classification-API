import jwt
from typing import Union
from datetime import datetime, timedelta
from passlib.context import CryptContext
from abc import ABC, abstractmethod

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


class JWTCryptEngine:
    def __init__(self, secret):
        self.secret = secret
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def create_access_token(
        self, data: dict, expires_delta: Union[timedelta, None] = None
    ):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret, algorithm=ALGORITHM)
        return encoded_jwt

    def validate_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret, algorithms=[ALGORITHM])
        except jwt.exceptions.InvalidTokenError as e:
            raise Exception("Token is not valid")

        return payload


class AuthenticationEngine(ABC):
    def __init__(self, jwt_crypt_engine: JWTCryptEngine):
        self.jwt_crypt_engine = jwt_crypt_engine

    @abstractmethod
    def _get_user(self, username: str):
        pass

    @abstractmethod
    def register_user(self, username: str, password: str):
        pass

    @abstractmethod
    def authenticate_user(self, username: str, password: str):
        pass
