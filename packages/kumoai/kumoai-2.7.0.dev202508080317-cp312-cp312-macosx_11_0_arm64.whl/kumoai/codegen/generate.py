from __future__ import annotations

import ast
import logging
import os
from collections import OrderedDict
from typing import Any, Optional

from kumoai.codegen.exceptions import (
    CyclicDependencyError,
    UnsupportedEntityError,
)
from kumoai.codegen.loader import load_from_id
from kumoai.codegen.naming import NameManager
from kumoai.codegen.registry import REG, Handler

logger = logging.getLogger(__name__)


def _get_handler(obj_type: type) -> Handler:
    if obj_type not in REG:
        raise UnsupportedEntityError(
            f"No handler registered for type: {obj_type.__name__}")
    return REG[obj_type]


def _execute_creation_code(
    creation_lines: list[str],
    import_lines: list[str],
    parent_objects: dict[str, Any],
    expected_var_name: str,
) -> Any:
    """Execute code to create baseline object for edit detection."""
    try:
        import kumoai as kumo

        local_env = {"kumo": kumo}
        local_env.update(parent_objects)

        for import_line in import_lines:
            exec(import_line, local_env)

        for line in creation_lines:
            exec(line, local_env)

        if expected_var_name in local_env:
            return local_env[expected_var_name]

        for line in creation_lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                tree = ast.parse(line)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                var_name = target.id
                                if var_name in local_env:
                                    return local_env[var_name]
            except SyntaxError:
                continue
        return None
    except Exception:
        return None


def _generate(
    obj: object,
    name_manager: NameManager,
    seen: dict[int, str],
    stack: set[int],
    context: Optional[dict] = None,
) -> tuple[list[str], list[str]]:
    obj_id = id(obj)
    if obj_id in seen:
        return [], []
    if obj_id in stack:
        raise CyclicDependencyError(
            f"Cyclic dependency detected for object ID: {obj_id}")

    stack.add(obj_id)
    handler = _get_handler(type(obj))
    all_imports, all_lines = [], []

    parent_objects = {}
    for parent in handler.parents(obj):
        parent_imports, parent_lines = _generate(parent, name_manager, seen,
                                                 stack, context)
        all_imports.extend(parent_imports)
        all_lines.extend(parent_lines)
        parent_objects[seen[id(parent)]] = parent

    var_name = name_manager.assign_entity_variable(obj)
    seen[obj_id] = var_name
    parent_map = {id(p): seen[id(p)] for p in handler.parents(obj)}

    all_imports.extend(handler.required_imports(obj))
    creation_lines = handler.emit_lines(obj, var_name, parent_map, context
                                        or {})
    all_lines.extend(creation_lines)

    if handler.detect_edits:
        baseline_obj = _execute_creation_code(
            creation_lines,
            handler.required_imports(obj),
            parent_objects,
            var_name,
        )
        if baseline_obj is not None:
            edits = handler.detect_edits(obj, baseline_obj, name_manager)
            for edit in edits:
                all_lines.extend(edit.emit_lines(var_name))
                all_imports.extend(edit.required_imports)

    stack.remove(obj_id)
    return all_imports, all_lines


def _load_entity_from_spec(input_spec: dict[str, Any]) -> object:
    """Load entity from input specification."""
    if "id" in input_spec:
        entity_class = input_spec.get("entity_class")
        return load_from_id(input_spec["id"], entity_class)
    elif "json" in input_spec:
        raise NotImplementedError("JSON loading not yet implemented")
    elif "object" in input_spec:
        return input_spec["object"]
    else:
        raise ValueError("input_spec must contain 'id', 'json', or 'object'")


def _write_script(code: str, output_path: str) -> None:
    """Write generated code to file."""
    with open(output_path, "w") as f:
        f.write(code)


def _assemble_code(imports: list[str], lines: list[str]) -> str:
    """Assemble final code from components."""
    from kumoai import __version__

    header = [
        f"# Generated with Kumo SDK version: {__version__}",
        "import kumoai as kumo",
        "import os",
        "",
        'kumo.init(url=os.getenv("KUMO_API_ENDPOINT"), '
        'api_key=os.getenv("KUMO_API_KEY"))',
        "",
    ]

    unique_imports = list(OrderedDict.fromkeys(imports))
    code = header + unique_imports + [""] + lines
    return "\n".join(code) + "\n"


def _init_kumo() -> None:
    """Initialize Kumo SDK for this python session."""
    import kumoai as kumo
    if os.getenv("KUMO_API_ENDPOINT") is None:
        logger.warning("KUMO_API_ENDPOINT env variable is not set, "
                       "assuming kumo.init has already been called")
        return
    if os.getenv("KUMO_API_KEY") is None:
        logger.warning("KUMO_API_KEY env variable is not set, "
                       "assuming kumo.init has already been called")
        return
    kumo.init(url=os.getenv("KUMO_API_ENDPOINT"),
              api_key=os.getenv("KUMO_API_KEY"))


def generate_code(input_spec: dict[str, Any],
                  output_path: Optional[str] = None) -> str:
    """Generate Python SDK code from Kumo entity specification."""
    _init_kumo()
    entity = _load_entity_from_spec(input_spec)

    context = {}
    if "id" in input_spec:
        context["input_method"] = "id"
        context["target_id"] = input_spec["id"]
    elif "json" in input_spec:
        context["input_method"] = "json"
    else:
        context["input_method"] = "object"

    name_manager = NameManager()
    imports, lines = _generate(entity, name_manager, seen={}, stack=set(),
                               context=context)

    code = _assemble_code(imports, lines)
    if output_path:
        _write_script(code, output_path)
    return code
