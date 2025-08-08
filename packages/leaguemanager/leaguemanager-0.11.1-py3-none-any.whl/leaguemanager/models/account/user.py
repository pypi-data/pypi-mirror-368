from datetime import UTC, datetime

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Boolean, Column, DateTime, String, Table
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import IndividualBase, add_slug_column, mapper, metadata

if TYPE_CHECKING:
    from .user_role import UserRole


@define(slots=False)
class User(IndividualBase):
    """A user of the system."""

    username: str | None = field(default=None, validator=validators.optional(validators.max_len(40)))
    email: str | None = field(default=None, validator=validators.max_len(40))
    password: str | None = field(default=None, validator=validators.max_len(32))
    active: bool = field(default=True)
    superuser: bool = field(default=False)
    joined: datetime | None = field(factory=lambda: datetime.now(UTC))

    @classmethod
    def signup(cls, email: str) -> "User":
        return cls(
            username=email,
            email=email,
            password="",
            active=True,
            superuser=False,
        )


# SQLAlchemy Imperative Mapping

user = Table(
    "user",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("username", String(40), unique=True, nullable=True),
    Column("email", String(40), unique=True, nullable=False),
    Column("password", String(32), nullable=False),
    Column("active", Boolean, default=True),
    Column("superuser", Boolean, default=False),
    Column("joined", DateTime, default=lambda: datetime.now(UTC)),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)

# ORM Relationships

mapper.map_imperatively(
    User,
    user,
    properties={
        "user_roles": relationship("UserRole", back_populates="user"),
        # "admin": relationship("Admin", back_populates="user"),
    },
)
