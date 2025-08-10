#!/usr/bin/env python3
"""
CLI output formatters. This module is presentation-only:
- Dispatches base JSON dict to a chosen output format handler.
- Delegates ANSI token rendering and counts formatting to output utilities.
- Provides JSON / count / pivot outputs using a compact pretty-printer.
"""

from typing import Any, Callable
import json

from tokker import messages
from tokker.cli.output.utils_output import render_colored_tokens, add_counts


def format_and_print_output(
    base_json: dict[str, Any], output_format: str, delimiter: str
) -> None:
    """
    Dispatch the tokenization `result` to a named output formatter.
    """
    if not isinstance(output_format, str):
        raise ValueError(f"Unknown output format: {output_format}")

    value = output_format.strip().lower()
    allowed = {m.value: m for m in messages.OutputFormat}
    member = allowed.get(value)
    if member is None:
        # Keeps the stable error prefix consumed by the centralized handler.
        raise ValueError(f"Unknown output format: {output_format}")

    handlers: dict[messages.OutputFormat, Callable[[], None]] = {
        messages.OutputFormat.COLOR: lambda: _print_color(base_json),
        messages.OutputFormat.JSON: lambda: _print_json(base_json),
        messages.OutputFormat.DEL: lambda: _print_del(base_json, delimiter),
        messages.OutputFormat.COUNT: lambda: _print_count(base_json),
        messages.OutputFormat.PIVOT: lambda: _print_pivot(base_json),
    }

    handler = handlers.get(member)
    if handler is None:
        raise ValueError(f"Unknown output format: {output_format}")

    handler()
    pass


# ---- Handlers ----


def _print_color(result: dict[str, Any]) -> None:
    tokens = result.get("token_strings", []) or []
    out = render_colored_tokens(tokens, include_delimiter=False)
    # Print tokens, then a blank line + summary. add_counts returns a string that
    # already begins with a newline, so use end="" to avoid adding an extra newline.
    print(out)
    print(add_counts(result))
    pass


def _print_del(result: dict[str, Any], delimiter: str) -> None:
    tokens = result.get("token_strings", []) or []
    out = render_colored_tokens(tokens, delimiter=delimiter, include_delimiter=True)
    print(out)
    print(add_counts(result))
    pass


def _print_json(result: dict[str, Any]) -> None:
    json_result = {
        "delimited_text": result.get("delimited_text", ""),
        "token_strings": result.get("token_strings", []),
        "token_ids": result.get("token_ids", []),
        "token_count": result.get("token_count", 0),
        "word_count": result.get("word_count", 0),
        "char_count": result.get("char_count", 0),
    }
    print(_format_json_output(json_result))
    pass


def _print_count(result: dict[str, Any]) -> None:
    count_summary = {
        "token_count": result.get("token_count", 0),
        "word_count": result.get("word_count", 0),
        "char_count": result.get("char_count", 0),
    }
    print(_format_json_output(count_summary))
    pass


def _print_pivot(result: dict[str, Any]) -> None:
    pivot = result.get("pivot", {}) or {}
    items = sorted(pivot.items(), key=lambda kv: (-kv[1], kv[0]))
    table_obj = {k: v for k, v in items}
    print(_format_json_output(table_obj))
    pass


# ---- Low-level formatters ----


def _format_json_output(data: dict[str, Any]) -> str:
    """
    Pretty-compact JSON printer: dicts multi-line and indented; lists one line.
    Preserves unicode characters.
    """

    def compact(obj: Any, indent: int = 0, step: int = 2) -> str:
        if isinstance(obj, dict):
            if not obj:
                return "{}"
            pad, pad_next = " " * indent, " " * (indent + step)
            items = (
                f'{pad_next}"{k}": {compact(v, indent + step, step)}'
                for k, v in obj.items()
            )
            return "{\n" + ",\n".join(items) + f"\n{pad}" + "}"
        if isinstance(obj, list):
            return "[" + ", ".join(json.dumps(x, ensure_ascii=False) for x in obj) + "]"
        return json.dumps(obj, ensure_ascii=False)

    return compact(data)
