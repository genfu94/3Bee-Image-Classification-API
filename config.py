from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    AUTH_SECRET_KEY: str
    POSTGRES_HOST: str
    POSTGRES_USER: str = "admin"
    POSTGRES_PASS: str = "admin"
    POSTGRES_DB: str = "db"
