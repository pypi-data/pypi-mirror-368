#!/usr/bin/env python3
from tokker import messages
from tokker.cli import config, History


def run_show_history() -> None:
    history = History(config.config_dir).load()

    print(messages.SEP_MAIN)
    print(messages.HDR_HISTORY)

    if not history:
        print(messages.MSG_HISTORY_EMPTY)
        print(messages.SEP_MAIN)
        return

    for entry in history:
        model_name = entry.get("model", "unknown")
        timestamp = entry.get("timestamp", "")
        ts = str(timestamp).replace("T", " ")[:16]
        print(f"{model_name:<32}{ts}")

    print(messages.SEP_MAIN)
    pass
