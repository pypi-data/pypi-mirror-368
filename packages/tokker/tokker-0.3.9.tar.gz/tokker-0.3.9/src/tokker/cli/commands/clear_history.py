#!/usr/bin/env python3
from tokker import messages
from tokker.cli import config, History


def run_clear_history() -> None:
    """Clear saved model usage history."""
    history = History(config.config_dir).load()

    if not history:
        print(messages.MSG_HISTORY_ALREADY_EMPTY)
        return

    History(config.config_dir).clear()

    print(messages.MSG_HISTORY_CLEARED)
    pass
