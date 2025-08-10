import copy
import json
import uuid
import arrow
from datetime import datetime
from typing import Union, Dict, Type, Tuple, Set, Mapping, Any, TYPE_CHECKING

from sqlalchemy.ext.asyncio.session import AsyncSession

from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.ext.asyncio import AsyncAttrs
from pydantic import BaseModel

from .operate import Operate
from ..exception.internal_exception import NoChangeException


@as_declarative()
class Base(AsyncAttrs):
    __abstract__ = True
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class InternalBaseModel(Base):
    __abstract__ = True

    id = Column(String(50), primary_key=True, nullable=False, default=uuid.uuid4)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def model_dump(self, mode: str = "json", exclude: set = None) -> Dict[str, Any]:
        """將 SQLAlchemy 模型轉換為字典"""
        exclude = exclude or set()
        result = {}

        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                if mode == "json" and isinstance(value, datetime):
                    result[column.name] = value.isoformat()
                else:
                    result[column.name] = value

        return result

    def model_copy(self):
        return copy.deepcopy(self.model_dump())

    async def update_wrap(self, db: AsyncSession, schema: Union[Dict, Type[BaseModel]], current_operator,
                          history_model=None) -> 'InternalBaseModel':
        from .base_history_model import BaseHistoryModel

        if history_model and not issubclass(type(history_model), BaseHistoryModel):
            raise TypeError("history_model must be a subclass of BaseHistoryModel")

        if not issubclass(type(schema), dict) and not issubclass(type(schema), BaseModel):
            raise TypeError("Schema must be a subclass of BaseModel or dict")

        original_model = self.model_copy()
        delta_dict = schema
        if issubclass(type(schema), BaseModel):
            delta_dict = schema.model_dump(exclude_unset=True, mode="json")

        for key, value in delta_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)

        operate = await Operate.generate_operate(original_model, self.model_dump())
        if not operate.add and not operate.remove and not operate.change:
            raise NoChangeException()

        await db.flush()
        await db.refresh(self)

        if history_model:
            if hasattr(history_model, f"{self.__tablename__}_id"):
                setattr(history_model, f"{self.__tablename__}_id", self.id)

            history_model.operator_id = current_operator.id
            history_model.operator_name = current_operator.name
            history_model.operator_type = current_operator.type
            history_model.operate = json.dumps(operate.model_dump(), ensure_ascii=False, indent=4)

            db.add(history_model)
            await db.flush()
            await db.refresh(history_model)

        return self

    async def create_wrap(self, db: AsyncSession, schema: Union[Dict, Type[BaseModel]], current_operator,
                          history_model=None) -> 'InternalBaseModel':
        from .base_history_model import BaseHistoryModel

        if history_model and not issubclass(type(history_model), BaseHistoryModel):
            raise TypeError("history_model must be a subclass of BaseHistoryModel")

        if not issubclass(type(schema), dict) and not issubclass(type(schema), BaseModel):
            raise TypeError("Schema must be a subclass of BaseModel or dict")

        delta_dict = schema
        if issubclass(type(schema), BaseModel):
            delta_dict = schema.model_dump(exclude_unset=True, mode="json")

        for key, value in delta_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)

        operate = await Operate.generate_operate(compare=self.model_dump())

        db.add(self)
        await db.flush()
        await db.refresh(self)

        if history_model:
            if hasattr(history_model, f"{self.__tablename__}_id"):
                setattr(history_model, f"{self.__tablename__}_id", self.id)

            history_model.operator_id = current_operator.id
            history_model.operator_name = current_operator.name
            history_model.operator_type = current_operator.type
            history_model.operate = json.dumps(operate.model_dump(), ensure_ascii=False, indent=4)

            db.add(history_model)
            await db.flush()
            await db.refresh(history_model)

        return self
