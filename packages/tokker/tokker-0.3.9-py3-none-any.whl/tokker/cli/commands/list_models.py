#!/usr/bin/env python3
"""
List available models with static, provider-sectioned guidance.

This module intentionally avoids probing which optional provider packages are
installed. Output is deterministic and provides static guidance for installing
dependencies and for BYOM (HuggingFace) usage.
"""

from tokker import messages
from tokker.models.registry import ModelRegistry


def run_list_models() -> None:
    """List available models, grouped by provider with curated static messaging."""
    registry = ModelRegistry()

    # Main separator
    print(messages.SEP_MAIN)

    # ---- OpenAI section ----
    print(messages.HDR_OPENAI)
    # Emit strictly in the insertion order defined by OPENAI_DESCRIPTIONS
    openai_models = registry.list_models("OpenAI")
    openai_names = {m["name"] for m in openai_models}
    for name in messages.OPENAI_DESCRIPTIONS.keys():
        if name in openai_names:
            description = messages.OPENAI_DESCRIPTIONS.get(name, "")
            if description:
                print(f"{name:<22}{description}")
            else:
                print(f"{name}")

    # Sub-separator
    print(messages.SEP_SUB)

    # ---- Google section ----
    print(messages.HDR_GOOGLE)
    # List Google models in reverse alphabetical order and show auth guidance
    google_models = registry.list_models("Google")
    for model in sorted(google_models, key=lambda m: m["name"], reverse=True):
        print(f"{model['name']}")
    # Static note about auth/setup
    print(messages.MSG_AUTH_REQUIRED)

    # Sub-separator
    print(messages.SEP_SUB)

    # ---- HuggingFace BYOM guidance ----
    print(messages.HDR_HF)
    for line in messages.BYOM_INSTRUCTIONS:
        print(line)
    for example in messages.BYOM_EXAMPLE_MODELS:
        print(f"{example}")

    # Final separator
    print(messages.SEP_MAIN)
