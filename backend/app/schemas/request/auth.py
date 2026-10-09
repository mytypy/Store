from pydantic import BaseModel, EmailStr, Field


class LoginData(BaseModel):
    """Модель для валидации данных для входа"""
    
    login: str = Field(min_length=10, max_length=64, description='Логин пользователя')
    password: str = Field(min_length=16, max_length=255, description='Пароль пользователя')


class RegistrationData(BaseModel):
    """Модель для валидации данных для регистрации"""
    
    name: str = Field(min_length=2, max_length=64, description='Имя пользователя')
    surname: str = Field(min_length=2, max_length=64, description='Фамилия пользователя')
    email: EmailStr = Field(description='Почта пользователя')
    login: str = Field(min_length=10, max_length=64, description='Логин пользователя')
    password: str = Field(min_length=16, max_length=255, description='Пароль пользователя')