import datetime
from typing import Annotated

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Model(DeclarativeBase):
    pass


int_pk = Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]

created_at_time = Annotated[datetime.datetime, mapped_column(DateTime(timezone=True), server_default=func.now())]
updated_at_time = Annotated[datetime.datetime, mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())]
