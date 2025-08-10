#!/usr/bin/env python3
"""
CLI package initializer.

This module intentionally avoids importing the `tokenize` submodule at import
time to prevent circular imports. The `tokenize` module imports other parts of
the `tokker.cli` package, so we lazily import it inside the public entry points.

Exports:
- `config` (Config instance) from `.config`
- `History` (history persistence class) from `.history`
- `main` and `main_entry` which lazily call `.tokenize.main`
"""

# Re-export stable, import-time-safe objects
from .config import config
from .history import History

# ---- Lazy entry points ----


def main(*args, **kwargs):
    """
    Lazily import and call `tokker.cli.tokenize.main`.

    This avoids importing the `tokenize` submodule during package import,
    which would otherwise create an import-time circular dependency.
    """
    from .tokenize import main as _main

    return _main(*args, **kwargs)


def main_entry(*args, **kwargs):
    """Backward-compatible entry point that delegates to `main`."""
    return main(*args, **kwargs)


# Public API
__all__ = ["main", "main_entry", "config", "History"]
