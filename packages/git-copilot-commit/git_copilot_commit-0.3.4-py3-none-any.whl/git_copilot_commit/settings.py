"""
Settings management using platformdirs for cross-platform directory paths.
"""

import json
from typing import Any

from platformdirs import (
    user_cache_dir,
    user_config_dir,
    user_data_dir,
    user_state_dir,
)


class Settings:
    """Manages application settings using platformdirs for cross-platform directory paths."""

    APP_NAME = "git-copilot-commit"

    def __init__(self):
        from pathlib import Path
        
        self.config_dir = Path(user_config_dir(f"com.kdheepak.{self.APP_NAME}"))
        self.data_dir = Path(user_data_dir(f"com.kdheepak.{self.APP_NAME}"))
        self.cache_dir = Path(user_cache_dir(f"com.kdheepak.{self.APP_NAME}"))
        self.state_dir = Path(user_state_dir(f"com.kdheepak.{self.APP_NAME}"))

        self.config_file = self.config_dir / "config.json"

        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self._config: dict[str, Any] = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from file."""
        if not self.config_file.exists():
            return {}

        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self._config, f, indent=2)
        except IOError:
            pass  # Silently fail if we can't write

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._config[key] = value
        self._save_config()

    def delete(self, key: str) -> None:
        """Delete a configuration value."""
        if key in self._config:
            del self._config[key]
            self._save_config()

    @property
    def default_model(self) -> str | None:
        """Get the default model."""
        return self.get("default_model")

    @default_model.setter
    def default_model(self, model: str) -> None:
        """Set the default model."""
        self.set("default_model", model)

    def clear_cache(self) -> None:
        """Clear the cache directory."""
        for file in self.cache_dir.glob("*"):
            if file.is_file():
                file.unlink()
            elif file.is_dir():
                import shutil

                shutil.rmtree(file)
