#!/usr/bin/env python3
"""
Top-level entry point for the tokker CLI.

This module performs minimal work at import time:
- applies runtime environment setup via `tokker.runtime`
- lazily imports the CLI `tokenize` module inside `main()` to avoid
  import-time circular dependencies
- routes all exceptions (including import errors) to the centralized
  `handle_exception` handler which maps them to user-facing messages.
"""

import sys

# Apply centralized runtime/environment setup early
import tokker.runtime as _tokker_runtime  # noqa

from tokker.error_handler import handle_exception


def main() -> int:
    try:
        # Import the CLI entry lazily to avoid circular imports at module import time.
        from tokker.cli.tokenize import main as cli_main

        return cli_main()
    except Exception as e:
        # Let the centralized handler map and print the error, and return its exit code.
        return handle_exception(e, sys.argv or [])


if __name__ == "__main__":
    sys.exit(main())
