from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Model, created_at_time, int_pk


class Prodcut(Model):
    __tablename__ = 'product'
    
    product_id: Mapped[int_pk]
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    star: Mapped[Decimal] = mapped_column(Numeric(precision=3, scale=2), nullable=False, server_default=text('0.00'))
    price: Mapped[Decimal] = mapped_column(Numeric(precision=9, scale=2), nullable=False)
    
    protein: Mapped[Decimal] = mapped_column(Numeric(precision=5, scale=1), nullable=False)
    fat: Mapped[Decimal] = mapped_column(Numeric(precision=5, scale=1), nullable=False)
    carbs: Mapped[Decimal] = mapped_column(Numeric(precision=5, scale=1), nullable=False)
    kcal: Mapped[Decimal] = mapped_column(Numeric(precision=5, scale=1), nullable=False)
    
    attributes: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    created_at: Mapped[created_at_time]
    

class ProductImages(Model):
    __tablename__ = 'product_image'
    
    image_id: Mapped[int_pk]
    product_id: Mapped[int] = mapped_column(ForeignKey('product.product_id', ondelete='CASCADE'), nullable=False)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    
    created_at: Mapped[created_at_time]


class ProductCategory(Model):
    __tablename__ = 'product_category'
    
    prod_cat_id: Mapped[int_pk]
    product_id: Mapped[int] = mapped_column(ForeignKey('product.product_id', ondelete='CASCADE'), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.category_id', ondelete='CASCADE'), nullable=False)
    
    created_at: Mapped[created_at_time]