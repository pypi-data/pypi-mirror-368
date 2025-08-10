#!/usr/bin/env python3
from tokker.cli import config, History
from tokker.cli.output.base_json import build_base_json
from tokker.cli.output.formats import format_and_print_output
from tokker.models.registry import ModelRegistry


def run_tokenize(text: str, model: str | None, output_format: str) -> None:
    """Tokenize text with selected or default model, format, and print output."""
    selected_model = _select_model(model)
    registry = ModelRegistry()

    # Let any errors bubble up to main; no local validation or error routing
    tokenization_result = registry.tokenize(text, selected_model)

    # Track model usage and get delimiter (let errors bubble)
    History(config.config_dir).add_model(selected_model)
    delimiter = config.get_delimiter()

    # Build canonical base JSON and print in the desired format
    result = build_base_json(tokenization_result, text, delimiter)
    format_and_print_output(result, output_format, delimiter)
    pass


# ---- Command helpers (local to CLI) ----


def _select_model(model: str | None) -> str:
    """Choose the model from CLI arg or default configuration."""
    return model if model else config.get_default_model()
