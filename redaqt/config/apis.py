# redaqt/config/apis.py

import yaml
from pathlib import Path

API_FILE = Path(__file__).parent / "apis.yaml"

class ApiConfig:
    _cfg = None

    @classmethod
    def _load(cls) -> dict:
        if cls._cfg is None:
            if not API_FILE.exists():
                cls._cfg = {}
            else:
                text = API_FILE.read_text(encoding="utf-8")
                cls._cfg = yaml.safe_load(text) or {}
        return cls._cfg

    @classmethod
    def get(cls, *keys, default=None):
        """
        Lookup a nested key path in the loaded API config.
        e.g. ApiConfig.get("users", "login", default="")
        """
        data = cls._load()
        for key in keys:
            if not isinstance(data, dict) or key not in data:
                return default
            data = data[key]
        return data