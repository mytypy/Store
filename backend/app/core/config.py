from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE_PATH = '../.env'

class DatabaseSettings(BaseSettings):
    """Класс для получения данных для БД"""
    
    USER: str
    PASSWORD: str
    HOST: str
    PORT: int
    DB: str
    
    PG_BOUNCER_PORT: int
    PG_BOUNCER_HOST: str

    model_config = SettingsConfigDict(
        env_prefix='POSTGRES_',
        env_file=ENV_FILE_PATH,
        extra='ignore'
        )


class JWTSecret(BaseSettings):
    """Класс для получения настроек JWT токенов"""
        
    ACCESS_TOKEN_SECRET: str
    REFRESH_TOKEN_SECRET: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    
    model_config = SettingsConfigDict(
        env_prefix="JWT_",
        extra='ignore',
        env_file=ENV_FILE_PATH
        )
    

class RedisSettings(BaseSettings):
    """Класс для получения данные для Redis"""
    
    HOST: str
    PORT: int
    
    model_config = SettingsConfigDict(
        env_prefix='REDIS_',
        env_file=ENV_FILE_PATH,
        extra='ignore'
        )