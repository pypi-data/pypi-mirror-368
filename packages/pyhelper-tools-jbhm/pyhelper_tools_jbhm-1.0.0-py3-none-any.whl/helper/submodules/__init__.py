import os
import importlib
from typing import List

_submodules_dir = os.path.dirname(__file__)

_exported_functions: List[str] = []

for filename in os.listdir(_submodules_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = filename[:-3]
        module = importlib.import_module(f".{module_name}", package=__package__)

        for name, obj in vars(module).items():
            if callable(obj) and not name.startswith("_"):
                globals()[name] = obj
                _exported_functions.append(name)

__all__ = _exported_functions