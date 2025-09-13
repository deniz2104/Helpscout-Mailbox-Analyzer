import json
import os

def load_config() -> dict:
    """Load configuration from config.json file."""
    config_file  = "config.json"

    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file {config_file} not found")
    
    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)

def get_helpscout_credentials() -> tuple[str, str]:
    """Retrieve Helpscout API credentials from config."""
    config = load_config()
    client_id : str = config.get("HELPSCOUT_CLIENT_ID")
    client_secret : str = config.get("HELPSCOUT_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError("HELPSCOUT_CLIENT_ID and HELPSCOUT_CLIENT_SECRET must be set in config.json")
    
    return client_id, client_secret
