from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth.auth_depends import is_auth, is_refresh_token
from app.core.security.jwt_service import JwtService
from app.db.config import get_db_session
from app.schemas.request.auth import LoginData
from app.schemas.response.auth import JWTokenModel
from app.services.utils.auth.auth_utils import get_tokens

router = APIRouter(prefix='/auth', tags=['Работа с авторизацией'])


@router.post('/handshake/')
async def handshake(_: JWTokenModel = Depends(is_auth)) -> JSONResponse:  # noqa: B008
    """Endpoint для проверки действительности access-токена

    Args:
        _ (JWTokenModel, optional): Объект JWT(Access) токена

    Returns:
        JSONResponse: Ответ, если все ок
    """
    
    return JSONResponse({'response': 'Ok'}, status_code=status.HTTP_200_OK)


@router.post('/login/')
async def auth_user(data: LoginData, session: AsyncSession = Depends(get_db_session), jwt_service: JwtService = Depends(JwtService)) -> JSONResponse:  # noqa: B008
    """Endpoint, который проводит авторизацию и вовзращает HttpOnly JWT токены

    Args:
        data (LoginData): LoginData, которую отправляет сайт
        session (AsyncSession, optional): Асинхронная сессия
        jwt_service (JwtService, optional): Объект класса для работы с JWT токенами

    Raises:
        HTTPException: Исключение, если LoginData не передана или не валидна

    Returns:
        JSONResponse: Access + Refresh токен
    """
    
    # Вот тут код
    user_id = None # Поменять
    
    response = await get_tokens(user_id=user_id, jwt_class=jwt_service)
    
    return response


@router.post('/refresh/')
async def refresh_tokens(refresh: JWTokenModel = Depends(is_refresh_token), jwt_service: JwtService = Depends(JwtService)) -> JSONResponse:  # noqa: B008
    """Endpoint, который сбрасывает токены пользователя

    Args:
        refresh (JWTokenModel, optional): Объект JWT(Refresh токена)
        auth (UserAuth, optional): Объект класса для авторизации

    Returns:
        JSONResponse: Новый Access + Refresh токен
    """
    
    user_id = int(refresh.get('sub'))
    
    response = await get_tokens(user_id=user_id, auth=jwt_service)
    
    return response