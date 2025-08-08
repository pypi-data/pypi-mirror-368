from attrs import define, field, validators
from sqlalchemy import UUID as _UUID
from sqlalchemy import Column, String, Table
from sqlalchemy.orm import relationship

from leaguemanager.models.base import UUIDBase, add_slug_column, mapper, metadata


@define(slots=False)
class Role(UUIDBase):
    """A role defining permissions in the system."""

    name: str | None = field(default=None, validator=validators.max_len(12))
    description: str | None = field(default=None, validator=validators.optional(validators.max_len(80)))
    slug: str | None = field(default=None, validator=validators.optional(validators.max_len(100)))


# SQLAlchemy Imperative Mapping

role = Table(
    "role",
    metadata,
    Column("id", _UUID, primary_key=True),
    Column("name", String(12), nullable=False),
    Column("description", String(80), nullable=True),
)

# Add slug column and constraints
add_slug_column(role)

# ORM Relationships

mapper.map_imperatively(Role, role, properties={"user_roles": relationship("UserRole", back_populates="role")})
