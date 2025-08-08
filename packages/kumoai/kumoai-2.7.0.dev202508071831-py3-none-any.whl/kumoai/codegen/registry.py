from __future__ import annotations

import importlib
import pkgutil
from typing import Callable, Dict, List, NamedTuple, Optional, Sequence, Type

from kumoai.codegen.edits import UniversalReplacementEdit
from kumoai.codegen.naming import NameManager


class Handler(NamedTuple):
    parents: Callable[[object], List[object]]
    required_imports: Callable[[object], List[str]]
    emit_lines: Callable[[object, str, dict[int, str], dict], List[str]]
    detect_edits: Optional[Callable[[object, object, NameManager],
                                    Sequence[UniversalReplacementEdit]]]


REG: dict[Type, Handler] = {}


def _discover_and_register_handlers() -> None:
    """Dynamically discover and import all modules in the 'handlers' folders,
    call their `get_handlers` function, and register the returned handlers.
    """
    from . import handlers

    handlers_dir = handlers.__path__
    prefix = f"{handlers.__name__}."

    for _, module_name, _ in pkgutil.iter_modules(handlers_dir, prefix):
        module = importlib.import_module(module_name)
        if hasattr(module, "get_handlers"):
            handlers_to_register: Dict[Type, Handler] = (module.get_handlers())
            for cls, handler in handlers_to_register.items():
                if cls in REG:
                    print(f"Warning: Overwriting handler for {cls.__name__}")
                REG[cls] = handler


_discover_and_register_handlers()
