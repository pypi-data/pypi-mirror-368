"""
Provider registry public surface.

This package-level module intentionally keeps a minimal import-time footprint:
- It exposes the Provider ABC, the global PROVIDERS registry, and the
  @register_provider decorator used by provider implementations.
- It does NOT import provider modules or re-export loader helpers to keep
  startup fast and optional dependencies lazy.
- Import helpers live in `tokker.providers.imports` and should be imported
  directly by callers that need to trigger provider module imports.
"""

from .provider import Provider

# Global mapping of provider display name -> provider class
PROVIDERS: dict[str, type[Provider]] = {}


def register_provider(cls: type[Provider]) -> type[Provider]:
    """
    Decorator used by provider modules to register their provider class.

    Idempotent: re-registering the same NAME is a no-op.

    Usage:
        @register_provider
        class ProviderTiktoken(Provider):
            NAME = "OpenAI"
            ...
    """
    name = getattr(cls, "NAME", None)
    if isinstance(name, str) and name and name not in PROVIDERS:
        PROVIDERS[name] = cls
    return cls


def list_registered() -> list[str]:
    """Return a sorted list of registered provider display names."""
    return sorted(PROVIDERS.keys())


__all__ = [
    "Provider",
    "register_provider",
    "PROVIDERS",
    "list_registered",
]
