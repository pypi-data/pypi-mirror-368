from __future__ import annotations

from typing import Iterator

from attrs import define, field
from sqlalchemy import select
from sqlalchemy.orm import Session

from leaguemanager.services._typing import (
    ImporterT,
    ModelT,
    ScheduleServiceT,
    SyncServiceT,
)

__all__ = ["ServiceManagement", "ImporterManagement", "SchedulerManagement"]


@define
class ServiceManagement:
    """Manages a SQLAlchemySyncRepositoryService[ModelT] class.

    TODO: Async support

    Given the `service_type` and `db_session`, as well as a db_session, it will hold then provide
    the applicable service (for the corresponding service type.). The `get_service` property will
    return the appropriate service for the given `service_type` and `db_session`.

    Attributes:
        service_type (type[SyncServiceT] | type[AsyncServiceT]): Service type to manage.
        model_type (type[ModelT]): Model type for the given `service_type`.
        db_session (Session | None): Database session to use for the service.

    Example:
      >>> _service = ServiceManagement(
      ...     service_type=SeasonSyncService, model_type=Season, db_session=session
      ... )
      >>> _service.get_service
    """

    service_type: type[SyncServiceT] = field()
    db_session: Session = field(default=None)
    model_type: type[ModelT] = field(init=False)

    def __attrs_post_init__(self):
        self.model_type = self.service_type.repository_type.model_type

    @property
    def get_service(self) -> Iterator[ServiceManagement.service_type]:  # type: ignore[return]
        with self.service_type.new(session=self.db_session, statement=select(self.model_type)) as service:
            yield service


@define
class ImporterManagement:
    """Manages Importer services.

    Provides a basic utility to manage importers for league data. It takes an `importer_type` and provides
    an instance of that importer type through the `get_importer` property. It can be used to register
    a specific importer type for league data management.

    Attributes:
        importer_type (type[ImporterT]): Importer type to manage.

    Example:
      >>> _importer = ImporterManagement(importer_type=LeagueImporter)
      >>> _importer.get_importer
    """

    importer_type: type[ImporterT] = field()

    @property
    def get_importer(self) -> ImporterT:
        return self.importer_type()


@define
class SchedulerManagement:
    """Manages scheduling services.

    Provides a basic utility to manage scheduling services for league data. It takes a `scheduler_type` and provides
    an instance of that scheduler type through the `get_scheduler` property. It can be used to register
    a specific scheduler type for league scheduling management.

    Attributes:
        service_type (type[SyncServiceT]): Service type to manage.

    Example:
      >>> _scheduler = SchedulerManagement(service_type=BracketSchedule)
      >>> _scheduler.get_service
    """

    scheduler_type: type[ScheduleServiceT] = field()

    @property
    def get_scheduler(self) -> ScheduleServiceT:
        return self.scheduler_type()
