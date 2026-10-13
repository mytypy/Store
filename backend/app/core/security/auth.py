from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Функция для сравнения пароля пользователя

    Args:
        plain_password (str): Незашифрованный пароль
        hashed_password (str): Зашифрованный пароль

    Returns:
        bool: Равны пароли или нет
    """
    
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Функция для шифрования пароля по алгоритму Argon2

    Args:
        password (str): Незашиврованный

    Returns:
        str: Зашифрованный пароль
    """
    
    return password_hash.hash(password)