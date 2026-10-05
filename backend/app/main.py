import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

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

api = APIRouter(prefix='/api')


app.include_router(api)