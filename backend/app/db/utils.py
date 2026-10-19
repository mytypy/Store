import logging
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, TypeVar

import asyncpg
from fastapi import HTTPException, status
from sqlalchemy.exc import (
    DataError,
    DBAPIError,
    DisconnectionError,
    IntegrityError,
    NoResultFound,
    OperationalError,
    PendingRollbackError,
    StatementError,
    TimeoutError,
)
from app.services.exceptions.exceptions import UniqueUser

P = ParamSpec("P")
R = TypeVar("R")
logger = logging.getLogger(__name__)


def db_errors_to_http(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
    """Функция декоратор для обработки ошибок в запросах базы данных"""
    
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        
        try:
            return await func(*args, **kwargs)

        except IntegrityError as e:
            logger.error(f'Ошибка: {e}')
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Нарушено ограничение целостности данных"
            )

        except DataError as e:
            logger.error(f'Ошибка: {e}')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Некорректные данные при работе с БД"
            )

        except OperationalError as e:
            logger.error(f'Ошибка: {e}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка операционной работы с БД"
            )

        except TimeoutError as e:
            logger.error(f'Ошибка: {e}')
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Превышено время ожидания БД"
            )

        except StatementError as e:
            logger.error(f'Ошибка: {e}')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Неправильный SQL-запрос"
            )

        except DBAPIError as e:
            logger.error(f'Ошибка: {e}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка низкоуровневого драйвера БД"
            )

        except DisconnectionError as e:
            logger.error(f'Ошибка: {e}')
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Потеряно соединение с БД"
            )

        except NoResultFound as e:
            logger.error(f'Ошибка: {e}')
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Запись не найдена"
            )

        except PendingRollbackError as e:
            logger.error(f'Ошибка: {e}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Транзакция БД в состоянии отката"
            )

        except asyncpg.exceptions.UniqueViolationError as e:
            logger.error(f'Ошибка: {e}')
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Нарушено ограничение уникальности"
            )
        except asyncpg.exceptions.ForeignKeyViolationError as e:
            logger.error(f'Ошибка: {e}')
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Нарушено внешнее ограничение (FK)"
            )
        except asyncpg.exceptions.NotNullViolationError as e:
            logger.error(f'Ошибка: {e}')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Обязательное поле имеет NULL‑значение"
            )
        except asyncpg.exceptions.CheckViolationError as e:
            logger.error(f'Ошибка: {e}')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Нарушено условие CHECK"
            )
        except asyncpg.PostgresError as e:
            logger.error(f'Ошибка: {e}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка PostgreSQL: "
            )

        except UniqueUser as e:
            logger.error(e.detail)
            
            raise HTTPException(detail=e.detail, status_code=e.status_code)
            
        except Exception as e:  # noqa: BLE001
            logger.error(f'Ошибка бд: {e}')
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутренняя ошибка сервера"
            )

    return wrapper