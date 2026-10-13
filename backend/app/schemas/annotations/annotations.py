from typing import TypedDict


class LoginUserData(TypedDict):
    """
    Аннотация для данных в login
    """
    
    user_id: int
    password: str