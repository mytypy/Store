from decimal import Decimal

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Model, created_at_time, int_pk


class Category(Model):
    __tablename__ = 'categories'
    
    category_id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(precision=3, scale=1))
    
    created_at: Mapped[created_at_time]