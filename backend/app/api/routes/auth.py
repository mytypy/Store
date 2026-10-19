import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth.auth_depends import is_auth, is_refresh_token
from app.core.security.auth import get_password_hash, verify_password
from app.core.security.jwt_service import JwtService
from app.crud.user.user import create_user, get_user
from app.db.manager import get_db_session
from app.models.user import User
from app.schemas.annotations.annotations import LoginUserData
from app.schemas.request.auth import LoginData, RegistrationData
from app.schemas.response.auth import JWTokenModel
from app.services.utils.auth.auth_utils import get_tokens

router = APIRouter(prefix='/auth', tags=['Работа с авторизацией'])
logger = logging.getLogger(name=__name__)

db_session = Depends(get_db_session)
auth = Depends(is_auth)
jwt_service = Depends(JwtService)
refresh_validate = Depends(is_refresh_token)


@router.post('/handshake/')
async def handshake(_: JWTokenModel = auth) -> JSONResponse:
    """Endpoint для проверки действительности access-токена

    Args:
        _ (JWTokenModel, optional): Объект JWT(Access) токена

    Returns:
        JSONResponse: Ответ, если все ок
    """
    
    return JSONResponse({'response': 'Ok'}, status_code=status.HTTP_200_OK)


@router.post('/login/')
async def login_user(data: LoginData, session: AsyncSession = db_session, jwt_service: JwtService = jwt_service) -> JSONResponse:
    """Endpoint, который выполняет вход пользователя и вовзращает HttpOnly JWT токены

    Args:
        data (LoginData): LoginData, которую отправляет сайт
        session (AsyncSession, optional): Асинхронная сессия
        jwt_service (JwtService, optional): Объект класса для работы с JWT токенами

    Raises:
        HTTPException: Исключение, если LoginData не передана или не валидна

    Returns:
        JSONResponse: Access + Refresh токен
    """
    
    user_fields = await get_user(User.email == data.email, session=session, fields_to_get=(User.password, User.user_id))
    user_data: list[LoginUserData] = user_fields.mappings().all()[0]
    
    is_coreect_password = verify_password(plain_password=data.password, hashed_password=user_data['password'])
    
    if is_coreect_password is False:
        raise HTTPException(detail='Некорректный логин или пароль', status_code=status.HTTP_400_BAD_REQUEST)
    
    response = await get_tokens(user_id=user_data['user_id'], jwt_service=jwt_service)
    
    return response


@router.post('/registration/')
async def user_registration(data: RegistrationData, session: AsyncSession = db_session, jwt_service: JwtService = jwt_service) -> JSONResponse:
    """Endpoint, который регистрирует пользователя и вовзращает HttpOnly JWT токены

    Args:
        data (RegistrationData): RegistrationData, которую отправляет сайт
        session (AsyncSession, optional): Асинхронная сессия
        jwt_service (JwtService, optional): Объект класса для работы с JWT токенами

    Raises:
        HTTPException: Исключение, если RegistrationData не передана или не валидна

    Returns:
        JSONResponse: Access + Refresh токен
    """
    hashed_password = get_password_hash(password=data.password)
    
    user_id = await create_user(name=data.name, surname=data.surname, email=data.email, hashed_password=hashed_password, session=session)
    await session.commit()
    
    response = await get_tokens(user_id=user_id, jwt_service=jwt_service)
    
    return response


@router.post('/refresh/')
async def refresh_tokens(refresh: JWTokenModel = refresh_validate, jwt_service: JwtService = jwt_service) -> JSONResponse:
    """Endpoint, который сбрасывает токены пользователя

    Args:
        refresh (JWTokenModel, optional): Объект JWT(Refresh токена)
        auth (UserAuth, optional): Объект класса для авторизации

    Returns:
        JSONResponse: Новый Access + Refresh токен
    """
    
    user_id = int(refresh.sub)
    
    response = await get_tokens(user_id=user_id, jwt_service=jwt_service)
    
    return response