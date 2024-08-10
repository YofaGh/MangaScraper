from utils.assets import load_modules_yaml_file
from utils.models import Manga, Doujin

def __import_module(module_name: str) -> Manga | Doujin:
    return getattr(__import__(f'modules.{module_name}', fromlist=[module_name]), module_name)

def get_modules(key: str | list[str | list] | None = None) -> Manga | Doujin | list[Manga | Doujin | list]:
    modules = load_modules_yaml_file()
    if not key:
        return [__import_module(module['className']) for module in modules.values()]
    if isinstance(key, list):
        return [get_modules(module) for module in key]
    if key in modules:
        return __import_module(modules[key]['className'])
    from utils.exceptions import MissingModuleException
    raise MissingModuleException(key)