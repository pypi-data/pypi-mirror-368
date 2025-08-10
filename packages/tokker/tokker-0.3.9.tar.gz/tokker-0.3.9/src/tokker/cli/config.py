#!/usr/bin/env python3
import json
from pathlib import Path

from tokker import messages

DEFAULT_CONFIG: dict[str, str] = {
    "default_model": "o200k_base",
    "default_output": messages.OutputFormat.COLOR.value,
    "delimiter": "⎮",
}


class Config:
    def __init__(self):
        """Initialize configuration manager."""
        self.config_dir = Path.home() / ".config" / "tokker"
        self.config_file = self.config_dir / "config.json"
        self._config: dict[str, str] | None = None
        pass

    def _ensure_config_dir(self) -> None:
        # Let PermissionError bubble if cannot create
        self.config_dir.mkdir(parents=True, exist_ok=True)
        pass

    def load(self) -> dict[str, str]:
        if self._config is not None:
            return self._config

        self._ensure_config_dir()

        if not self.config_file.exists():
            self.save(DEFAULT_CONFIG)
            self._config = DEFAULT_CONFIG.copy()
        else:
            with open(self.config_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if not isinstance(loaded, dict):
                    raise ValueError("Invalid configuration format")
                self._config = {str(k): str(v) for k, v in loaded.items()}

        for k, v in DEFAULT_CONFIG.items():
            self._config.setdefault(k, v)

        return self._config

    def save(self, config: dict[str, str]) -> None:
        self._ensure_config_dir()
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        self._config = config
        pass

    def get_default_model(self) -> str:
        config = self.load()
        return config.get("default_model", DEFAULT_CONFIG["default_model"])

    def set_default_model(self, model: str) -> None:
        config = self.load()
        config["default_model"] = model
        self.save(config)
        pass

    def get_default_output(self) -> str:
        """
        Return the configured default output format.
        Falls back to the system default defined in DEFAULT_CONFIG.
        """
        config = self.load()
        return config.get("default_output", DEFAULT_CONFIG["default_output"])

    def set_default_output(self, output: str) -> None:
        """
        Validate and persist a new default output format.
        """
        allowed = messages.OutputFormat.values()
        if output not in allowed:
            raise ValueError(f"Unknown output format: {output}")
        config = self.load()
        config["default_output"] = output
        self.save(config)
        pass

    def get_delimiter(self) -> str:
        config = self.load()
        return config.get("delimiter", DEFAULT_CONFIG["delimiter"])


# Global configuration instance
config = Config()
