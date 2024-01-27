from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    AUTH_SECRET_KEY: str