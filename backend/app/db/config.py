import asyncio
import logging
import sys
from pathlib import Path
from typing import Literal

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import DatabaseSettings

logger = logging.getLogger(__name__)


class Config:
    
    def __init__(self):
        self.settings = DatabaseSettings()
    
    @property
    def pg_bouncer_url(self) -> str:
        env = self.settings
        return f'postgresql+asyncpg://{env.USER}:{env.PASSWORD}@{env.PG_BOUNCER_HOST}:{env.PG_BOUNCER_PORT}/{env.DB}'

    @property
    def direct_url(self) -> str:
        env = self.settings
        return f'postgresql+asyncpg://{env.USER}:{env.PASSWORD}@{env.HOST}:{env.PORT}/{env.DB}'

    async def wait_db(self, engine: AsyncEngine, retries=30) -> None: # Проверка на то, готова ли БД принимать запросы
        engine_type: Literal['PostgrSQL', 'PG Bouncer'] = 'PostgrSQL' if 'localhost' in engine.url else 'PG Bouncer'
        
        for i in range(retries):
            try:
                async with engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                    
                logger.info(f"{engine_type} работает и готов принимать SQL запросы")
                
                return
            except OperationalError:
                logger.info(f"{engine_type} не готова ({i+1}/{retries})")
                
                await asyncio.sleep(2)

        raise RuntimeError(f"{engine_type} недоступна")


cfg = Config()
engine = create_async_engine(cfg.direct_url,
    poolclass=NullPool,
    connect_args={
        "statement_cache_size": 0
    })
SessionMaker = async_sessionmaker(engine, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator:
    async with SessionMaker() as session:
        yield session