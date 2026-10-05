from decimal import Decimal

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Numeric, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Model, created_at_time, int_pk
from app.models.enums.enum import OrderEnum


class Order(Model):
    __tablename__ = 'order'
    
    order_id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id', ondelete='SET NULL'), nullable=True)
    
    total_price: Mapped[Decimal] = mapped_column(Numeric(precision=9, scale=2), nullable=False)
    status: Mapped[OrderEnum] = mapped_column(SQLEnum(OrderEnum,
                                                       name='order_status_enum',
                                                        values_callable=lambda enum_cls: [item.value for item in enum_cls]),
                                               nullable=False, server_default=OrderEnum.PROCESS)
    
    created_at: Mapped[created_at_time]
    

class OrderItem(Model):
    __tablename__ = 'order_item'
    
    order_items_id: Mapped[int_pk]
    order_id: Mapped[int] = mapped_column(ForeignKey('order.order_id', ondelete='SET NULL'), nullable=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('product.product_id', ondelete='SET NULL'), nullable=True)
    
    price: Mapped[Decimal] = mapped_column(Numeric(precision=9, scale=2), nullable=False)
    count: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    
    created_at: Mapped[created_at_time]