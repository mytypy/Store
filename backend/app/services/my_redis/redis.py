import logging
from typing import Any

import redis.asyncio as aioredis

from app.core.config import RedisSettings


class Redis(aioredis.Redis):
    """Класс для разных взаимодействий с Redis"""
    
    def __init__(self):
        redis_settings = RedisSettings()
        self.redis = aioredis.Redis(host=redis_settings.HOST, port=redis_settings.PORT, decode_responses=True)
        self.logger = logging.getLogger(__name__)

    async def ping(self, retries_for_ping: int = 10) -> None:
        """Функция для проверки состояния redis сервера

        Args:
            retries_for_ping (int, optional): Кол-во попыток для пинга. ПО умолчанию 10.

        Raises:
            RuntimeError: _description_
        """
        for i in range(1, retries_for_ping + 1):
            self.logger.info(f"Пробуем подклчюиться к Redis. Попытка №{i}")
            
            try:
                await self.redis.ping()
                
                break
            except Exception as er:  # noqa: BLE001
                self.logger.error(f'Неудалось подключиться к Redis: {er}')
        else:
            raise RuntimeError('Неудалось подключиться к Redis')
        
    async def init(self, retries_for_ping: int = 10) -> None:
        """Функция для иницализации Redis клиента

        Args:
            retries_for_ping (int, optional): Кол-во попыток для пинга Redis

        Raises:
            RuntimeError: Ошибка, если неудлаось пингануть Redis спустя retries_for_ping попыток
        """
        
        await self.ping(retries_for_ping=retries_for_ping)
        
        self.logger.info('Успешно подключились к Redis!')
    
    async def close(self) -> None:
        """Функция для закрытия соединения Redis"""
        
        await self.redis.aclose()
    
    def __getattr__(self, name: str) -> Any:
        """
        Магический метод для получения метода, которого нет в классе
        (делается для того, чтобы можно было использовать в сочетании с наследованием)

        Args:
            name (str): Имя аттрибута

        Returns:
            Any: Объект класса aioredis.Redis
        """
        
        return getattr(self.redis, name)


redis = Redis()