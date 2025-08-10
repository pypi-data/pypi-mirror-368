#!/usr/bin/env python3
"""
ModelRegistry facade using discovery and model_index helpers:
- Owns registry state (providers, provider classes, model index, cache path).
- Orchestrates discovery (cache read/validate, guarded imports) via tokker.models.discovery.
- Builds model index via tokker.models.model_index.
- Lazily instantiates providers and delegate tokenization.
"""

from tokker.providers import Provider, PROVIDERS

from tokker.models.discovery import (
    CACHE_DEFAULT_PATH,
    load_models_from_cache,
    write_cache,
)
from tokker.providers.imports import load_providers, load_provider
from tokker.models.model_index import build_model_index


class ModelRegistry:
    def __init__(self) -> None:
        # Instantiated provider instances by provider name
        self._providers: dict[str, Provider] = {}
        # Registered provider classes by provider name (populated from PROVIDERS)
        self._provider_classes: dict[str, type[Provider]] = {}
        # Static model -> provider_name mapping (from class-level MODELS or cache)
        self._model_to_provider: dict[str, str] = {}
        self._discovered: bool = False
        # Cache file path
        self._cache_path = CACHE_DEFAULT_PATH
        # Provider display names known from cache or computed; may be present even before classes import
        self._provider_names: set[str] = set()
        pass

    def _ensure_discovered(self) -> None:
        """Perform discovery once: try cache, otherwise guarded imports + build index."""
        if self._discovered:
            return

        # 1) Try cache
        result = load_models_from_cache(self._cache_path)
        if result:
            # Populate model index and provider names from cache without importing provider modules
            if isinstance(result, tuple):
                cache_index, provider_names = result
            else:
                cache_index, provider_names = result, []
            self._model_to_provider = dict(cache_index)
            # Cache provider display names for quick listing even before modules are imported
            self._provider_names = set(provider_names) or set(
                self._model_to_provider.values()
            )
            # Snapshot provider classes (may be empty until provider modules are imported)
            self._provider_classes = dict(PROVIDERS)
            self._discovered = True
            return

        # 2) Cache not usable -> import provider modules (best-effort)
        load_providers()

        # 3) Snapshot provider classes and build index
        self._provider_classes = dict(PROVIDERS)
        model_index = build_model_index(self._provider_classes)
        self._model_to_provider = model_index

        # 4) Persist a fresh cache (best-effort)
        try:
            write_cache(
                self._cache_path,
                sorted(list(self._provider_classes.keys())),
                model_index,
            )
        except Exception:
            pass

        self._discovered = True
        pass

    def _ensure_provider_instance(self, provider_name: str) -> Provider:
        """Return cached provider instance or instantiate via provider helper."""
        # Keep import local to avoid import-time cycles.
        from tokker.providers.instances import instantiate_provider

        # Ensure discovery has been run (may populate _provider_classes via cache)
        if not self._discovered:
            self._ensure_discovered()

        # Delegate instantiation and caching to providers.instances.instantiate_provider
        inst = instantiate_provider(provider_name, self._providers)
        return inst

    def _find_provider_for_model(self, model_name: str) -> str | None:
        """
        Resolve a model name to a provider:
          - static index first
          - fallback: probe HuggingFace provider for BYOM via its validator
        """
        provider_name = self._model_to_provider.get(model_name)
        if provider_name:
            return provider_name

        # Attempt lazy import of HuggingFace provider to support BYOM on cache-only startup.
        if not self._provider_classes.get("HuggingFace"):
            load_provider("HuggingFace")
            # Refresh provider classes snapshot after attempting import
            self._provider_classes = dict(PROVIDERS)
            if not self._provider_classes.get("HuggingFace"):
                return None

        provider = self._ensure_provider_instance("HuggingFace")
        validate = getattr(provider, "is_on_huggingface", None)
        if callable(validate) and validate(model_name):
            return getattr(provider, "NAME", "HuggingFace")
        return None

    # -------- public API --------

    def get_provider_by_model(self, model_name: str) -> Provider:
        """Return a provider instance that supports the given model name."""
        self._ensure_discovered()
        provider_name = self._find_provider_for_model(model_name)
        if not provider_name:
            raise Exception(f"Model not found: {model_name}")
        return self._ensure_provider_instance(provider_name)

    def list_models(self, provider: str | None = None) -> list[dict[str, str]]:
        """List known models, optionally filtered by provider name."""
        self._ensure_discovered()
        items = [
            {"name": m, "provider": p}
            for m, p in self._model_to_provider.items()
            if provider is None or p == provider
        ]
        return sorted(items, key=lambda i: (i["name"], i["provider"]))

    def get_providers(self) -> list[str]:
        """Return sorted provider names."""
        self._ensure_discovered()
        names: set[str] = set()
        if self._provider_classes:
            names.update(self._provider_classes.keys())
        if getattr(self, "_provider_names", None):
            names.update(self._provider_names)
        if not names and self._model_to_provider:
            names.update(self._model_to_provider.values())
        return sorted(names)

    def is_model_supported(self, model_name: str) -> bool:
        """Check if a model name is resolvable to a provider."""
        self._ensure_discovered()
        return self._find_provider_for_model(model_name) is not None

    def tokenize(
        self,
        text: str,
        model_name: str,
    ) -> dict[str, str | int | list[str] | list[int]]:
        """Tokenize text via the appropriate provider; let exceptions bubble raw."""
        provider = self.get_provider_by_model(model_name)
        return provider.tokenize(text, model_name)
