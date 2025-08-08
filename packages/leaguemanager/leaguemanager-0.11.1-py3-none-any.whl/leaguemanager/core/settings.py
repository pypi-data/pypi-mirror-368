import os
from functools import lru_cache
from importlib.util import find_spec
from pathlib import Path

from attrs import define, field


@define
class Settings:
    # League Manager app info
    DEFAULT_MODULE_NAME: str = "leaguemanager"
    LEAGUE_MANAGER_APP_DIR: Path = field()
    LEAGUE_MANAGER_ROOT_DIR: Path = field()

    @LEAGUE_MANAGER_APP_DIR.default
    def _default_module_path(self):
        return self._module_to_os_path(self.DEFAULT_MODULE_NAME)

    @LEAGUE_MANAGER_ROOT_DIR.default
    def _default_root_path(self):
        return self.LEAGUE_MANAGER_APP_DIR.parent.resolve()

    DATE_FORMAT: str = field(default="%Y-%m-%d %H:%M:%S")
    SYNTH_DATA_DIR: Path = field(init=False)
    TEMPLATE_LOADER_DIR: Path = field(init=False)
    EXCEL_TEMPLATE_DIR: Path = field(init=False)

    SEARCH_APP_MODULES: bool = field(default=False)

    def __attrs_post_init__(self):
        self.SYNTH_DATA_DIR: Path = Path(self.LEAGUE_MANAGER_APP_DIR) / "db/synthetic_data"
        self.TEMPLATE_LOADER_DIR: Path = Path(self.LEAGUE_MANAGER_APP_DIR) / "services" / "template_loader"
        self.EXCEL_TEMPLATE_DIR: Path = Path(self.LEAGUE_MANAGER_APP_DIR) / "db" / "importer_templates" / "excel"

        if _search_app := os.getenv("SEARCH_APP_MODULES"):
            self.SEARCH_APP_MODULES = bool(_search_app)

    @property
    def APP_DIR(self):
        if _app_dir := os.getenv("APP_DIR"):
            try:
                app_dir = Path(_app_dir)
                if app_dir.is_dir():
                    return app_dir
            except ValueError:
                print(f"Environment Variable refers to invalid directory: {_app_dir}")
        return Path.cwd()

    @property
    def APP_ROOT(self):
        if _app_root := os.getenv("APP_ROOT"):
            try:
                app_root = Path(_app_root)
                if app_root.is_dir():
                    return app_root
            except ValueError:
                print(f"Environment Variable refers to invalid directory: {_app_root}")
        return Path.cwd()

    @property
    def ADVANCED_ALCHEMY_CONFIG_DIR(self):
        if self.APP_DIR.name == self.DEFAULT_MODULE_NAME:
            return None
        if _aa_config_module := os.getenv("ADVANCED_ALCHEMY_CONFIG_DIR"):
            _aa_config_dir = self.APP_DIR / _aa_config_module
            if not Path(_aa_config_dir).is_dir():
                raise ValueError(f"Environment Variable refers to invalid directory: {_aa_config_dir}")
            return _aa_config_dir
        else:
            return None

    @property
    def MIGRATION_PATH(self):
        if "MIGRATION_PATH" in os.environ:
            migration_path = Path(os.getenv("MIGRATION_PATH"))
            return Path(self.APP_DIR / migration_path, exist_ok=True)
        else:
            return self.APP_DIR / "migrations"

    @property
    def MIGRATION_CONFIG(self):
        if "MIGRATION_CONFIG" in os.environ:
            return Path(os.getenv("MIGRATION_CONFIG"))
        else:
            return self.APP_DIR

    @property
    def ALEMBIC_TEMPLATE_PATH(self):
        if "ALEMBIC_TEMPLATE_PATH" in os.environ:
            return Path(os.getenv("ALEMBIC_TEMPLATE_PATH"))
        else:
            return Path(self.LEAGUE_MANAGER_APP_DIR) / "db/alembic_templates"

    @property
    def SQLITE_DATA_DIRECTORY(self):
        if "SQLITE_DATA_DIRECTORY" in os.environ:
            return os.getenv("SQLITE_DATA_DIRECTORY")
        return self.APP_DIR / "data_league_db"

    def _module_to_os_path(self, module_name: str) -> Path:
        """Get the string path of the module."""
        spec = find_spec(module_name)
        if not spec:
            raise ValueError(f"Couldn't find path for {module_name}")
        return Path(spec.origin).parent.resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()
