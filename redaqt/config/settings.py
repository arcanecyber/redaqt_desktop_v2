# redaqt/config/settings.py

import yaml
from pathlib import Path
from typing import Any, Dict, Optional

from redaqt.models.defaults import DefaultSettings

class SettingsManager:
    """
    Manages two separate YAML files:
      - default_path (config/default.yaml) → holds user‐editable default settings
      - config_path  (config/config.yaml)  → holds other static config
    """

    def __init__(
        self,
        default_path: Path = Path("config/default.yaml"),
        config_path:  Path = Path("config/config.yaml")
    ):
        self.default_path = default_path
        self.config_path  = config_path

        self._defaults: Dict[str, Any] = {}
        self._config:   Dict[str, Any] = {}

        self.load_all()

    def load_all(self) -> None:
        """Load both YAML files into memory."""
        self._defaults = self._load_file(self.default_path)
        self._config   = self._load_file(self.config_path)

    def _load_file(self, path: Path) -> Dict[str, Any]:
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                return data if isinstance(data, dict) else {}
        except FileNotFoundError:
            return {}
        except yaml.YAMLError as e:
            raise RuntimeError(f"Failed to parse {path}: {e}")

    # --- default.yaml API ---
    def get_default(self, *keys: str, default: Optional[Any] = None) -> Any:
        node = self._defaults
        for k in keys:
            if not isinstance(node, dict) or k not in node:
                return default
            node = node[k]
        return node

    def set_default(self, value: Any, *keys: str) -> None:
        node = self._defaults
        for k in keys[:-1]:
            node = node.setdefault(k, {})
        node[keys[-1]] = value

    def save_defaults(self) -> None:
        self._write_file(self.default_path, self._defaults)

    # --- config.yaml API ---
    def get_config(self, *keys: str, default: Optional[Any] = None) -> Any:
        node = self._config
        for k in keys:
            if not isinstance(node, dict) or k not in node:
                return default
            node = node[k]
        return node

    def set_config(self, value: Any, *keys: str) -> None:
        node = self._config
        for k in keys[:-1]:
            node = node.setdefault(k, {})
        node[keys[-1]] = value

    def save_config(self) -> None:
        self._write_file(self.config_path, self._config)

    def _write_file(self, path: Path, data: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            yaml.safe_dump(data, f)

    # --- utility & migration to Pydantic model ---
    def as_dict_defaults(self) -> Dict[str, Any]:
        """Return a deep‐copied dict of default.yaml contents."""
        return yaml.safe_load(yaml.safe_dump(self._defaults))

    def as_dict_config(self) -> Dict[str, Any]:
        """Return a deep‐copied dict of config.yaml contents."""
        return yaml.safe_load(yaml.safe_dump(self._config))

    def get_validated_defaults(self) -> DefaultSettings:
        """
        Validate & return a DefaultSettings model built from default.yaml.
        Raises on schema errors.
        """
        raw = self.get_default("default_settings", default={})
        return DefaultSettings(**raw)