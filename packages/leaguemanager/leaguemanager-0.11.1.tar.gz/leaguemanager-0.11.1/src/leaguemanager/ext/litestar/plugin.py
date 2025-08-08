from __future__ import annotations

from logging import Logger
from typing import TYPE_CHECKING

from advanced_alchemy.extensions.litestar.providers import create_service_provider
from attrs import define, field
from typing_extensions import override

from leaguemanager.dependency.dependency_registry import LeagueManager
from litestar.di import Provide
from litestar.exceptions import ImproperlyConfiguredException
from litestar.plugins import InitPlugin

from .oauth import AccessTokenState, OAuth2AuthorizeCallback, OAuth2Token

if TYPE_CHECKING:
    from litestar.app import Litestar
    from litestar.config.app import AppConfig
    from litestar.datastructures.state import State


logger = Logger(__name__)


@define
class LMPluginConfig:
    """Configuration for the LeagueManager plugin."""

    league_manager: LeagueManager | None = None
    league_manager_state_key: str = field(default="lm")
    service_provider_state_key: str = field(default="service_provider")

    include_auth: bool = field(default=True)

    registry_key: str = field(init=False)
    container_key: str = field(init=False)

    def __attrs_post_init__(self) -> None:
        if self.league_manager is None:
            try:
                from leaguemanager import LeagueManager

                self.league_manager = LeagueManager()
            except ImportError as e:
                raise ImportError("LeagueManager is not installed. Please install it to use the LM Dashboard.") from e
        self.registry_key = self.league_manager._SVCS_KEY_REGISTRY
        self.container_key = self.league_manager._SVCS_KEY_CONTAINER


class LMPlugin(InitPlugin):
    """Plugin to integrate LeagueManager into Litestar applications."""

    _league_manager: LeagueManager

    def __init__(self, config: LMPluginConfig) -> None:
        """Initialize the plugin with the provided configuration."""
        self._config = config

    def provide_lm(self, state: State) -> LeagueManager:
        league_manager = state.get(self._config.league_manager_state_key)
        assert league_manager is not None
        return league_manager

    def lm_service_provider(self, state: State) -> LeagueManager:
        """Provide the LeagueManager instance from the app state."""
        league_manager = state.get(self._config.league_manager_state_key)
        if league_manager is None:
            raise ImproperlyConfiguredException("LeagueManager is not available in the app state.")
        return league_manager.provide_db_service

    def add_lm_to_app(self, app: Litestar) -> None:
        if self._config.league_manager:
            league_manager = self._config.league_manager
            logger.info("Using provided LeagueManager instance.")
        else:
            msg = "LeagueManager class must be provided."
            raise ImproperlyConfiguredException(
                msg,
            )
        app.state.update({self._config.league_manager_state_key: league_manager})

    @override
    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        app_config.dependencies.update(
            {
                self._config.league_manager_state_key: Provide(self.provide_lm, sync_to_thread=False),
                self._config.service_provider_state_key: Provide(self.lm_service_provider, sync_to_thread=False),
            }
        )
        app_config.on_startup.insert(0, self.add_lm_to_app)
        app_config.signature_namespace.update(
            {
                "LeagueManager": LeagueManager,
            }
        )
        if self._config.include_auth:
            app_config.signature_namespace.update(
                {
                    "OAuth2AuthorizeCallback": OAuth2AuthorizeCallback,
                    "AccessTokenState": AccessTokenState,
                    "OAuth2Token": OAuth2Token,
                },
            )
        return app_config
