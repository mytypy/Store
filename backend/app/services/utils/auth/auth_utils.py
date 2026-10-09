from typing import Literal

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.core.security.jwt_service import JwtService
from app.db.config import get_db_session
from app.schemas.response.auth import JWTokenModel
from app.services.exceptions.exceptions import AuthException
from app.services.my_redis.redis import redis

security = HTTPBearer()


async def is_auth(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security),
                  jwt_service: JwtService = Depends(JwtService), session: AsyncSession = Depends(get_db_session)) -> JWTokenModel:
    """Функция для проверки актуальности пользователя и access токена

    Args:
        request (Request): Объект запроса
        credentials (HTTPAuthorizationCredentials, optional): Credentials
        auth (UserAuth, optional): Экземпляр класса для проверки токенов
        session (AsyncSession, optional): Асинхронная сессия

    Raises:
        AuthException: Исключение, если не был передан Access токен
        AuthException: Исключение с очисткой cookies, если такого пользователя нет в БД

    Returns:
        JWTokenModel: Объект JWT(Access) токена
    """
    
    access_token = credentials.credentials    

    if access_token is None:
        raise AuthException(
            detail='Вы не передали access token',
            status_code=status.HTTP_403_FORBIDDEN,
            clear_cookies=False
        )

    validate = await jwt_service.decode_token(access_token, secret=jwt_service.jwt_secret.ACCESS_TOKEN_SECRET)
    
    user_id = int(validate.sub)
    
    redis_result: bool = await check_user_relevance(user_id=user_id)
    
    if redis_result is False:
        user_object = await get_user_units(User.user_id == user_id, session=session)
        user: User | None = user_object.scalars().one_or_none()
        
        if user is None:
            raise AuthException(
                detail='Вы не передали access token',
                status_code=status.HTTP_403_FORBIDDEN,
                clear_cookies=True
        ) 
        else:
            await set_user_relevance(user_id=user_id, expire=jwt_service.jwt_secret.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    
    await check_jti(user_id=user_id, jti=validate.jti, type_jti=validate.type)
    
    request.state.user_id = validate.sub
    
    return validate


async def is_refresh_token(request: Request, jwt_service: JwtService = Depends(JwtService)) -> JWTokenModel:
    """Функция для проверки refresh токена

    Args:
        request (Request): Объект запроса
        auth (UserAuth, optional): Экземпляр класса для проверки токенов

    Raises:
        HTTPException: Ошибка, если refresh токен не был передан

    Returns:
        JWTokenModel: Объект JWT токена
    """
    
    cookies = request.cookies
    refresh_token = cookies.get('refresh_token')
    
    if not refresh_token:
        raise HTTPException(detail='Вы не передали RefreshToken!', status_code=status.HTTP_403_FORBIDDEN)
    
    validate = await jwt_service.decode_token(refresh_token, secret=jwt_service.jwt_secret.REFRESH_TOKEN_SECRET)
    
    user_id = int(validate.sub)
    jti = validate.jti
    
    await check_jti(user_id=user_id, jti=jti, type_jti=validate.type)
    
    return validate


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
    """Функция для проверки jti токена

    Args:
        user_id (int): user_id пользователя из БД
        jti (str): Уникальный идентификатор jwt токена
        type_jti (Literal[access, refresh]): Типы jwt токенов

    Raises:
        HTTPException: Ошибка, если jti не актуален
    """
      
    key = f'{user_id}_{type_jti}_jti'
    
    redis_jti = await redis.get(key)
    
    if redis_jti != jti and redis_jti is not None:
        raise HTTPException(detail=f'Это не актуальный {type_jti.title()} Token', status_code=status.HTTP_403_FORBIDDEN)


async def set_jti(user_id: int, jti: str, time_expire: int, type_jti: Literal['access', 'refresh']) -> None:
    """Функция для вставки jti в Redis

    Args:
        user_id (int): user_id пользователя из БД
        jti (str): Уникальный идентификатор jwt токена
        time_expire (int): Срок истечения jti
        type_jti (Literal[access, refresh]): Типы JWT токенов
    """
    
    key = f'{user_id}_{type_jti}_jti'
    
    await redis.delete(key)
    await redis.set(key, jti)
    await redis.expire(name=key, time=time_expire)


async def check_user_relevance(user_id: int) -> bool:
    """Функция для проверки существования актуальности ключа пользователя в Redis

    Args:
        user_id (int): user_id из JWT токена пользователя

    Returns:
        bool: Есть ли запись в redis
    """
    key = f'user_relevance_{user_id}'
    
    response = await redis.get(key)
    
    return bool(response)


async def set_user_relevance(user_id: int, expire: int) -> None:
    """Функция для вставки значения для актуальности пользователя в redis

    Args:
        user_id (int): user_id из jwt токена
        expire (int): Кол-во секунд до удаления ключа из redis
    """
    
    key = f'user_relevance_{user_id}'
    
    await redis.set(key, value=1, ex=expire)