from fastapi import status


class AuthException(Exception):
    def __init__(
        self,
        detail: str = "Unauthorized",
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        clear_cookies: bool = False,
    ):
        self.detail = detail
        self.status_code = status_code
        self.clear_cookies = clear_cookies