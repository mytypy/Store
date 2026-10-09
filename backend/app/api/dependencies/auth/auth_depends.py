import jwt
from db.config import get_db_session
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from services.exceptions.exceptions import AuthException
from services.utils.auth.auth_utils import (
    check_jti,
    check_user_relevance,
    set_user_relevance,
)
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.core.security.jwt_service import UserAuth
from app.schemas.response.auth import JWTokenModel

security = HTTPBearer()


async def is_auth(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security),  # noqa: B008
                  auth: UserAuth = Depends(UserAuth), session: AsyncSession = Depends(get_db_session)) -> JWTokenModel:  # noqa: B008
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

    validate = await auth.decode_token(access_token, secret=auth.jwt_secret.ACCESS_TOKEN_SECRET)
    
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
            await set_user_relevance(user_id=user_id, expire=auth.jwt_secret.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    
    await check_jti(user_id=user_id, jti=validate.jti, type_jti=validate.type)
    
    request.state.user_id = validate.sub
    
    return validate


async def is_refresh_token(request: Request, auth: UserAuth = Depends(UserAuth)) -> JWTokenModel:  # noqa: B008
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
    
    jwt.decode(jwt=refresh_token, key=auth.jwt_secret.REFRESH_TOKEN_SECRET, algorithms=auth.jwt_secret.ALGORITHM)
    validate = await auth.decode_token(refresh_token, secret=auth.jwt_secret.REFRESH_TOKEN_SECRET)
    
    user_id = int(validate.sub)
    jti = validate.jti
    
    await check_jti(user_id=user_id, jti=jti, type_jti=validate.type)
    
    return validate