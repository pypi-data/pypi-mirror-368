"""
Utilities for loading YAML config files and resolving control_arena objects.

This module provides:
- load_yaml_config: Read a YAML file to a Python dict
- ConfigResolver: Resolve vars, settings, components, and inline specs to live objects
- import_custom_module: Optional hook to import a user module and let it register extras
"""

from __future__ import annotations

import importlib.util
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

import yaml

from control_runner.registry import resolve_type


_REFERENCE_PATTERN = re.compile(r"^\$\{([^}]+)\}$")


def load_yaml_config(yaml_path: str) -> dict[str, Any]:
    """Load a YAML file into a Python dictionary.

    Args:
        yaml_path: Path to the YAML configuration file.

    Returns:
        Parsed configuration as a dict.
    """
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("Top-level YAML must be a mapping (dict).")
    return data


def _is_pathlike_string(value: str) -> bool:
    if not isinstance(value, str) or not value:
        return False
    if value.startswith("./") or value.startswith("../") or value.startswith("/"):
        # Heuristic: has a file extension and no newline
        return "." in os.path.basename(value) and "\n" not in value
    return False


def _read_text_file_with_fallbacks(
    path_str: str, base_dirs: list[str]
) -> Optional[str]:
    """Try to read a file relative to any of the provided base dirs or absolute path.

    Returns file content if resolved, else None.
    """
    candidate_paths: list[Path] = []
    path_obj = Path(path_str)
    if path_obj.is_absolute():
        candidate_paths.append(path_obj)
    else:
        for base in base_dirs:
            candidate_paths.append(Path(base) / path_obj)

    for candidate in candidate_paths:
        if candidate.exists() and candidate.is_file():
            return candidate.read_text(encoding="utf-8")
    return None


def import_custom_module(custom_py: str, resolver: "ConfigResolver") -> None:
    """Import a custom python module file, optionally letting it register extras.

    If the module defines a top-level function named `register`, it will be called
    with the resolver instance to allow the module to extend resolution behavior.
    """
    module_path = Path(custom_py)
    if not module_path.exists():
        raise FileNotFoundError(f"Custom module not found: {custom_py}")

    spec = importlib.util.spec_from_file_location(module_path.stem, str(module_path))
    if spec is None or spec.loader is None:  # type: ignore[truthy-bool]
        raise ImportError(f"Unable to load spec for module: {custom_py}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]

    register_fn: Optional[Callable[["ConfigResolver"], None]] = getattr(
        module, "register", None
    )
    if callable(register_fn):
        register_fn(resolver)


@dataclass
class _Context:
    base_dirs: list[str]


class ConfigResolver:
    """Resolve a control_arena configuration into live objects.

    Responsibilities:
    - Prepare variables (including file content expansion)
    - Lazily build settings and components
    - Resolve inline specs and reference expressions in params
    """

    def __init__(
        self,
        raw_config: dict[str, Any],
        building_blocks: Optional[dict[str, dict[str, Any]]] = None,
        base_dir: Optional[str] = None,
    ) -> None:
        self.raw_config = raw_config
        # building_blocks is accepted for API compatibility but not needed; we use resolve_type
        self._building_blocks = building_blocks or {}
        # Base dirs for relative file resolution: prefer CWD, then YAML dir if provided
        cwd = os.getcwd()
        base_candidates: list[str] = [cwd]
        if base_dir:
            base_candidates.append(base_dir)
        self.ctx = _Context(base_dirs=base_candidates)

        self.vars: dict[str, Any] = {}
        self._prepare_vars()

        self._settings_defs: dict[str, Any] = dict(self.raw_config.get("settings", {}))
        self._components_defs: dict[str, Any] = dict(
            self.raw_config.get("components", {})
        )
        self._resolved_settings: dict[str, Any] = {}
        self._resolved_components: dict[str, Any] = {}

    # ------------------------------ Public API ------------------------------
    def resolve_component(self, spec: Any) -> Any:
        """Resolve a component or reference to a live object.

        Accepts:
        - "${name}" references to settings/components/vars
        - Inline specs: {type: name, params: {...}}
        - Already-built objects (returned as-is)
        """
        return self._resolve_value(spec)

    def resolve_protocol(self, spec: Any) -> Any:
        """Alias for resolve_component; kept for readability."""
        return self._resolve_value(spec)

    # ---------------------------- Internal helpers --------------------------
    def _prepare_vars(self) -> None:
        raw_vars: dict[str, Any] = dict(self.raw_config.get("vars", {}))
        prepared: dict[str, Any] = {}
        for key, value in raw_vars.items():
            if isinstance(value, str) and _is_pathlike_string(value):
                content = _read_text_file_with_fallbacks(value, self.ctx.base_dirs)
                prepared[key] = content if content is not None else value
            else:
                prepared[key] = value
        self.vars = prepared

    def _apply_string_substitutions(self, value: str) -> str:
        # Replace ${var} occurrences with string versions of vars when embedded
        def _replace(m: re.Match[str]) -> str:
            name = m.group(1)
            replacement = self._get_reference_value(name)
            if isinstance(replacement, (str, int, float)):
                return str(replacement)
            # If the replacement is not a primitive, keep the original text
            return m.group(0)

        return re.sub(r"\$\{([^}]+)\}", _replace, value)

    def _resolve_value(self, value: Any) -> Any:
        # Reference string like ${name}
        if isinstance(value, str):
            ref_match = _REFERENCE_PATTERN.match(value)
            if ref_match:
                name = ref_match.group(1)
                return self._get_reference_value(name)

            # Bare-string resolution: if it exactly matches a known ref, return it
            if (
                value in self.vars
                or value in self._settings_defs
                or value in self._components_defs
                or value in self._resolved_settings
                or value in self._resolved_components
            ):
                try:
                    return self._get_reference_value(value)
                except KeyError:
                    pass

            # If it matches a known type in the registry, call it with no params
            try:
                target = resolve_type(value)
                if callable(target):
                    return target()
            except Exception:
                # Not a known registry type or not callable with no args
                pass

            # Else perform embedded substitutions for primitive vars
            return self._apply_string_substitutions(value)

        # Inline spec
        if isinstance(value, dict) and ("type" in value or "import" in value):
            return self._build_inline_spec(value)

        # Lists
        if isinstance(value, list):
            return [self._resolve_value(v) for v in value]

        # Pass-through
        return value

    def _get_reference_value(self, name: str) -> Any:
        # Vars first
        if name in self.vars:
            return self.vars[name]
        # Settings
        if name in self._resolved_settings:
            return self._resolved_settings[name]
        if name in self._settings_defs:
            self._resolved_settings[name] = self._build_inline_spec(
                self._settings_defs[name]
            )
            return self._resolved_settings[name]
        # Components
        if name in self._resolved_components:
            return self._resolved_components[name]
        if name in self._components_defs:
            self._resolved_components[name] = self._build_inline_spec(
                self._components_defs[name]
            )
            return self._resolved_components[name]
        raise KeyError(f"Unknown reference: '{name}'")

    def _build_inline_spec(self, spec: dict[str, Any]) -> Any:
        if "type" in spec:
            type_name = spec["type"]
            params = spec.get("params", {})
            if not isinstance(params, dict):
                raise TypeError("'params' must be a dict when provided")
            resolved_params = {k: self._resolve_value(v) for k, v in params.items()}
            target = resolve_type(type_name)
            return self._call_target(target, resolved_params)

        # Optional support: direct dotted imports via {'import': 'module:Name', 'params': {...}}
        if "import" in spec:
            import_str = spec["import"]
            params = spec.get("params", {})
            if not isinstance(params, dict):
                raise TypeError("'params' must be a dict when provided")
            resolved_params = {k: self._resolve_value(v) for k, v in params.items()}
            module_path, obj_name = import_str.rsplit(":", 1)
            module = __import__(module_path, fromlist=[obj_name])
            target = getattr(module, obj_name)
            return self._call_target(target, resolved_params)

        raise ValueError("Inline spec must include 'type' or 'import'")

    def _call_target(self, target: Any, params: dict[str, Any]) -> Any:
        if callable(target):
            return target(**params)
        # Target is a class-like object not callable? Attempt attribute-based construction not supported
        raise TypeError(f"Target '{target}' is not callable and cannot be instantiated")
