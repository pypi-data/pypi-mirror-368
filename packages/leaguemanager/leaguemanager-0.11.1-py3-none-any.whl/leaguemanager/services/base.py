from typing import Any

import attrs
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService as _SQLAlchemyAsyncRepositoryService
from advanced_alchemy.service import SQLAlchemySyncRepositoryService as _SQLAlchemySyncRepositoryService
from advanced_alchemy.service import is_dict_with_field, is_dict_without_field

from ._typing import ModelT


class SQLAlchemySyncRepositoryService(_SQLAlchemySyncRepositoryService):
    """Introduces a `to_model` method to transform ModelT data to a dictionary. This is
    only necessary because SQLAlchemySyncRepositoryService does not work out of the box
    for attrs defined classes.
    """

    def to_model(
        self,
        data: ModelT | dict[str, Any],
        operation: str | None = None,
    ) -> ModelT:
        if attrs.has(data):
            data = attrs.asdict(data)
        return super().to_model(data, operation)


# Not sure if this is needed
# TODO: Seems like litestar checks if data received is a certain kind before transforming "to model"
class SQLAlchemyAsyncRepositoryService(_SQLAlchemyAsyncRepositoryService):
    """Introduces a `to_model` method to transform ModelT data to a dictionary. This is
    only necessary because SQLAlchemyAsyncRepositoryService does not work out of the box
    for attrs defined classes.
    """

    async def to_model(
        self,
        data: ModelT | dict[str, Any],
        operation: str | None = None,
    ) -> ModelT:
        if attrs.has(data):
            data = attrs.asdict(data)
        return await super().to_model(data, operation)
