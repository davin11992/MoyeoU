import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "LocalHub API"
    DATABASE_URL: str = "sqlite:///./moyeou.db"
    OPENAI_API_KEY: str = ""

    # backend/ 폴더 상위의 .env 파일을 찾아 매핑합니다.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()