import os

from pydantic_settings import BaseSettings, SettingsConfigDict

# 환경 변수에서 프로필 정보를 가져옵니다. 기본값은 'local'입니다.
PROFILE = os.getenv("PROFILE", "local")
config_dict = SettingsConfigDict(
    extra="ignore",
    env_file=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        f'env/.env.{PROFILE}'
    ),
    env_file_encoding='utf-8',
)


class Settings(BaseSettings):
    model_config = config_dict

    CORS_ORIGINS: list[str]
    CORS_HEADERS: list[str]


class DBConfig(BaseSettings):
    model_config = config_dict

    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str


settings = Settings()
db_config = DBConfig()
