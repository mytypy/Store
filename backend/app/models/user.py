from decimal import Decimal

from sqlalchemy import Boolean, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Model, created_at_time, int_pk


class User(Model):
    __tablename__ = 'user'
    
    user_id: Mapped[int_pk]
    login: Mapped[str] = mapped_column(String(64), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    adress: Mapped[str] = mapped_column(String(255), nullable=True)
    balance: Mapped[Decimal] = mapped_column(Numeric(precision=9, scale=2), server_default=text('0.00'), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, server_default=text('false'), nullable=False)
    
    first_login_at: Mapped[created_at_time]