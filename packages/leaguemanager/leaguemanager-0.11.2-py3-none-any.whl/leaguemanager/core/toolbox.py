from datetime import datetime

from sqlalchemy import delete
from sqlalchemy.orm import Session

from leaguemanager.core import get_settings
from leaguemanager.models.base import UUIDBase

settings = get_settings()


def clear_table(session: Session, model: UUIDBase) -> None:
    """Clears table of given model."""
    session.execute(delete(model))


def str_to_iso(date_string: str, format: str):
    """Converts string to datetime object."""
    return datetime.strptime(date_string, format)
