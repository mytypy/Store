from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    USER: str
    PASSWORD: str
    HOST: str
    PORT: int
    DB: str
    PG_BOUNCER_PORT: int
    PG_BOUNCER_HOST: str

    model_config = SettingsConfigDict(env_prefix='POSTGRES_', env_file='../.env', extra='ignore')