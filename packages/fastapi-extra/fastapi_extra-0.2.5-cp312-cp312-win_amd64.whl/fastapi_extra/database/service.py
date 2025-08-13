__author__ = "ziyan.yin"
__date__ = "2025-01-12"

from contextvars import ContextVar
from typing import Any, Generic, TypeVar

from fastapi_extra.database.model import SQLModel
from fastapi_extra.database.session import AsyncSession, DefaultSession
from fastapi_extra.dependency import AbstractService

Model = TypeVar("Model", bound=SQLModel)


class ModelService(AbstractService, Generic[Model], abstract=True):
    __slot__ = ()
    __model__: type[Model]
    __session_container__ = ContextVar[AsyncSession | None]("__session_container__", default=None)

    @classmethod
    def __class_getitem__(cls, item: type[SQLModel]) -> type["ModelService"]:
        if not issubclass(item, SQLModel):
            raise TypeError(f"type[SQLModel] expected, got {item}")
        if not (table_arg := item.model_config.get("table", None)):
            raise AttributeError(
                f"True expected for argument {item.__name__}.model_config.table, got {table_arg}"
            )

        class SubService(ModelService):
            __slot__ = ()
            __model__ = item

        return SubService

    def __init__(self, session: DefaultSession):
        self.__session_container__.set(session)

    @property
    def session(self) -> AsyncSession:
        _session = self.__session_container__.get()
        assert _session is not None, "Session is not initialized"
        return _session

    async def get(self, ident: int | str, **kwargs: Any) -> Model | None:
        return await self.session.get(self.__model__, ident, **kwargs)

    async def create_model(self, **kwargs: Any) -> Model:
        model = self.__model__.model_validate(kwargs)
        self.session.add(model)
        await self.session.flush()
        return model

    async def delete(self, model: Model) -> None:
        return await self.session.delete(model)
