#!/usr/bin/env python3
from datetime import datetime
import json
from pathlib import Path
from typing import Any

Entry = dict[str, str | int]


class History:
    def __init__(
        self,
        config_dir: Path | None = None,
        history_file: Path | None = None,
        max_entries: int = 50,
    ) -> None:
        self.config_dir = config_dir or (Path.home() / ".config" / "tokker")
        self._history_file = history_file
        self.max_entries = int(max_entries)
        pass

    @property
    def path(self) -> Path:
        return self._history_file or (self.config_dir / "history.json")

    def load(self) -> list[Entry]:
        raw = _read_json(self.path)
        return _prepare_history(raw)

    def save(self, history: list[Entry]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        _write_json(self.path, history)
        pass

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()
            pass

    def add_model(self, model_name: str) -> None:
        history = self.load()

        prev_count = 0
        for entry in history:
            if entry.get("model") == model_name:
                prev_val = entry.get("count", 0)
                if isinstance(prev_val, (int, float)) and not isinstance(
                    prev_val, bool
                ):
                    prev_count = int(prev_val)
                elif isinstance(prev_val, str) and prev_val.isdigit():
                    prev_count = int(prev_val)
                else:
                    prev_count = 0
                break

        history = [entry for entry in history if entry.get("model") != model_name]

        new_entry: Entry = {
            "model": model_name,
            "timestamp": datetime.now().isoformat(),
            "count": (prev_count or 0) + 1,
        }

        history.insert(0, new_entry)
        history = history[: self.max_entries]

        self.save(history)
        pass


# --- internal helpers ---
def _read_json(path: Path) -> Any:
    if not path.exists():
        return []
    # Let JSON parsing and decoding errors propagate to the centralized error handler.
    # This avoids silently hiding corrupt config/history files and ensures the
    # top-level handler can present a clear message to the user.
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _write_json(path: Path, value: Any) -> None:
    with path.open("w", encoding="utf-8") as fh:
        json.dump(value, fh, indent=2, ensure_ascii=False)
    pass


def _prepare_history(raw: Any) -> list[Entry]:
    if not isinstance(raw, list):
        return []

    prepared_entries: list[Entry] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        if "model" not in item or "timestamp" not in item:
            continue

        model = str(item.get("model"))
        timestamp = str(item.get("timestamp"))
        count_val = item.get("count", 1)

        if isinstance(count_val, (int, float)) and not isinstance(count_val, bool):
            count = int(count_val)
        elif isinstance(count_val, str) and count_val.isdigit():
            count = int(count_val)
        else:
            count = 1

        prepared_entries.append(
            {"model": model, "timestamp": timestamp, "count": count}
        )

    return prepared_entries
