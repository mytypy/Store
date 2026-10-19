import asyncio
import logging
from collections.abc import AsyncGenerator
from typing import Literal

from sqlalchemy import URL, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import DatabaseSettings

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_type: Literal['PostgreSQL', 'PG Bouncer'] = 'PostgreSQL'):
        self.settings = DatabaseSettings()
        self.db_type: Literal['PostgreSQL', 'PG Bouncer'] = db_type
        
        if self.db_type == 'PostgreSQL':
            self.engine: AsyncEngine = create_async_engine(
                self.direct_url, 
            )
        else:
            self.engine: AsyncEngine = create_async_engine(
                self.pg_bouncer_url, 
                poolclass=NullPool,
                connect_args={"statement_cache_size": 0}
            )
            
        self.session_maker = async_sessionmaker(
            self.engine, 
            expire_on_commit=False,
        )
    
    @property
    def pg_bouncer_url(self) -> URL:
        """Свойство для получения ссылки на подключение к PG Bouncer через asyncpg"""
        
        env = self.settings
        
        return URL.create(
            drivername="postgresql+asyncpg",
            username=env.USER,
            password=env.PASSWORD,
            host=env.PG_BOUNCER_HOST,
            port=env.PG_BOUNCER_PORT,
            database=env.DB,
        )

    @property
    def direct_url(self) -> URL:
        """Свойство для получения ссылки на подключение к PostgreSQL через asyncpg"""
        
        env = self.settings
        
        return URL.create(
            drivername="postgresql+asyncpg",
            username=env.USER,
            password=env.PASSWORD,
            host=env.HOST,
            port=env.PORT,
            database=env.DB,
        )

    async def wait_db(self, retries: int = 30, delay: int = 2) -> None:
        """Функция для проверки готовности БД принимать запросы

        Args:
            retries (int, optional): Кол-во попыток для подключения к БД. По умолчанию 30
            delay (int, optional): Задержка в секундах после неудачной попытки

        Raises:
            RuntimeError: Ошибка, если БД недоступна
        """

        for i in range(retries):
            try:
                async with self.engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                logger.info(f"{self.db_type} работает и готов принимать SQL запросы")
                return
            except OperationalError:
                logger.info(f"{self.db_type} не готова ({i+1}/{retries}). Ждем {delay} сек...")
                await asyncio.sleep(delay)

        raise RuntimeError(f"{self.db_type} недоступна после {retries} попыток")

    async def dispose(self) -> None:
        """Закрывает пул соединений и разрывает физические соединения с БД"""
        
        await self.engine.dispose()


cfg = DatabaseManager()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency для FastAPI 

    Yields:
        Iterator[AsyncGenerator[AsyncSession, None]]: Асинхронная сессия
    """
    async with cfg.session_maker() as session:
        yield session