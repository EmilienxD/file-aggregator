from __future__ import annotations

import os
import sys
import time
from typing import Iterable, List, Optional, Sequence

from .utils import get_file_states, concatenate_file
from .config import (
    load_config,
    save_config,
    resolve_config_paths,
    load_config_slices,
    merge_config_slices,
    find_slice_path_for_target,
)


def _effective_paths(
    project_name: Optional[str] = None,
    config_paths: Optional[Iterable[str]] = None,
) -> List[str]:
    if config_paths is not None:
        return [os.path.abspath(p) for p in config_paths]
    return resolve_config_paths(project_name)


def register_target(
    target: str,
    sources: Sequence[str],
    project_name: Optional[str] = None,
    config_paths: Optional[Iterable[str]] = None,
    into_path: Optional[str] = None,
) -> None:
    """Registers a new target and its sources."""
    missing_sources = [src for src in sources if not os.path.exists(src)]
    if missing_sources:
        print(f"Error: The following source files do not exist: {', '.join(missing_sources)}")
        print("Aggregation aborted. No target registered.")
        return

    paths = _effective_paths(project_name, config_paths)
    if into_path:
        into_path = os.path.abspath(into_path)
        if into_path not in paths:
            print(f"Error: --into path must be one of this project's config files: {paths}")
            return

    slices = load_config_slices(paths)
    existing_file = find_slice_path_for_target(slices, target)

    if existing_file:
        cfg = load_config(existing_file)
        cfg[target] = {"sources": sources, "enabled": True}
        save_path = save_config(cfg, existing_file)
        print(f"Registered '{target}' with {len(sources)} source(s) in {save_path}.")
        return

    dest = into_path or paths[0]
    cfg = load_config(dest)
    cfg[target] = {"sources": sources, "enabled": True}
    save_path = save_config(cfg, dest)
    print(f"Registered '{target}' with {len(sources)} source(s) in {save_path}.")


def remove_target(
    target: str,
    project_name: Optional[str] = None,
    config_paths: Optional[Iterable[str]] = None,
) -> None:
    """Removes a registered target from whichever config file defines it."""
    paths = _effective_paths(project_name, config_paths)
    slices = load_config_slices(paths)
    path = find_slice_path_for_target(slices, target)
    if path is None:
        print(f"Error: Target '{target}' not found.")
        return
    cfg = load_config(path)
    del cfg[target]
    save_config(cfg, path)
    print(f"Removed target '{target}'.")


def toggle_target(
    target: str,
    enabled: bool = True,
    project_name: Optional[str] = None,
    config_paths: Optional[Iterable[str]] = None,
) -> None:
    """Enables or disables a registered target."""
    paths = _effective_paths(project_name, config_paths)
    slices = load_config_slices(paths)
    path = find_slice_path_for_target(slices, target)
    if path is None:
        print(f"Error: Target '{target}' not found.")
        return
    cfg = load_config(path)
    cfg[target]["enabled"] = enabled
    save_config(cfg, path)
    status = "enabled" if enabled else "disabled"
    print(f"Target '{target}' is now {status}.")


def list_targets(
    only_enabled: bool = False,
    project_name: Optional[str] = None,
    config_paths: Optional[Iterable[str]] = None,
    show_config_file: bool = False,
) -> None:
    """Lists all registered targets (merged view when multiple config files are used)."""
    paths = _effective_paths(project_name, config_paths)
    slices = load_config_slices(paths)
    config = merge_config_slices(slices)
    if not config:
        print("No targets registered.")
        return

    target_to_path = {}
    if show_config_file or len(paths) > 1:
        for path, cfg in slices:
            for t in cfg:
                if t not in target_to_path:
                    target_to_path[t] = path

    if show_config_file or len(paths) > 1:
        print(f"{'Target':<40} | {'Config file':<48} | {'Status':<10} | {'Sources'}")
        print("-" * 130)
        for target, data in config.items():
            enabled = data.get("enabled", True)
            if only_enabled and not enabled:
                continue
            status = "Enabled" if enabled else "Disabled"
            sources = ", ".join(data.get("sources", []))
            src_path = target_to_path.get(target, "")
            cfg_disp = src_path if len(src_path) <= 48 else "..." + src_path[-45:]
            print(f"{target:<40} | {cfg_disp:<48} | {status:<10} | {sources}")
        return

    print(f"{'Target':<40} | {'Status':<10} | {'Sources'}")
    print("-" * 80)
    for target, data in config.items():
        enabled = data.get("enabled", True)
        if only_enabled and not enabled:
            continue
        status = "Enabled" if enabled else "Disabled"
        sources = ", ".join(data.get("sources", []))
        print(f"{target:<40} | {status:<10} | {sources}")


def start_watcher(
    poll_interval: float = 2,
    project_name: Optional[str] = None,
    config_paths: Optional[Iterable[str]] = None,
) -> None:
    """Polls all registered files across one or more JSON configs."""
    paths = _effective_paths(project_name, config_paths)
    print(f"Starting watcher using {len(paths)} config file(s)... (Press Ctrl+C to exit)")
    for p in paths:
        print(f"  - {p}")

    last_states = {}

    try:
        while True:
            slices = load_config_slices(paths)
            config = merge_config_slices(slices)

            for target, data in config.items():
                if not data.get("enabled", True):
                    continue

                sources = data.get("sources", [])
                current_states = get_file_states(sources)

                if target not in last_states or current_states != last_states[target]:
                    if concatenate_file(target, sources):
                        last_states[target] = current_states

            for old_target in list(last_states.keys()):
                if old_target not in config:
                    del last_states[old_target]

            time.sleep(poll_interval)

    except KeyboardInterrupt:
        print("\nAggregator stopped.")
        sys.exit(0)
