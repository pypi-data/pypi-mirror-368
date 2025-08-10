#!/usr/bin/env python3
"""
CLI output utilities for token rendering and summary formatting.

Public functions:
- render_colored_tokens(tokens, delimiter="⎮", include_delimiter=False, bg_pattern=None) -> str
- add_counts(result) -> str

They use explicit SGR sequences to ensure black glyphs render on bright backgrounds.
"""

from typing import Any, Iterable


# ANSI sequences (kept local to this module)
_ANSI_RESET = "\x1b[0m"
# Use explicit 256-color foreground sequence for black to ensure glyphs stay black
# even on bright backgrounds (e.g., SGR background 107).
_ANSI_FG_BLACK_256 = "38;5;0"
# Default rotating bright-background SGR codes (easy to read and edit)
_DEFAULT_BG_PATTERN = ["106", "107", "102", "103"]


def render_colored_tokens(
    tokens: Iterable[str],
    delimiter: str = "⎮",
    include_delimiter: bool = False,
    bg_pattern: list[str] | None = None,
) -> str:
    """
    Render a sequence of token strings with ANSI styling.

    Args:
        tokens: Each token is wrapped in an ANSI sequence for color formatting.
        delimiter: Inserted unstyled.
        include_delimiter: If True, join colored token fragments with `delimiter`.
        bg_pattern: Optional list of background SGR codes (strings). If omitted,
                    a default 4-color bright pattern is used.

    Returns:
        A single string ready to print to a terminal that supports ANSI SGR codes.
    """
    pattern = bg_pattern or _DEFAULT_BG_PATTERN
    parts: list[str] = []
    idx = 0
    for t in tokens:
        bg = pattern[idx % len(pattern)]
        # Compose SGR: explicit 256-color foreground black + bright background SGR.
        # Example piece: "\x1b[38;5;0;106mThe\x1b[0m"
        part = f"\x1b[{_ANSI_FG_BLACK_256};{bg}m{t}{_ANSI_RESET}"
        parts.append(part)
        idx += 1

    if include_delimiter:
        # Join with delimiter (unstyled) so delimiter is not affected by token styling.
        return delimiter.join(parts)
    return "".join(parts)


def add_counts(result: dict[str, Any]) -> str:
    """
    Build a human-readable counts summary string from a tokenization result.

    Args:
        result: Base result dict (as produced by `build_base_json`).

    Returns:
          "nCount: 8 tokens, 6 words, 31 chars."
    """
    token_val = result.get("token_count") or 0
    if isinstance(token_val, (int, float)) and not isinstance(token_val, bool):
        token_count = int(token_val)
    elif isinstance(token_val, str) and token_val.isdigit():
        token_count = int(token_val)
    else:
        token_count = 0

    word_val = result.get("word_count") or 0
    if isinstance(word_val, (int, float)) and not isinstance(word_val, bool):
        word_count = int(word_val)
    elif isinstance(word_val, str) and word_val.isdigit():
        word_count = int(word_val)
    else:
        word_count = 0

    char_val = result.get("char_count") or 0
    if isinstance(char_val, (int, float)) and not isinstance(char_val, bool):
        char_count = int(char_val)
    elif isinstance(char_val, str) and char_val.isdigit():
        char_count = int(char_val)
    else:
        char_count = 0

    return f"{token_count} tokens, {word_count} words, {char_count} chars"
