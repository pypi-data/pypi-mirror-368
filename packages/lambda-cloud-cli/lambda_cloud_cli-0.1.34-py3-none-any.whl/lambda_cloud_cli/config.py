import os
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".lambda-cli"
CONFIG_PATH = CONFIG_DIR / "config.json"

def save_api_key(api_key: str):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump({"api_key": api_key}, f)
    os.chmod(CONFIG_PATH, 0o600)

def load_api_key():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f).get("api_key")
    return None

def delete_api_key():
    if CONFIG_PATH.exists():
        CONFIG_PATH.unlink()
        return True
    return False

