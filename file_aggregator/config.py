import json
import os

DEFAULT_CONFIG_DIR = ".file-aggregator"
DEFAULT_CONFIG_FILE = os.path.join(DEFAULT_CONFIG_DIR, "aggregator.json")
GLOBAL_SETTINGS_FILE = os.path.expanduser("~/.fag_settings.json")

def get_config_path():
    """Returns the effective configuration path."""
    if os.path.exists(GLOBAL_SETTINGS_FILE):
        with open(GLOBAL_SETTINGS_FILE, 'r', encoding='utf-8') as f:
            try:
                settings = json.load(f)
                return settings.get("config_path", DEFAULT_CONFIG_FILE)
            except (json.JSONDecodeError, KeyError):
                pass
    return DEFAULT_CONFIG_FILE

def set_global_config_path(new_path):
    """Sets a persistent global configuration path."""
    settings = {}
    if os.path.exists(GLOBAL_SETTINGS_FILE):
        with open(GLOBAL_SETTINGS_FILE, 'r', encoding='utf-8') as f:
            try:
                settings = json.load(f)
            except json.JSONDecodeError:
                pass
    
    settings["config_path"] = os.path.abspath(new_path)
    with open(GLOBAL_SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2)
    return settings["config_path"]

def load_config(config_path=None):
    """Loads the registration file and migrates old format if necessary."""
    if config_path is None:
        config_path = get_config_path()

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
                save_config(config, config_path)
            return config
        except json.JSONDecodeError:
            return {}

def save_config(config, config_path=None):
    """Saves the configuration to the JSON file, creating directories if needed."""
    if config_path is None:
        config_path = get_config_path()
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    return config_path
