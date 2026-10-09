import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from services.exceptions.exceptions import AuthException

from app.db.config import cfg, engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s:%(lineno)d] %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):    
    try:
        await cfg.wait_db(engine=engine, retries=10)
        
        yield
    finally:
        await engine.dispose()


app = FastAPI(lifespan=lifespan)

@app.exception_handler(AuthException)
async def auth_exception_handler(_: Request, exc: AuthException):
    """Функция для пользовательской ошибки

    Args:
        request (Request): Объект запроса
        exc (AuthException): Экземпляр класса ошибки AuthException

    Returns:
        JSONResponse: Ответ
    """
    
    response = JSONResponse(
        content={"detail": exc.detail},
        status_code=exc.status_code,
    )

    if exc.clear_cookies:
        response.delete_cookie(
            key="refresh_token",
            path="/",
            httponly=True,
            secure=True,
            samesite="none",
        )

    return response


api = APIRouter(prefix='/api')


app.include_router(api)