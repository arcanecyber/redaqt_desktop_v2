import yaml
from pathlib import Path

DEFAULT_SETTINGS = {
  "default_settings": {
    "add_certificate": False,
    "appearance": "dark",
    "mfa": {
      "methods": {
        "bio": False,
        "hardware_key": False,
        "pin": False,
        "totp": False
      },
      "mfa_active": False
    },
    "request_receipt": {
      "on_delivery": False,
      "on_request": False
    },
    "smart_policy": {
      "methods": {
        "lock_to_user": False,
        "no_open_after": False,
        "no_open_before": False,
        "no_policy": True,
        "passphrase": False
      }
    }
  }
}

def reset_default_yaml(config_path: Path = Path("config/default.yaml")):
    """Reset the default.yaml file to the original factory settings."""
    try:
        with config_path.open("w") as f:
            yaml.dump(DEFAULT_SETTINGS, f, sort_keys=False, indent=2)
        print(f"[INFO] Reset config written to {config_path}.")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to reset config: {e}")
        return False