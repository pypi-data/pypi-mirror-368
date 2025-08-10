#!/usr/bin/env python3
import re
from typing import Any


def build_base_json(
    tokenization_result: dict[str, Any],
    text: str,
    delimiter: str,
) -> dict[str, Any]:
    """
    Build the base JSON structure for CLI consumption from a tokenization result.

    tokenization_result is expected to contain:
      - 'token_strings': list[str]
      - 'token_ids': list[int]
      - 'token_count': int
    """
    _ts = tokenization_result.get("token_strings", [])
    _tids = tokenization_result.get("token_ids", [])
    _tcount = tokenization_result.get("token_count", 0)

    token_strings: list[str] = [str(s) for s in _ts] if isinstance(_ts, list) else []
    token_ids: list[int] = [int(i) for i in _tids] if isinstance(_tids, list) else []
    token_count = int(_tcount) if isinstance(_tcount, (int, float)) else 0

    pivot: dict[str, int] = {}
    for s in token_strings:
        if s:
            pivot[s] = pivot.get(s, 0) + 1

    return {
        "delimited_text": delimiter.join(token_strings),
        "token_strings": token_strings,
        "token_ids": token_ids,
        "token_count": token_count,
        "word_count": _count_words(text),
        "char_count": len(text),
        "pivot": pivot,
    }


# ---- helpers (kept local for base builder) ----


def _count_words(text: str) -> int:
    if not text.strip():
        return 0
    return len(re.findall(r"\S+", text))
