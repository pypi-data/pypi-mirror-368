#!/usr/bin/env python3
"""
Cache IO for model discovery.

Responsibilities:
- Provide a default cache path.
- Read and validate discovery cache, returning (model->provider mapping, provider names).
- Write cache from provider names and model index.

This module does not perform provider imports; import-side effects live in
`tokker.providers.imports` and should be imported directly by callers. Version
helpers are provided by `tokker.utils.get_version`.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from tokker.models.model_index import get_dependency_versions
from tokker.utils import get_version


# Default cache file (renamed as requested)
CACHE_DEFAULT_PATH: Path = (
    Path.home() / ".config" / "tokker" / "discovered_models_cache.json"
)


def load_models_from_cache(cache_path: Path) -> tuple[dict[str, str], list[str]] | None:
    """
    Read cache at `cache_path` and return a validated model->provider dict.
    """
    try:
        if not cache_path.exists():
            return None
        with cache_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            return None

        cache_deps = data.get("deps", {})
        if not isinstance(cache_deps, dict):
            return None

        if cache_deps != get_dependency_versions():
            return None

        if data.get("tokker_version") != get_version():
            return None

        models = data.get("models", [])
        if not isinstance(models, list):
            return None
        providers = data.get("providers", [])
        if not isinstance(providers, list):
            return None

        out: dict[str, str] = {}
        for item in models:
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            provider = item.get("provider")
            if isinstance(name, str) and isinstance(provider, str):
                out[name] = provider

        provider_names: list[str] = []
        for p in providers:
            if isinstance(p, str):
                provider_names.append(p)

        return out, provider_names
    except Exception:
        return None


def write_cache(
    cache_path: Path, provider_names: list[str], model_index: dict[str, str]
) -> None:
    """
    Write a discovery cache derived from `provider_names` and `model_index`.
    """
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = {
            "tokker_version": get_version(),
            "deps": get_dependency_versions(),
            "providers": sorted(provider_names),
            "models": [
                {"name": n, "provider": model_index[n]}
                for n in sorted(model_index.keys())
            ],
            "ts": datetime.utcnow().isoformat() + "Z",
        }
        with cache_path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
    except Exception:
        return


__all__ = [
    "CACHE_DEFAULT_PATH",
    "load_models_from_cache",
    "write_cache",
]
