from utils.assets import load_yaml_file

def import_module(module_name):
    return getattr(__import__(f'modules.{module_name}', fromlist=[module_name]), module_name)

def get_modules(key=None):
    modules = load_yaml_file('modules.yaml')
    if not key:
        return [import_module(module['className']) for module in modules.values()]
    if isinstance(key, list):
        return [get_modules(module) for module in key]
    if key in modules:
        return import_module(modules[key]['className'])
    from utils.exceptions import MissingModuleException
    raise MissingModuleException(key)