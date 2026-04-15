import time
import sys
from .config import load_config, save_config, CONFIG_FILE
from .utils import get_file_states, concatenate_file

def register_target(target, sources, config_path=CONFIG_FILE):
    """Registers a new target and its sources."""
    config = load_config(config_path)
    config[target] = sources
    save_config(config, config_path)
    print(f"Registered '{target}' with {len(sources)} source(s) in {config_path}.")

def start_watcher(poll_interval=2, config_path=CONFIG_FILE):
    """Polls all registered files in the JSON config."""
    print(f"Starting watcher using {config_path}... (Press Ctrl+C to exit)")
    
    last_states = {}

    try:
        while True:
            # Hot-reload config
            config = load_config(config_path)
            
            for target, sources in config.items():
                current_states = get_file_states(sources)
                
                # If newly registered or if any source file's state changed
                if target not in last_states or current_states != last_states[target]:
                    concatenate_file(target, sources)
                    last_states[target] = current_states
            
            # Clean up states for targets that were removed from the JSON
            for old_target in list(last_states.keys()):
                if old_target not in config:
                    del last_states[old_target]

            time.sleep(poll_interval)
            
    except KeyboardInterrupt:
        print("\nAggregator stopped.")
        sys.exit(0)
