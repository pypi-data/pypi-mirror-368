#!/usr/bin/env python3

import re
import sys
from typing import Iterable

from tokker import messages
from tokker.utils import get_arg_value, is_google_model


def handle_exception(e: Exception, argv: list[str]) -> int:
    """
    Map low-level exceptions to user-facing stderr messages and return exit code 1.
    Prints only to stderr and never calls sys.exit() so caller can decide.
    """
    err_text = str(e) if e is not None else ""
    lower = err_text.lower()

    # small helpers for brevity
    def _write(line: str) -> None:
        sys.stderr.write(line + "\n")
        pass

    def _write_fmt(fmt: str, /, **kwargs) -> None:
        _write(fmt.format(**kwargs))
        pass

    def _return_1_after(fn, *args, **kwargs) -> int:
        fn(*args, **kwargs)
        return 1

    def any_in_lower(keys: Iterable[str]) -> bool:
        return any(k in lower for k in keys)

    # 1) Specific known errors: formatter unknown output format
    if isinstance(e, ValueError) and err_text.startswith("Unknown output format: "):
        value = err_text.split(":", 1)[1].strip()
        return _return_1_after(
            _write_fmt, messages.MSG_UNKNOWN_OUTPUT_FORMAT_FMT, value=f"`{value}`"
        )

    # 1b) If setting default model, always print the model-not-found block
    model_default_arg = get_arg_value(argv, "-dm", "--default-model")
    if model_default_arg:
        return _return_1_after(_print_model_not_found, model_default_arg)

    # 2) Candidate model: explicit -w/--with or configured default
    model_arg = get_arg_value(argv, "-w", "--with")
    if not model_arg:
        try:
            # Local import to avoid import cycles
            from tokker.cli.config import config  # type: ignore

            model_arg = config.get_default_model() or None
        except Exception:
            model_arg = None

    model_name_safe = bool(model_arg and re.match(r"^[A-Za-z0-9_.:/\\-]+$", model_arg))

    # 3) Model-related diagnostics (missing dep or unknown/invalid)
    if model_name_safe and any_in_lower(["no module found"]):
        return _return_1_after(_print_model_not_found, model_arg)
    if model_name_safe and any_in_lower(
        ["not found", "unknown model", "invalid model"]
    ):
        return _return_1_after(_print_model_not_found, model_arg)

    # 4) Google-specific guidance
    if is_google_model(model_arg) or (
        any_in_lower(["compute_tokens"]) and "google" in lower
    ):
        return _return_1_after(_print_google_guidance, model_arg)

    # 5) Filesystem / IO errors
    fs_keys = [
        "permission denied",
        "read-only file system",
        "ioerror",
        "is a directory",
        "not a directory",
    ]
    if isinstance(e, (OSError, IOError)) or any_in_lower(fs_keys):
        return _return_1_after(
            _write_fmt, messages.MSG_FILESYSTEM_ERROR_FMT, err=err_text
        )

    # 6) JSON / config parsing errors
    json_keys = [
        "jsondecodeerror",
        "expecting value",
        "invalid json",
        "unterminated string",
    ]
    if any_in_lower(json_keys):
        return _return_1_after(_write_fmt, messages.MSG_CONFIG_ERROR_FMT, err=err_text)

    # 7) Fallback unexpected error
    return _return_1_after(_write_fmt, messages.MSG_UNEXPECTED_ERROR_FMT, err=err_text)


# ---- Internal helpers ----


def _print_model_not_found(model: str | None) -> None:
    providers_str = "none"
    model_display = f"`{model}`" if model else "<unknown>"
    sys.stderr.write(
        messages.MSG_DEFAULT_MODEL_UNSUPPORTED_FMT.format(
            model=model_display, providers=providers_str
        )
        + "\n"
    )
    _print_lines(
        [
            messages.MSG_DEP_HINT_HEADING,
            messages.MSG_DEP_HINT_ALL,
            messages.MSG_DEP_HINT_TIKTOKEN,
            messages.MSG_DEP_HINT_GOOGLE,
            messages.MSG_DEP_HINT_TRANSFORMERS,
        ]
    )
    pass


def _print_lines(lines: Iterable[str]) -> None:
    sys.stderr.write("".join(f"{line}\n" for line in lines))
    pass


def _print_google_guidance(model: str | None) -> None:
    _print_lines([messages.MSG_GOOGLE_AUTH_HEADER, messages.MSG_GOOGLE_AUTH_GUIDE_URL])
    pass
