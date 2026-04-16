import os
import time
import sys
from .config import load_config, save_config, get_config_path
from .utils import get_file_states, concatenate_file

def register_target(target, sources, config_path=None):
    """Registers a new target and its sources."""
    # Check if all sources exist
    missing_sources = [src for src in sources if not os.path.exists(src)]
    if missing_sources:
        print(f"Error: The following source files do not exist: {', '.join(missing_sources)}")
        print("Aggregation aborted. No target registered.")
        return

    config = load_config(config_path)
    config[target] = {"sources": sources, "enabled": True}
    actual_path = save_config(config, config_path)
    print(f"Registered '{target}' with {len(sources)} source(s) in {actual_path}.")

def remove_target(target, config_path=None):
    """Removes a registered target."""
    config = load_config(config_path)
    if target in config:
        del config[target]
        save_config(config, config_path)
        print(f"Removed target '{target}'.")
    else:
        print(f"Error: Target '{target}' not found.")

def toggle_target(target, enabled=True, config_path=None):
    """Enables or disables a registered target."""
    config = load_config(config_path)
    if target in config:
        config[target]["enabled"] = enabled
        save_config(config, config_path)
        status = "enabled" if enabled else "disabled"
        print(f"Target '{target}' is now {status}.")
    else:
        print(f"Error: Target '{target}' not found.")

def list_targets(only_enabled=False, config_path=None):
    """Lists all registered targets."""
    config = load_config(config_path)
    if not config:
        print("No targets registered.")
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

def start_watcher(poll_interval=2, config_path=None):
    """Polls all registered files in the JSON config."""
    actual_path = config_path if config_path else get_config_path()
    print(f"Starting watcher using {actual_path}... (Press Ctrl+C to exit)")
    
    last_states = {}

    try:
        while True:
            # Hot-reload config
            config = load_config(config_path)
            
            for target, data in config.items():
                if not data.get("enabled", True):
                    continue

                sources = data.get("sources", [])
                current_states = get_file_states(sources)
                
                # If newly registered or if any source file's state changed
                if target not in last_states or current_states != last_states[target]:
                    # concatenate_file now handles the case where sources might be missing temporarily
                    if concatenate_file(target, sources):
                        last_states[target] = current_states
            
            # Clean up states for targets that were removed from the JSON
            for old_target in list(last_states.keys()):
                if old_target not in config:
                    del last_states[old_target]

            time.sleep(poll_interval)
            
    except KeyboardInterrupt:
        print("\nAggregator stopped.")
        sys.exit(0)
