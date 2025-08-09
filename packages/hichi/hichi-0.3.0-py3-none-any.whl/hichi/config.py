import os
import json

CONFIG_DIR = os.path.expanduser("~/.hichi")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
DEFAULT_MODEL = "openai/gpt-oss-120b"

def ensure_config_dir_exists():
    """Ensures that the configuration directory exists."""
    os.makedirs(CONFIG_DIR, exist_ok=True)

def get_config():
    """Reads the configuration from the config file."""
    ensure_config_dir_exists()
    if not os.path.exists(CONFIG_FILE):
        return {"api_key": None, "model": DEFAULT_MODEL}
    
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        
        # Ensure model is set to default if not present or if it's the old model
        if "model" not in config or config.get("model") == "Qwen3 480b Coder":
            config["model"] = DEFAULT_MODEL
            save_config(config)
        
        return config
    except (json.JSONDecodeError, FileNotFoundError):
        return {"api_key": None, "model": DEFAULT_MODEL}

def save_config(config):
    """Saves the configuration to the config file."""
    ensure_config_dir_exists()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)