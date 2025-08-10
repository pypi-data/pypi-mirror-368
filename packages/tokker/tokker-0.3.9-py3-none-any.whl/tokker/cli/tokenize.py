#!/usr/bin/env python3
"""
Main CLI entrypoint for tokker.

This module keeps imports minimal at module import time to avoid pulling in
command handlers, configuration, or provider modules unless the user actually
requests the corresponding functionality. Heavy or command-specific imports are
performed lazily inside the decision branches after `args = parser.parse_args()`.
"""

import sys
import json

# Apply centralized runtime/environment setup early (keeps env defaults small)
import tokker.runtime as _tokker_runtime  # noqa: F401

from tokker.cli.arguments import build_argument_parser


def main() -> int:
    """Parse CLI args and dispatch to the right command (lazy-import handlers)."""
    parser = build_argument_parser()
    args = parser.parse_args()

    # ---- List models ----
    if getattr(args, "models", False):
        # Local import to avoid loading registry/providers on every tok invocation.
        from tokker.cli.commands.list_models import run_list_models

        run_list_models()
        return 0

    # ---- History commands ----
    if getattr(args, "history", False):
        from tokker.cli.commands.show_history import run_show_history

        run_show_history()
        return 0

    if getattr(args, "history_clear", False):
        from tokker.cli.commands.clear_history import run_clear_history

        run_clear_history()
        return 0

    # ---- Set default model ----
    if getattr(args, "default_model", None):
        # Validate & persist via command handler (which uses ModelRegistry lazily)
        from tokker.cli.commands.set_default_model import run_set_default_model

        run_set_default_model(getattr(args, "default_model"))
        return 0

    # ---- Set default output ----
    if getattr(args, "default_output", None):
        # Lazy import config and messages to avoid module-level imports
        from tokker.cli.config import config
        from tokker import messages

        cfg_out = getattr(args, "default_output")
        # Let Config.validate raise if the output is unknown
        config.set_default_output(cfg_out)
        print(f"Default output set to: `{cfg_out}`")
        print(messages.MSG_CONFIG_SAVED_TO.format(path=config.config_file))
        return 0

    # ---- Show config ----
    if getattr(args, "config", False):
        from tokker.cli.config import config

        cfg = config.load()
        print(json.dumps(cfg, indent=2, ensure_ascii=False))
        return 0

    # ---- Read text (argument or stdin) ----
    text = None
    if getattr(args, "text", None) is not None:
        text = args.text
    elif not sys.stdin.isatty():
        text = sys.stdin.read().strip()

    if text:
        # Decide which output format to use:
        # - If the user explicitly passed -o/--output, honor it.
        # - Otherwise, fall back to configured default_output.
        argv = list(sys.argv or [])
        explicit_output = any(a == "-o" or a.startswith("--output") for a in argv)

        # If we didn't explicitly pass an output, consult persisted config.
        if explicit_output:
            output_choice = args.output
        else:
            # Lazy import config to avoid startup cost when not needed
            from tokker.cli.config import config

            output_choice = config.get_default_output()

        # Lazy import the tokenizer command implementation
        from tokker.cli.commands.tokenize_text import run_tokenize

        run_tokenize(
            text,
            getattr(args, "with", None) or getattr(args, "model", None),
            output_choice,
        )
        return 0

    # No text provided: show help and return non-zero
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
