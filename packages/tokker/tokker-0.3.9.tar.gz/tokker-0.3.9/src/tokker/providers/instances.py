#!/usr/bin/env python3
"""
Provider instantiation helpers:
- instantiate_provider(provider_name: str, instances: dict[str, object]) -> object
- Uses `try_import_provider_module` (best-effort) to import provider module if needed.
- Raises Exception("Provider not found: ...") when provider class is unavailable.
"""

from tokker.providers import PROVIDERS, Provider
from tokker.providers.imports import load_provider


def instantiate_provider(
    provider_name: str, instances: dict[str, Provider]
) -> Provider:
    """
    Return a provider instance from `instances` cache or construct one.
    """
    # Return cached instance
    if provider_name in instances:
        return instances[provider_name]

    # Lookup registered provider class
    cls = PROVIDERS.get(provider_name)
    if not cls:
        # Try importing provider module to let it register itself
        load_provider(provider_name)
        cls = PROVIDERS.get(provider_name)

    if not cls:
        raise Exception(f"Provider not found: {provider_name}")

    # Construct and cache instance; let constructor exceptions bubble
    inst = cls()
    instances[provider_name] = inst
    return inst
    pass


__all__ = ["instantiate_provider"]
