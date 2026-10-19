from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.engine.result import Result
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.utils import db_errors_to_http
from app.models.user import User
from app.services.exceptions.exceptions import UniqueUser


@db_errors_to_http
async def create_user(name: str, surname: str, email: str, hashed_password: str, session: AsyncSession) -> int | None:
    """Функция, которая регистрирует пользователя

    Args:
        name (str): Имя пользователя
        surname (str): Фамилия пользователя
        email (str): Email пользователя
        password (str): Зашифрованный пароль пользователя
        
        session (AsyncSession): Асинхронная сессия
    """
    
    stmt = (
        pg_insert(User)
        .values(name=name, surname=surname, email=email, password=hashed_password)
        .on_conflict_do_nothing(index_elements=["email"])
        .returning(User.user_id)
        )
    
    result = await session.execute(stmt)
    user_id = result.scalar()
    
    if user_id is None:
        raise UniqueUser(detail='Пользователь с этим email уже существует', status_code=status.HTTP_409_CONFLICT)
    
    return user_id
    

@db_errors_to_http
async def get_user(*params, session: AsyncSession, fields_to_get: tuple = (User, )) -> Result[tuple[User]]:
    """Функция, которая возврашает объект/ы таблицы пользователя

    Args:
        session (AsyncSession): Асинхронная сессия

    Returns:
        Result[tuple[User]]: Результат запроса
    """
    
    query = select(*fields_to_get).where(*params)
    
    result = await session.execute(query)
    
    return result