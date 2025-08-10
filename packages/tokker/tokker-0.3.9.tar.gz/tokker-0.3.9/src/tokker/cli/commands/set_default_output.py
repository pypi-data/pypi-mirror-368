#!/usr/bin/env python3

from tokker import messages
from tokker.cli.config import config


def run_set_default_output(output: str) -> None:
    """Set the default output format and persist it to the config.

    Validation is performed by Config.set_default_output which will raise a
    ValueError for unknown formats; let exceptions bubble to the centralized
    error handler for consistent user-facing messaging.
    """
    # Validate & persist (let Config handle validation and raise as needed)
    config.set_default_output(output)

    # Confirmation to the user (wrap the value in backticks for clarity)
    print(f"Default output set to: `{output}`")
    print(messages.MSG_CONFIG_SAVED_TO.format(path=config.config_file))
    pass
