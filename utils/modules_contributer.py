from typing import TypeVar, Optional
from utils.assets import load_modules_yaml_file
from utils.models import Manga, Doujin

T = TypeVar("T", bound="NestedModule")
NestedModule = Manga | Doujin | list[T]

_imported_modules_cache: dict[str, Manga | Doujin] = {}
_modules_yaml_cache: Optional[dict] = None


def _load_cached_modules_yaml() -> dict:
    global _modules_yaml_cache
    if _modules_yaml_cache is None:
        _modules_yaml_cache = load_modules_yaml_file()
    return _modules_yaml_cache


def __import_module(module_name: str) -> Manga | Doujin:
    if module_name not in _imported_modules_cache:
        _imported_modules_cache[module_name] = getattr(
            __import__(f"modules.{module_name}", fromlist=[module_name]), module_name
        )()
    return _imported_modules_cache[module_name]


def get_modules(key: str | list[str | list] | None = None) -> NestedModule:
    modules = _load_cached_modules_yaml()
    if not key:
        return [__import_module(module["className"]) for module in modules.values()]
    if isinstance(key, list):
        return [get_modules(module) for module in key]
    if key in modules:
        return __import_module(modules[key]["className"])
    from utils.exceptions import MissingModuleException

    raise MissingModuleException(key)
