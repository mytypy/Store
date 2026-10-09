from typing import Literal

from pydantic import BaseModel, Field


class JWTokenModel(BaseModel):
    """Модель для создания объекта JWT токена"""
    
    sub: str = Field(description='User_id пользователя из БД')
    type: Literal['access', 'refresh'] = Field(description='Тип JWT токена')
    jti: str = Field(description='Уникальный идентификатор JWT токена')
    exp: int = Field(description='Время истечения JWT токена в Unix-форме')
    iat: int = Field(description='Время выпуска JWT токена в Unix-форме')