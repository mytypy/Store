from sqlalchemy import ForeignKey, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Model, int_pk


class Cart(Model):
    __tablename__ = 'cart'
    
    cart_id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('product.product_id', ondelete='CASCADE'), nullable=False)
    count: Mapped[int] = mapped_column(SmallInteger, nullable=False)