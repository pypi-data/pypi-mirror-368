from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base_model import InternalBaseModel


class BaseHistoryModel(InternalBaseModel):
    __abstract__ = True

    operator_id: Mapped[str] = mapped_column(String(100))
    operator_name: Mapped[str] = mapped_column(String(100))
    operator_type: Mapped[str] = mapped_column(String(100))
    operate: Mapped[str] = mapped_column(Text(2000))
