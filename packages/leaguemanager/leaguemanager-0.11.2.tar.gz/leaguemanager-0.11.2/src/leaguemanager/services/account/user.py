from __future__ import annotations

from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.repository import SQLAlchemyAsyncRepository, SQLAlchemySyncRepository
from sqlalchemy import select

from leaguemanager.models import User, UserRole
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["UserSyncService", "UserAsyncService", "UserRoleSyncService", "UserRoleAsyncService"]


class UserSyncService(SQLAlchemySyncRepositoryService):
    """Handles user database operations."""

    class Repo(SQLAlchemySyncRepository[User]):
        """User repository."""

        model_type = User

    repository_type = Repo


class UserRoleSyncService(SQLAlchemySyncRepositoryService):
    """Handles database operations in the user/role association."""

    class Repo(SQLAlchemySyncRepository[UserRole]):
        """User repository."""

        model_type = UserRole

    repository_type = Repo


class UserAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles user database operations."""

    class Repo(SQLAlchemyAsyncRepository[User]):
        """User repository."""

        model_type = User

    repository_type = Repo


class UserRoleAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations in the user/role association."""

    class Repo(SQLAlchemyAsyncRepository[UserRole]):
        """User repository."""

        model_type = UserRole

    repository_type = Repo
