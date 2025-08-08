from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from inspect import isclass
from pathlib import Path
from types import ModuleType
from typing import Any, Generator, Iterable

from advanced_alchemy.config import SQLAlchemyAsyncConfig, SQLAlchemySyncConfig
from advanced_alchemy.repository import SQLAlchemyAsyncRepository, SQLAlchemySyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService
from attrs import define, field

from leaguemanager.core import get_settings
from leaguemanager.services.scheduling.base import ScheduleServiceBase
from leaguemanager.services.template_loader.league_importer import Importer

get_settings.cache_clear()
settings = get_settings()


@define
class DynamicObjectLoader:
    app_dir: Path = field()
    root_dir: Path = field()
    search_dir: Path = field()
    local_only: bool = field(default=False)

    @app_dir.default
    def _app_dir(self):
        return settings.LEAGUE_MANAGER_APP_DIR

    @root_dir.default
    def _root_dir(self):
        return settings.LEAGUE_MANAGER_ROOT_DIR

    @search_dir.default
    def _search_dir(self):
        return settings.LEAGUE_MANAGER_APP_DIR

    @classmethod
    def local_app(
        cls,
        app_dir: Path | None = None,
        root_dir: Path | None = None,
        search_dir: Path | None = None,
    ):
        """Creates a DynamicObjectLoader for a user's application

        Args:
            app_dir (Path | None, optional): The path to user's application. Defaults to None.
            root_dir (Path | None, optional): The path to the root of the user's application. Defaults to None.
            search_dir (Path | None, optional): The path to search for modules. Defaults to None.

        Returns:
            DynamicObjectLoader: A configured DynamicObjectLoader with defaults for user's application
        """
        if not app_dir:
            app_dir = settings.APP_DIR
        if not root_dir:
            root_dir = settings.APP_ROOT
        if not search_dir:
            search_dir = app_dir
        return cls(app_dir=app_dir, root_dir=root_dir, search_dir=search_dir, local_only=True)

    def _is_sync_repo(self, item: Any):
        """Checks if item is SQLAlchemySyncRepository class or subclass"""
        return isclass(item) and issubclass(item, SQLAlchemySyncRepository)

    def _is_async_repo(self, item: Any):
        """Checks if item is SQLAlchemyAsyncRepository class or subclass"""
        return isclass(item) and issubclass(item, SQLAlchemyAsyncRepository)

    def _is_sync_service(self, item: Any):
        """Checks if item is SQLAlchemySyncRepositoryService class or subclass."""
        return isclass(item) and issubclass(item, SQLAlchemySyncRepositoryService)

    def _is_async_service(self, item: Any):
        """Checks if item is SQLAlchemyAsyncRepositoryService class or subclass."""
        return isclass(item) and issubclass(item, SQLAlchemyAsyncRepositoryService)

    def _is_sync_config(self, item: Any):
        """Checks if item is a SQLAlchemySyncConfig.

        Using `isclass(item)` doesn't work here. May revisit at a later time.
        """
        return item.__class__ == SQLAlchemySyncConfig

    def _is_async_config(self, item: Any):
        """Checks if item is a SQLAlchemyAsyncConfig.

        Using `isclass(item)` doesn't work here. May revisit at a later time.
        """
        return item.__class__ == SQLAlchemyAsyncConfig

    def _is_importer(self, item: Any):
        """Checks if item is a Protocol of the Importer class."""
        return isclass(item) and issubclass(item, Importer)

    def _is_schedule(self, item: Any):
        """Checks if item is a ScheduleServiceBase class or subclass."""
        return isclass(item) and issubclass(item, ScheduleServiceBase)

    def get_repositories(
        self,
        is_async: bool = False,
        **kwargs,
    ) -> list[SQLAlchemySyncRepository | SQLAlchemyAsyncRepository]:
        """Returns all SQLAlchemySyncRepository or SQLAlchemyAsyncRepository classes dynamically.

        Args:
            is_async (bool, optional): If True, returns all SQLAlchemyAsyncRepository classes.
            Defaults to False.
        """
        if is_async:
            return self.load_objects(self.search_dir, self._is_async_repo)
        return self.load_objects(self.search_dir, self._is_sync_repo)

    def get_services(
        self,
        is_async: bool = False,
        **kwargs,
    ) -> list[SQLAlchemySyncRepositoryService | SQLAlchemyAsyncRepositoryService]:
        """Returns all SQLAlchemySyncRepositoryService or SQLAlchemyAsyncRepositoryService classes dynamically.

        Args:
            is_async (bool, optional): If True, returns all SQLAlchemyAsyncRepositoryService classes.
            Defaults to False.
        """
        if is_async:
            return self.load_objects(self.search_dir, self._is_async_service)
        return self.load_objects(self.search_dir, self._is_sync_service)

    def get_configs(self, is_async: bool = False) -> list[SQLAlchemySyncConfig | SQLAlchemyAsyncConfig]:
        """Gets all SQLAlchemySyncConfig or SQLAlchemyAsyncConfig classes dynamically.

        If try_local_first is True, the search will start on the host application, and if a config
        item is found, it will load instead of league manager's default.

        Args:
            is_async (bool, optional): If True, returns all SQLAlchemyAsyncConfig classes.
            Defaults to False.
        """
        if is_async:
            return self.load_objects(self.search_dir, self._is_async_config, local_only=self.local_only)
        return self.load_objects(self.search_dir, self._is_sync_config, local_only=self.local_only)

    def get_importers(self) -> list[Importer]:
        """Returns all Importer classes dynamically.

        This will return all classes that implement the Importer protocol.
        """
        return self.load_objects(self.search_dir, self._is_importer, local_only=self.local_only)

    def get_schedule_services(self) -> list[ScheduleServiceBase]:
        """Returns all ScheduleServiceBase classes dynamically.

        This is used to load scheduling services that are defined in the user's application.

        For now, only implemented to look at internally defined modules.
        """

        return self.load_objects(self.search_dir, self._is_schedule, local_only=self.local_only)

    def load_objects(
        self,
        search_dir: Path,
        compare: callable,
        local_only: bool = False,
    ) -> Iterable[ModuleType]:
        """Looks through a list of objects and returns them based on a comparison function.

        If `local_only` is True, then it will only search the local directory for modules. Use this to
        override League Manager's default search location.

        Args:
            search_dir (Path): Directory name to search recursively
            compare (bool): Boolean comparison of all py files in `search_dir` directory
            local_only (bool): If True, only search the local directory for modules. Defaults to False.

        Returns:
            list: All modules that match the `compare` function.
        """
        items = []
        if local_only:
            _full_paths = self.full_paths(search_dir)
            items += self.collect_matching_objects(_full_paths, compare, is_dotted_path=False)
        else:
            _dotted_paths = self.dotted_paths(search_dir)
            items += self.collect_matching_objects(_dotted_paths, compare)
        return items

    def collect_matching_objects(
        self,
        modules: Iterable[str | Path],
        compare: callable,
        is_dotted_path: bool = True,
    ) -> Iterable[ModuleType]:
        """Looks for all classes that match the `compare` function in a list of dotted paths.

        It expects a list of dotted paths to modules. It attempts to import each item, ignoring
        circular imports and modules that don't exist. If a module has an `__all__` attribute, it
        will only run the compare function on items in that attribute, and will only return unique
        items found.

        Args:
            modules (list[str]): List of dotted paths to modules
            compare (callable | bool): Boolean comparison of all py files in `search_dir` directory. If set
                to True, then all items in the module will be returned.
            is_dotted_path (bool, optional): Expects `modules` to be a list of dotted relative paths to modules (e.g. "app.app").
                If False, expects a list of full paths (e.g. /home/user/app/app.py). Defaults to True.

        Returns:
            list: All modules that match the `compare` function.
        """
        items = []
        for mod in modules:
            if "__init__" in str(mod):
                continue
            try:
                if not is_dotted_path:
                    _module = self.import_module_from_full_path(mod.stem, str(mod))
                else:
                    _module = import_module(mod)

            except AttributeError:
                # Ignore modules that create circular imports
                continue
            except ModuleNotFoundError:
                # Ignore modules that don't exist
                continue
            except Exception as e:
                print(f"Failed to import {mod} due to: {e}")
                return None
            if hasattr(_module, "__all__"):
                objs = [getattr(_module, obj) for obj in _module.__all__]
                if not objs:
                    print("No objects found")
                    continue
                items += [o for o in objs if compare(o) and o not in items]
        return items

    def dotted_paths(self, search_path: Path) -> Generator[str, None, None]:
        """Creates dotted paths to all .py files in `search_path` directory.

        Will exclude any files in directories in the `_exclude` list.

        Args:
            search_path (Path): Directory name to search recursively

        Returns:
            Generator[str]: Generator of dotted paths to all .py files in `search_path` directory
        """
        _exclude = [".venv", "venv", "tests", "test", "docs", "migrations", "__main__", "__init__"]
        for _file in search_path.rglob("**/*.py"):
            mod_path = str(_file.relative_to(self.root_dir)).replace("/", ".")
            if any(e in mod_path for e in _exclude):
                continue
            yield f"{mod_path[:-3]}"

    def full_paths(self, search_path: Path) -> Generator[Path, None, None]:
        """Creates full paths to all .py files in `search_path` directory.

        Will exclude any files in directories in the `_exclude` list.

        Args:
            search_path (Path): Directory name to search recursively

        Returns:
            Generator[Path]: Generator of full paths to all .py files in `search_path` directory
        """
        _exclude = ["tests", "test", "docs", "migrations", "__main__", "__init__"]
        for _file in search_path.rglob("**/*.py"):
            if any(e in str(_file) for e in _exclude):
                continue
            yield _file

    def import_module_from_full_path(self, module_name: str, full_path: str) -> Any:
        spec = spec_from_file_location(module_name, full_path)
        _module = module_from_spec(spec)
        spec.loader.exec_module(_module)
        return _module
