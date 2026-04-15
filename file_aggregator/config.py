import json
import os

CONFIG_FILE = "aggregator.json"

def load_config(config_path=CONFIG_FILE):
    """Loads the registration file."""
    if not os.path.exists(config_path):
        return {}
    with open(config_path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_config(config, config_path=CONFIG_FILE):
    """Saves the configuration to the JSON file."""
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
