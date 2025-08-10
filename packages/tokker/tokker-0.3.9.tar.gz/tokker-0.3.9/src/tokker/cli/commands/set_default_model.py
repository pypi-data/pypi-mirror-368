#!/usr/bin/env python3

from tokker import messages
from tokker.cli.config import config
from tokker.models.registry import ModelRegistry


def run_set_default_model(model: str) -> None:
    """Set the default model and persist it to the config.

    Validation is performed by resolving a provider via ModelRegistry.get_provider(model).
    Any exceptions raised during resolution are allowed to bubble to the centralized
    error handler, which will render a provider-aware message.
    """
    registry = ModelRegistry()

    # Validate by resolving the provider; let exceptions bubble to the centralized handler
    provider = registry.get_provider_by_model(model)

    # Persist selection on success
    config.set_default_model(model)

    # Display confirmation without tick/description; no blank lines
    provider_name = getattr(provider, "NAME", None) or "Unknown"
    print(messages.MSG_DEFAULT_SET_PROVIDER.format(model=model, provider=provider_name))
    print(messages.MSG_CONFIG_SAVED_TO.format(path=config.config_file))
    pass
