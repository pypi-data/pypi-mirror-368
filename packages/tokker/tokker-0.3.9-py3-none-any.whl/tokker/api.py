#!/usr/bin/env python3
"""
Simple public API wrappers over ModelRegistry for programmatic use:
  from tokker import tokenize, count_tokens, count_words, count_characters,
                   list_models, get_providers
"""

import re
from typing import Any

from tokker.models.registry import ModelRegistry


def tokenize(text: str, model: str) -> dict[str, Any]:
    """
    Tokenize text with the given model. Returns a dict with keys:
      - token_strings: list[str]
      - token_ids: list[int]
      - token_count: int
    """
    registry = ModelRegistry()
    return registry.tokenize(text, model)


def count_tokens(text: str, model: str) -> int:
    "Return the token count for the given text and model."
    result = tokenize(text, model)
    token_count = result.get("token_count")
    if isinstance(token_count, (int, float)):
        return int(token_count)
    token_ids = result.get("token_ids") or []
    return len(token_ids)


def count_words(text: str) -> int:
    "Return the number of words in the text."
    if not text.strip():
        return 0
    return len(re.findall(r"\S+", text))


def count_characters(text: str) -> int:
    "Return the number of characters in the text."
    return len(text)


def list_models(provider: str | None = None) -> list[dict[str, str]]:
    """
    Return a canonically sorted list of models, optionally filtered by provider.
    Each item is a dict: {"name": <model_name>, "provider": <provider_name>}
    """
    registry = ModelRegistry()
    return registry.list_models(provider=provider)


def get_providers() -> list[str]:
    "Return a sorted list of provider names."
    registry = ModelRegistry()
    return registry.get_providers()
