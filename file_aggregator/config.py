from __future__ import annotations

import json
import os
from typing import Any, Dict, Iterable, List, Optional, Tuple

DEFAULT_CONFIG_DIR = ".file-aggregator"
DEFAULT_CONFIG_FILE = os.path.join(DEFAULT_CONFIG_DIR, "aggregator.json")
GLOBAL_SETTINGS_FILE = os.path.expanduser("~/.fag_settings.json")
PROJECTS_KEY = "projects"


def _read_global_settings() -> Dict[str, Any]:
    if not os.path.exists(GLOBAL_SETTINGS_FILE):
        return {}
    with open(GLOBAL_SETTINGS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _write_global_settings(settings: Dict[str, Any]) -> None:
    parent = os.path.dirname(GLOBAL_SETTINGS_FILE)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(GLOBAL_SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def get_config_path() -> str:
    """Returns the effective configuration path (legacy single-file default)."""
    settings = _read_global_settings()
    return settings.get("config_path", DEFAULT_CONFIG_FILE)


def get_project_config_paths(project_name: str) -> Optional[List[str]]:
    """
    Returns absolute paths for a named project, or None if the project is unknown.
    """
    settings = _read_global_settings()
    projects = settings.get(PROJECTS_KEY) or {}
    paths = projects.get(project_name)
    if not paths:
        return None
    return [os.path.abspath(p) for p in paths]


def resolve_config_paths(project_name: Optional[str] = None) -> List[str]:
    """
    Returns a non-empty list of absolute config paths to use.
    If project_name is set, uses that project's path list from global settings.
    Otherwise uses the legacy single global config_path.
    """
    if project_name:
        paths = get_project_config_paths(project_name)
        if paths is None:
            raise ValueError(
                f"Unknown project {project_name!r}. "
                f"Define it with: fag configure project {project_name} <path> [<path> ...]"
            )
        if not paths:
            raise ValueError(f"Project {project_name!r} has no config paths configured.")
        return paths
    return [os.path.abspath(get_config_path())]


def set_global_config_path(new_path: str) -> str:
    """Sets a persistent global configuration path."""
    settings = _read_global_settings()
    settings["config_path"] = os.path.abspath(new_path)
    _write_global_settings(settings)
    return settings["config_path"]


def set_project_config_paths(project_name: str, paths: Iterable[str]) -> List[str]:
    """Sets one or more aggregator JSON paths for a named project (overwrites)."""
    settings = _read_global_settings()
    projects = dict(settings.get(PROJECTS_KEY) or {})
    norm = [os.path.abspath(p) for p in paths]
    if not norm:
        raise ValueError("At least one config path is required.")
    projects[project_name] = norm
    settings[PROJECTS_KEY] = projects
    _write_global_settings(settings)
    return norm


def list_projects_config() -> Tuple[str, Dict[str, List[str]]]:
    """Returns (default_config_path, dict project_name -> list of paths)."""
    settings = _read_global_settings()
    default_path = settings.get("config_path", DEFAULT_CONFIG_FILE)
    projects = {
        name: [os.path.abspath(p) for p in paths]
        for name, paths in (settings.get(PROJECTS_KEY) or {}).items()
        if paths
    }
    return os.path.abspath(default_path), projects


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Loads a single registration file and migrates old format if necessary."""
    if config_path is None:
        config_path = get_config_path()

    if not os.path.exists(config_path):
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        try:
            config = json.load(f)
            migrated = False
            for target, data in config.items():
                if isinstance(data, list):
                    config[target] = {"sources": data, "enabled": True}
                    migrated = True
            if migrated:
                save_config(config, config_path)
            return config
        except json.JSONDecodeError:
            return {}


def load_config_slices(config_paths: Iterable[str]) -> List[Tuple[str, Dict[str, Any]]]:
    """Loads each path as its own dict; missing files yield empty dicts."""
    return [(os.path.abspath(p), load_config(p)) for p in config_paths]


def merge_config_slices(slices: Iterable[Tuple[str, Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Merges per-file configs into one mapping. Later files override duplicate target keys.
    """
    merged: Dict[str, Any] = {}
    for _, cfg in slices:
        merged.update(cfg)
    return merged


def find_slice_path_for_target(
    slices: Iterable[Tuple[str, Dict[str, Any]]], target: str
) -> Optional[str]:
    """Returns the config file path that defines target, or None."""
    for path, cfg in slices:
        if target in cfg:
            return path
    return None


def save_config(config: Dict[str, Any], config_path: Optional[str] = None) -> str:
    """Saves the configuration to the JSON file, creating directories if needed."""
    if config_path is None:
        config_path = get_config_path()

    os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    return config_path
