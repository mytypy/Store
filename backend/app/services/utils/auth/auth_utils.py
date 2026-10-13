from typing import Literal

from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from app.core.security.jwt_service import JwtService
from app.db.config import get_db_session
from app.services.my_redis.redis import redis

security = HTTPBearer()
security = Depends(security)
jwt_service = Depends(JwtService)
db_session = Depends(get_db_session)


async def get_tokens(user_id: int, jwt_service: JwtService) -> JSONResponse:
    """Функция для генерации JWT токенов

    Args:
        user_id (int): user_id пользователя из БД
        auth (UserAuth): Экземпляр класса для проверки токенов

    Returns:
        JSONResponse: Ответ
    """
    
    expire_access_minutes = jwt_service.jwt_secret.ACCESS_TOKEN_EXPIRE_MINUTES
    expire_refresh_minutes = jwt_service.jwt_secret.REFRESH_TOKEN_EXPIRE_MINUTES
    
    jti_access, access_token = await jwt_service.create_acess_token(user_id=user_id, expire_minutes=expire_access_minutes)
    jti_refresh, refresh_token = await jwt_service.create_refresh_token(user_id=user_id, expire_minutes=expire_refresh_minutes)
    
    await set_jti(user_id=user_id, jti=jti_access, time_expire=expire_access_minutes * 60, type_jti='access')
    await set_jti(user_id=user_id, jti=jti_refresh, time_expire=expire_refresh_minutes * 60, type_jti='refresh')
    
    response = JSONResponse(content={'accessToken': access_token})
    # response.set_cookie(
    #     "refresh_token",
    #     refresh_token,
    #     httponly=True,
    #     samesite="lax",
    #     secure=False,
    #     max_age=expire_refresh_minutes * 60
    # ) local
    
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=expire_refresh_minutes * 60
    )
    
    return response 


async def check_jti(user_id: int, jti: str, type_jti: Literal['access', 'refresh']) -> None:
    """
    Проверяет, является ли JWT-токен актуальным.

    Для каждого пользователя и типа токена в Redis хранится
    один разрешённый jti. Если запись отсутствует или значение
    не совпадает с jti из токена, доступ запрещается.

    Args:
        user_id: Идентификатор пользователя из проверенного JWT
        jti: Уникальный идентификатор предъявленного токена
        type_jti: Тип токена — access или refresh
        redis: Асинхронный клиент Redis

    Raises:
        HTTPException: Если токен отозван, устарел или отсутствует
            в списке актуальных токенов.
    """
      
    key = f'{user_id}_{type_jti}_jti'
    
    redis_jti = await redis.get(key)
    
    if redis_jti != jti or redis_jti is None:
        raise HTTPException(detail=f'Это не актуальный {type_jti.title()} Token', status_code=status.HTTP_403_FORBIDDEN)


async def set_jti(user_id: int, jti: str, time_expire: int, type_jti: Literal['access', 'refresh']) -> None:
    """
    Сохраняет актуальный jti для пользователя в Redis.

    Предыдущий jti для этого типа токена заменяется новым.
    Ключ автоматически удаляется по истечении time_expire.

    Args:
        user_id: Идентификатор пользователя
        jti: Идентификатор нового JWT
        time_expire: Время жизни записи в секундах
        type_jti: Тип токена — access или refresh
        redis: Асинхронный клиент Redis

    Raises:
        ValueError: Если срок хранения не положительный
    """
    
    if time_expire <= 0:
        raise ValueError("time_expire должен быть больше нуля!")

    key = f"{user_id}_{type_jti}_jti"

    await redis.set(key, jti, ex=time_expire)


async def check_user_relevance(user_id: int) -> bool:
    """
    Проверяет наличие записи об актуальности пользователя в Redis.

    Отсутствие ключа означает, что пользователь не считается
    активным в рамках этой системы проверки.

    При необходимости это проверяется
    отдельным запросом к БД.

    Args:
        user_id: Идентификатор пользователя
        redis: Асинхронный клиент Redis

    Returns:
        True, если ключ существует; иначе False
    """
    
    key = f'user_relevance_{user_id}'
    
    response = await redis.get(key)
    
    return bool(response)


async def set_user_relevance(user_id: int, expire: int) -> None:
    """
    Создаёт запись об актуальности пользователя в Redis.

    Запись автоматически удаляется через expire секунд.

    Args:
        user_id: Идентификатор пользователя
        expire: Время жизни записи в секундах
        redis: Асинхронный клиент Redis

    Raises:
        ValueError: Если срок хранения не положительный
    """
    
    if expire <= 0:
        raise ValueError("expire должен быть больше нуля!")

    key = f"user_relevance_{user_id}"

    await redis.set(key, 1, ex=expire)