from .core import *

import os
import importlib

__version__ = "1.0.0"
__name__ = "pyhelper-tools-jbhm"

_submodules_dir = os.path.join(os.path.dirname(__file__), "submodules")
_submodules_package = __name__ + ".submodules"

__submodules__ = []
for filename in os.listdir(_submodules_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = filename[:-3]
        importlib.import_module(f"{_submodules_package}.{module_name}")
        __submodules__.append(module_name)

globals().update(
    {
        name: importlib.import_module(f"{_submodules_package}.{name}")
        for name in __submodules__
    }
)

__all__ = __submodules__ + [
    "sys",
    "ast",
    "pd",
    "Path",
    "Dict",
    "Set",
    "json",
    "csv",
    "ET",
    "Union",
    "List",
    "sns",
    "mpl"
    "tk",
    "messagebox",
    "ScrolledText",
    "np",
    "plt",
    "re",
    "inspect",
    "asyncio",
    "Callable",
    "time",
    "os",
    "re",
    "help",
    "format_number",
    "config",
    "REGISTRY",
    "register",
    "NORMAL_SIZE",
    "BIG_SIZE",
    "CONFIG_LANG",
    "set_language",
    "t",
    "show_gui_popup",
    "load_user_translations",
    "Optional",
    "filedialog"
]