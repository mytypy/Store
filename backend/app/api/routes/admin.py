import logging

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.admin.admin_dependencies import is_admin
from app.api.dependencies.auth.auth_depends import is_auth
from app.db.manager import get_db_session
from app.schemas.request.product import AddProductData
from app.schemas.response.auth import JWTokenModel

logger = logging.getLogger(name=__name__)
router = APIRouter(prefix='/admin', tags=['Админ панель'])

db_session = Depends(get_db_session)
auth = Depends(is_auth)
admin = Depends(is_admin)


@router.post('/add_product/')
async def add_product(
    data: str = Form(..., description="JSON-строка с полями AddProductData"),
    photos: list[UploadFile] = File(...),
    session: AsyncSession = db_session,
    admin: JWTokenModel = admin,
):
    product_data = AddProductData.model_validate_json(data)
    
    # logger.info(f"Данные товара: {product_data}")
    # logger.info(f"Получено файлов: {len(photos)}")