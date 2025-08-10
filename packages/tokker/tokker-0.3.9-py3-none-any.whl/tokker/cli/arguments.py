#!/usr/bin/env python3
import argparse

from tokker import messages
from tokker.utils import get_version


def build_argument_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser for tokker."""
    parser = argparse.ArgumentParser(
        add_help=False,
        allow_abbrev=False,
        description=(
            f"Tokker {get_version()}: a fast local-first CLI tokenizer with all the "
            "best models in one place"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{messages.SEP_MAIN}
Examples:
  `echo 'Hello world' | tok -o json`
  `tok 'Hello world'`
  `tok 'Hello world' -m deepseek-ai/DeepSeek-R1`
  `tok 'Hello world' -m gemini-2.5-pro -o count`
  `tok 'Hello world' -o pivot`
  `tok -dm cl100k_base`
  `tok -do json`
{messages.SEP_MAIN}
{messages.MSG_DEP_HINT_HEADING}
{messages.MSG_DEP_HINT_ALL}
{messages.MSG_DEP_HINT_TIKTOKEN}
{messages.MSG_DEP_HINT_TRANSFORMERS}
{messages.MSG_DEP_HINT_GOOGLE}

Google auth setup   →   {messages.GOOGLE_AUTH_GUIDE}
        """,
    )

    parser.add_argument(
        "text", nargs="?", help="text to tokenize (or read from stdin if not provided)"
    )
    parser.add_argument(
        "--help",
        action="help",
        help="(or just `tok`) to show this help message",
    )

    parser.add_argument(
        "-w",
        "--with",
        metavar="MODEL",
        type=str,
        help="with specific (non-default) model",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        choices=messages.OutputFormat.values(),
        default=messages.OutputFormat.COLOR.value,
        help="output format",
    )

    parser.add_argument("-m", "--models", action="store_true", help="list all models")

    parser.add_argument(
        "-c", "--config", action="store_true", help="show config with settings"
    )

    parser.add_argument(
        "-dm", "--default-model", metavar="MODEL", type=str, help="set default model"
    )

    parser.add_argument(
        "-do", "--default-output", metavar="OUTPUT", type=str, help="set default output"
    )

    parser.add_argument(
        "-h", "--history", action="store_true", help="show history of used models"
    )

    parser.add_argument(
        "-x", "--history-clear", action="store_true", help="clear history"
    )

    return parser
