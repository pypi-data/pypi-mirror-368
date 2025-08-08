from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field
from sqlalchemy import UUID as _UUID
from sqlalchemy import Column, DateTime, ForeignKey, Table
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import UUIDBase, mapper, metadata

if TYPE_CHECKING:
    from .role import Role
    from .user import User


@define(slots=False)
class UserRole(UUIDBase):
    """A relationship link between a user and a role."""

    user_id: UUID | None = field(default=None)
    role_id: UUID | None = field(default=None)
    assigned_at: datetime = field(factory=lambda: datetime.now(UTC))

    # user_name: AssociationProxy = association_proxy("user", "username")
    # role_name: AssociationProxy = association_proxy("role", "name")


# SQLAlchemy Imperative Mapping

user_role = Table(
    "user_role",
    metadata,
    Column("user_id", _UUID, ForeignKey("user.id"), primary_key=True),
    Column("role_id", _UUID, ForeignKey("role.id"), primary_key=True),
    Column("assigned_at", DateTime, nullable=False),
)

# ORM Relationships

mapper.map_imperatively(
    UserRole,
    user_role,
    properties={
        "user": relationship("User", back_populates="user_roles"),
        "role": relationship("Role", back_populates="user_roles"),
    },
)
