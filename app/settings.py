from pydantic import (
    BaseSettings
)

class Settings(BaseSettings):
    FINNHUB_API_KEY: str
