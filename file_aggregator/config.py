import json
import os

CONFIG_FILE = "aggregator.json"

def load_config(config_path=CONFIG_FILE):
    """Loads the registration file and migrates old format if necessary."""
    if not os.path.exists(config_path):
        return {}
    with open(config_path, 'r', encoding='utf-8') as f:
        try:
            config = json.load(f)
            # Migration: convert old list format to dict format
            migrated = False
            for target, data in config.items():
                if isinstance(data, list):
                    config[target] = {"sources": data, "enabled": True}
                    migrated = True
            if migrated:
                # We save it back to ensure consistency
                save_config(config, config_path)
            return config
        except json.JSONDecodeError:
            return {}

def save_config(config, config_path=CONFIG_FILE):
    """Saves the configuration to the JSON file."""
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
