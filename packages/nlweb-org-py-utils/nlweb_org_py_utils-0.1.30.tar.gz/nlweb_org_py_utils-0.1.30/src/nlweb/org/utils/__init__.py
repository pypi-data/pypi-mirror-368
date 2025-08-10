class LOADER:

    @classmethod
    def AppendFolderToPath(cls, folder:str):
        '''👉️ Appends a folder to the system path.'''
        import sys
        from pathlib import Path

        # Path to the folder containing this __init__.py
        current_dir = Path(__file__).resolve().parent

        # Path to the 'tests' folder (child folder)
        folder_dir = current_dir / folder

        # Add to sys.path if not already there
        if str(folder_dir) not in sys.path:
            sys.path.append(str(folder_dir))


    @classmethod
    def LoadImports(cls):
        '''👉 Loads the imports.'''
        cls.AppendFolderToPath('init')
        from .IMPORTS import IMPORTS 
        

#LOADER.LoadImports()





# nlweb/org/utils/__init__.py
import importlib
import inspect
import pkgutil
from types import ModuleType
from typing import List

__all__: List[str] = []

PACKAGE_PREFIX = __name__ + "."
FILTER_PREFIX = "LOG_"        # only load modules/classes starting with LOG_

def _iter_modules(package_path):
    # Recurse into subpackages
    for mod_info in pkgutil.walk_packages(package_path, PACKAGE_PREFIX):
        yield mod_info.name

def _load_classes_from_module(mod: ModuleType):
    for name, obj in inspect.getmembers(mod, inspect.isclass):
        # only classes actually defined in this module (not re-exported)
        if obj.__module__ != mod.__name__:
            continue
        # keep only LOG_* classes (change/remove this if you want everything)
        if name.startswith(FILTER_PREFIX):
            globals()[name] = obj
            __all__.append(name)

# Discover and import every module whose basename starts with LOG_
for fqmn in _iter_modules(__path__):  # type: ignore[name-defined]
    base = fqmn.rsplit(".", 1)[-1]
    if base.startswith(FILTER_PREFIX):
        mod = importlib.import_module(fqmn)
        _load_classes_from_module(mod)
