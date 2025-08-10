#!/usr/bin/env python3
"""
Provider import helpers for the providers package.

Responsibilities:
- Map provider display names to their provider module import paths.
- Provide best-effort import helpers:
    - `load_providers()` imports all known provider modules (no-raise).
    - `load_provider(name)` imports a single provider module by provider display name (no-raise).

Design constraints:
- Import-time cheap: this module must not import heavy optional dependencies.
- Use `__import__` on module path strings and swallow ImportError/Exception.
- No legacy aliases; keep a small, clear API.
"""

# Mapping: provider display name -> provider module path
PROVIDER_MODULE_MAP: dict[str, str] = {
    "OpenAI": "tokker.providers.tiktoken",
    "HuggingFace": "tokker.providers.huggingface",
    "Google": "tokker.providers.google",
}


def load_providers() -> None:
    """
    Best-effort import of all known provider modules so their registration
    decorators can run.

    Import errors are swallowed to keep discovery non-fatal and import-time cheap.
    This implementation delegates to `load_provider()` to avoid duplicating the
    import logic in two places.
    """
    for provider_name in PROVIDER_MODULE_MAP.keys():
        try:
            load_provider(provider_name)
        except Exception:
            # load_provider already swallows errors; be defensive here.
            pass
    return None


def load_provider(provider_name: str) -> None:
    """
    Best-effort import of a single provider module by provider display name.

    If `provider_name` is unknown or the import fails, this function returns None
    and does not raise; callers should handle the absence of a provider class.
    """
    module_path = PROVIDER_MODULE_MAP.get(provider_name)
    if not module_path:
        return None
    try:
        __import__(module_path)
    except Exception:
        # Swallow errors: higher-level code will raise if a provider class is required.
        pass
    return None


__all__ = ["PROVIDER_MODULE_MAP", "load_providers", "load_provider"]
