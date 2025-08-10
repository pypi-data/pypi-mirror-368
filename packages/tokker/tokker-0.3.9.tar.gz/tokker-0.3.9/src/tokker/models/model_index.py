#!/usr/bin/env python3
"""
Small helpers for building and serializing the model -> provider index.

Also contains lightweight dependency/version helpers used by cache validation.

Public helpers:
- build_model_index(provider_classes) -> dict[str, str]
- build_model_list(model_index) -> list[dict[str, str]]
- get_dependency_versions() -> dict[str, str | None]
"""

from importlib import metadata


def build_model_index(provider_classes: dict[str, type]) -> dict[str, str]:
    """
    Construct a mapping from model name -> provider display name.
    """
    out: dict[str, str] = {}
    if not provider_classes:
        return out

    for provider_name, cls in provider_classes.items():
        models = getattr(cls, "MODELS", []) or []
        for m in models:
            if isinstance(m, str):
                out[m] = provider_name
    return out


def build_model_list(model_index: dict[str, str]) -> list[dict[str, str]]:
    """
    Convert an index mapping into a serializable list of {"name":..., "provider":...}
    sorted by model name for stable output.
    """
    items: list[dict[str, str]] = []
    if not model_index:
        return items

    for name in sorted(model_index.keys()):
        provider = model_index.get(name, "")
        items.append({"name": name, "provider": provider})
    return items


# -----------------------
# Dependency / version helpers
# -----------------------


def get_dependency_versions() -> dict[str, str | None]:
    """
    Return distribution -> installed version (or None) for the known providers.
    """
    dists = ("tiktoken", "transformers", "google-genai")
    out: dict[str, str | None] = {}
    for dist in dists:
        try:
            out[dist] = metadata.version(dist)
        except Exception:
            out[dist] = None
    return out
