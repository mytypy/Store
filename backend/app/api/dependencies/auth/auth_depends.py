import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.core.security.jwt_service import JwtService
from app.crud.user.user import get_user
from app.db.manager import get_db_session
from app.models.user import User
from app.schemas.response.auth import JWTokenModel
from app.services.exceptions.exceptions import AuthException
from app.services.utils.auth.auth_utils import (
    check_jti,
    check_user_relevance,
    set_user_relevance,
)

security = Depends(HTTPBearer())
jwt_service = Depends(JwtService)
db_session = Depends(get_db_session)


async def is_auth(request: Request, credentials: HTTPAuthorizationCredentials = security,
                  jwt_service: JwtService = jwt_service,
                  session: AsyncSession = db_session) -> JWTokenModel:
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
        user_object = await get_user(User.user_id == user_id, session=session, fields_to_get=(User.user_id, ))
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


async def is_refresh_token(request: Request, jwt_service: JwtService = jwt_service) -> JWTokenModel:
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
    
    jwt.decode(jwt=refresh_token, key=jwt_service.jwt_secret.REFRESH_TOKEN_SECRET, algorithms=jwt_service.jwt_secret.ALGORITHM)
    validate = await jwt_service.decode_token(refresh_token, secret=jwt_service.jwt_secret.REFRESH_TOKEN_SECRET)
    
    user_id = int(validate.sub)
    jti = validate.jti
    
    await check_jti(user_id=user_id, jti=jti, type_jti=validate.type)
    
    return validate