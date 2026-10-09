import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status

from app.core.config import JWTSecret
from app.schemas.response.auth import JWTokenModel


class JwtService:
    
    def __init__(self):
        self.jwt_secret = JWTSecret()
        
    async def create_acess_token(self, user_id: int, expire_minutes: int = 10) -> tuple[str, str]:
        """Метод, который создает access токен

        Args:
            user_id (int): БД ID пользователя
            expire_minutes (int, optional): Срок действия access токена в минутах. По умолчанию 10 минут

        Returns:
            tuple[str, str]: jti и JWT токен
        """
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=expire_minutes)
        jti = str(uuid.uuid4())
        
        payload = {
            "sub": str(user_id),
            "type": "access",
            "jti": jti,
            "exp": expire,
            "iat": now
            }
        
        token = jwt.encode(payload=payload, key=self.jwt_secret.ACCESS_TOKEN_SECRET, algorithm=self.jwt_secret.ALGORITHM)
        
        return jti, token
    
    async def create_refresh_token(self, user_id: int, expire_minutes: int = 3600) -> tuple[str, str]:
        """Метод, который создает refresh токен
        
        Args:
            user_id (int): БД ID пользователя
            expire_minutes (int, optional): Срок действия access токена в минутах. По умолчанию 10 минут
        
        Returns:
            tuple[str, str]: jti и JWT токен
        """
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=expire_minutes)

        jti = str(uuid.uuid4())

        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": expire,
            "jti": jti,
            "iat": now,
        }

        token = jwt.encode(
            payload=payload,
            key=self.jwt_secret.REFRESH_TOKEN_SECRET,
            algorithm=self.jwt_secret.ALGORITHM
        )

        return jti, token
    
    async def decode_token(self, token: str, secret: str) -> JWTokenModel:
        """Метод, который декодирует JWT токен
                
        Args:
            token (str): JWT токен
            secret (str): Секретная подпись для JWT токена
                
        Returns:
            JWTokenModel: Модель JWT токена
        """
        try:
            token = jwt.decode(jwt=token, key=secret, algorithms=self.jwt_secret.ALGORITHM)
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Токен истек')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Токен инвалид')
        
        return JWTokenModel(**token)