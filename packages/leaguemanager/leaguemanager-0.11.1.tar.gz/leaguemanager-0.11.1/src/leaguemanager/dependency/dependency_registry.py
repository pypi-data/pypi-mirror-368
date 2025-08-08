from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from typing import Any, AsyncGenerator, Generator

from attrs import define, field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from svcs import Container, Registry

from leaguemanager.core import get_settings
from leaguemanager.db import async_config, get_async_session, get_session, sync_config, validate_config
from leaguemanager.dependency.loader import DynamicObjectLoader
from leaguemanager.dependency.managers import ImporterManagement, SchedulerManagement, ServiceManagement
from leaguemanager.services._typing import (
    AsyncServiceT,
    ImporterT,
    ScheduleServiceT,
    SQLAlchemyAsyncConfigT,
    SQLAlchemySyncConfigT,
    SyncServiceT,
)

__all__ = ["LeagueManager"]

get_settings.cache_clear()
settings = get_settings()


@define
class LeagueManager:
    """Registry for managing services.

    TODO: Serve up async repos/services

    If no `Registry` is provided, one will be created. Keep in mind that there should only
    be one registry per application.

    Services are kept in an svcs `Container` and are provided as needed. This includes a
    database session, League Manager "repositories" and "services" (which themselves provide
    common database operations), Advanced Alchemy database configuration objects, and other
    league related services (such as importers and schedulers).

    Attributes:
        service_registry (Registry | None): An `svcs` Registry for managing services.
        loader (DynamicObjectLoader): A DynamicObjectLoader for loading specific objects.
        local_base_dir (Path): The local base directory. Uses `settings.APP_DIR` by default.
        local_root_dir (Path): The local root directory. Uses `settings.APP_ROOT` by default.
        aa_config_dir (Path): The Advanced Alchemy configuration directory.
        get_session (Generator[Session, Any, None]): A generator for a database session.
        get_async_session (AsyncGenerator[AsyncSession, Any]): A generator for an async database session.
        sync_services (list[type[SyncServiceT]]): List of services for sync database operations.
        async_services (list[type[AsyncServiceT]]): List of services for async database operations.

    Example:
        >>> registry = LeagueManager()
        >>> season_service = registry.provide_db_service(SeasonSyncService)
        >>> team_service = registry.provide_db_service(TeamSyncService)
        >>>
        >>> season_service.list()  #  List all seasons
        >>> team_service.count()  #  Count number of teams

    """

    service_registry: Registry | None = field(default=None)

    loader: DynamicObjectLoader = field(default=DynamicObjectLoader())

    # Might make sense to make these private or keep them in post_init
    # Better to control these through the environment variables
    local_base_dir: Path = field(default=settings.APP_DIR)
    local_root_dir: Path = field(default=settings.APP_ROOT)
    aa_config_dir: Path | None = field(default=settings.ADVANCED_ALCHEMY_CONFIG_DIR)

    get_session: Generator[Session, Any, None] = field(default=get_session)
    get_async_session: AsyncGenerator[AsyncSession, Any] = field(default=get_async_session)

    sync_services: list[type[SyncServiceT]] = field(init=False)
    async_services: list[type[AsyncServiceT]] = field(init=False)

    # Useful for integrating with other apps/frameworks
    _SVCS_KEY_REGISTRY: str = field(default="league_manager_registry")
    _SVCS_KEY_CONTAINER: str = field(default="league_manager")

    def __attrs_post_init__(self):
        if not self.service_registry:
            self.service_registry = Registry()

        # Get Importer services
        _importers = self.loader.get_importers()

        # Get Scheduling services
        _schedulers = self.loader.get_schedule_services()

        # Get Advanced Alchemy services
        self.sync_services = self.loader.get_services()
        self.async_services = self.loader.get_services(is_async=True)

        if not settings.APP_DIR.name == settings.DEFAULT_MODULE_NAME and not settings.SEARCH_APP_MODULES:
            self.loader = self.loader.local_app()
            self.sync_services += self.loader.get_services()
            self.async_services += self.loader.get_services(is_async=True)

        # If no Advanced Alchemy config directory is set, use the default sync/async configs
        if not self.aa_config_dir:
            _sync_config = [sync_config]
            _async_config = [async_config]
        else:
            print(f"Loading Advanced Alchemy configurations from {self.aa_config_dir}")
            self.loader = self.loader.local_app(search_dir=self.loader.app_dir / self.aa_config_dir)
            _sync_config = self.loader.get_configs()
            _async_config = self.loader.get_configs(is_async=True)
            if not _sync_config and not _async_config:
                raise ValueError(
                    f"Cannot find any Advanced Alchemy configurations in {self.aa_config_dir}. "
                    "You may need to wrap the configuration within a function."
                )

        # Register objects
        for _importer in _importers:
            self.register_importer_service(importer_type=_importer)

        for _scheduler in _schedulers:
            self.register_scheduler_service(scheduler_type=_scheduler)

        for service_type in self.sync_services:
            self.register_db_service(service_type=service_type)

        for _config in _sync_config:
            _config = validate_config(_config)
            self.registry.register_value(SQLAlchemySyncConfigT, _config)
        for _config in _async_config:
            _config = validate_config(_config, is_async=True)
            self.registry.register_value(SQLAlchemyAsyncConfigT, _config)

    @property
    def registry(self) -> Registry:
        return self.service_registry

    @contextmanager
    def sync_session_container(self) -> Generator[Container, None, None]:
        """Create a container for a sync database session."""
        self.registry.register_factory(Session, self.get_session)
        with Container(self.registry) as container:
            yield container

    @asynccontextmanager
    async def async_session_container(self) -> AsyncGenerator[Container, None]:
        """Create a container for an async database session."""
        self.registry.register_factory(AsyncSession, self.get_async_session)
        async with Container(self.registry) as container:
            yield container

    def register_db_service(self, service_type: type[SyncServiceT]) -> None:
        """Register a League Manager service based on its type."""
        _service = ServiceManagement(service_type=service_type, db_session=self.provide_db_session)
        self.registry.register_value(service_type, next(_service.get_service))

    def register_importer_service(self, importer_type: type[ImporterT]) -> None:
        """Register an importer service based on the type specified."""
        _importer = ImporterManagement(importer_type=importer_type)
        self.registry.register_value(importer_type, _importer.get_importer)

    def register_scheduler_service(self, scheduler_type: type[ScheduleServiceT]) -> None:
        """Register a scheduling service based on its type."""
        _scheduler = SchedulerManagement(scheduler_type=scheduler_type)
        self.registry.register_value(scheduler_type, _scheduler.get_scheduler)

    # Retrieve and provide dependencies

    @property
    def provide_db_session(self) -> Session:
        """Provide a sync database session."""
        with self.sync_session_container() as container:
            return container.get(Session)

    @property
    def provide_async_db_session(self) -> AsyncSession:
        """Provide an async database session."""
        with self.async_session_container() as container:
            return container.get(AsyncSession)

    @property
    def provide_sync_config(self) -> SQLAlchemySyncConfigT:
        return Container(self.registry).get(SQLAlchemySyncConfigT)

    @property
    def provide_async_config(self) -> SQLAlchemyAsyncConfigT:
        return Container(self.registry).get(SQLAlchemyAsyncConfigT)

    def provide_db_service(self, service_type: type[SyncServiceT]) -> type[SyncServiceT]:
        """Provide a League Manager service based on its type."""
        return Container(self.registry).get(service_type)

    def provide_importer_service(self, importer_type: type[ImporterT]) -> ImporterT:
        """Provide an importer service based on the type specified."""
        return Container(self.registry).get(importer_type)

    def provide_scheduler_service(self, scheduler_type: type[ScheduleServiceT]) -> ScheduleServiceT:
        """Provide a scheduling service based on the type specified."""
        return Container(self.registry).get(scheduler_type)
