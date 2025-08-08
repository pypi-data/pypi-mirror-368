from __future__ import annotations

from typing import Any

import attrs
from advanced_alchemy.repository import (
    SQLAlchemyAsyncSlugRepository,
    SQLAlchemySyncSlugRepository,
)
from sqlalchemy import select

from leaguemanager import models as m
from leaguemanager.services._typing import ModelT
from leaguemanager.services.base import (
    SQLAlchemyAsyncRepositoryService,
    SQLAlchemySyncRepositoryService,
    is_dict_with_field,
    is_dict_without_field,
)

__all__ = ["RoleSyncService", "RoleAsyncService"]


class RoleSyncService(SQLAlchemySyncRepositoryService):
    """Handles database operations for roles data."""

    class SlugRepo(SQLAlchemySyncSlugRepository[m.Role]):
        """Role repository."""

        model_type = m.Role

    repository_type = SlugRepo

    def to_model_on_create(
        self,
        data: ModelT | dict[str, Any],
    ) -> ModelT:
        if attrs.has(data):
            data = attrs.asdict(data)
        if is_dict_without_field(data, "slug"):
            data["slug"] = self.repository.get_available_slug(data["name"])
        return data

    def to_model_on_update(self, data):
        if attrs.has(data):
            data = attrs.asdict(data)
        if is_dict_without_field(data, "slug") and is_dict_with_field(data, "name"):
            data["slug"] = self.repository.get_available_slug(data["name"])
        return data


class RoleAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for roles data."""

    class SlugRepo(SQLAlchemyAsyncSlugRepository[m.Role]):
        """Role repository."""

    model_type = m.Role

    repository_type = SlugRepo

    async def to_model_on_create(
        self,
        data: ModelT | dict[str, Any],
    ) -> ModelT:
        if attrs.has(data):
            data = attrs.asdict(data)
        if is_dict_without_field(data, "slug"):
            data["slug"] = await self.repository.get_available_slug(data["name"])
        return data

    async def to_model_on_update(self, data):
        if attrs.has(data):
            data = attrs.asdict(data)
        if is_dict_without_field(data, "slug") and is_dict_with_field(data, "name"):
            data["slug"] = await self.repository.get_available_slug(data["name"])
        return data
