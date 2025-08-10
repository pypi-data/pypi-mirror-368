#!/usr/bin/env python3
"""
Lightweight shared helpers used by the CLI and error handling.

This module intentionally avoids importing other tokker modules (like
`tokker.messages`) at module import time so it stays cheap to import.
It provides:
- `get_arg_value` : extract a arg's value from argv (supports split and --arg=value)
- `is_google_model` : heuristic predicate for Google Gemini model names
- `get_version` : lightweight package version lookup that prefers importlib.metadata
                and falls back to `tokker.__version__` then empty string
"""

from collections.abc import Iterable

# Prefer the standard importlib.metadata API (Python >= 3.8)
try:
    from importlib import metadata
except Exception:
    metadata = None  # type: ignore


def get_arg_value(argv: Iterable[str], *flags: str) -> str | None:
    """
    Return the value associated with a CLI flag from argv.

    Supported syntaxes:
      - Split form:        ["tok", "-m", "cl100k_base"]      -> "cl100k_base"
      - --flag=value form: ["tok", "--model=cl100k_base"]    -> "cl100k_base"
    """
    try:
        xs = list(argv)
        flagset = set(flags)
        for i, a in enumerate(xs):
            # Split form: -f VALUE or --flag VALUE
            if a in flagset:
                if i + 1 < len(xs):
                    return xs[i + 1]
                continue
            # --flag=value form
            for f in flagset:
                if a.startswith(f + "="):
                    return a.split("=", 1)[1]
        return None
    except Exception:
        # Best-effort: never raise from argv parsing
        return None


def is_google_model(model: str | None) -> bool:
    """
    Return True if the provided model name starts with "gemini-" or "models/gemini-"
    """
    if not model:
        return False
    return model.startswith("gemini-") or model.startswith("models/gemini-")


def get_version() -> str:
    """
    Return the installed package version for "tokker". Resolution order:
      1. importlib.metadata.version("tokker") -- preferred (no package import)
      2. lazy read of `tokker.__version__` (may import the package; our top-level is minimal)
      3. empty string
    """
    # 1) Try package metadata
    if metadata is not None:
        try:
            return metadata.version("tokker")
        except Exception:
            pass

    # 2) Fallback: try to read tokker.__version__ lazily
    try:
        import tokker as _tokker  # package top-level is intentionally minimal

        ver = getattr(_tokker, "__version__", None)
        if isinstance(ver, str) and ver:
            return ver
    except Exception:
        pass
    return ""
