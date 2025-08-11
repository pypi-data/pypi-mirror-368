#!/usr/bin/env python3

"""Shared constants"""

import os
import pathlib
from importlib.metadata import version
from typing import List, Tuple

VERSION: str = version("work")
RECORDS_VERSION: int = 3

# Directories
PARENT_DIR: pathlib.Path = pathlib.Path("~", ".local", "share").expanduser()
DIRECTORY: pathlib.Path = PARENT_DIR.joinpath("work")
DIRECTORY_DEBUG: pathlib.Path = PARENT_DIR.joinpath("debug", "work")

# Paths – work directory
PROTOCOL_DIRECTORY_NAME = "records"
PROTOCOL_FILE_EXTENSION = "wprot"
INFO_FILE_NAME = "info.winf"
RUN_FILE_NAME = "running.wtime"
RECESS_DIRECTORY_NAME = "recess"
RECESS_FILE_EXTENSION = "wvac"


def _resolve_xdg_path(env_var: str, default: str) -> str:
    """Get path at `env_var` or default, and expand user and variables."""
    path_or_default: str = os.environ.get(env_var, default)
    return os.path.expanduser(os.path.expandvars(path_or_default))


# Configuration – XDG_CONFIG_HOME
_CONFIG_HOME: str = _resolve_xdg_path("XDG_CONFIG_HOME", os.path.join("~", ".config"))
RC_FILE: pathlib.Path = pathlib.Path(_CONFIG_HOME, "workrc")

# Flags – XDG_STATE_HOME
_STATE_HOME: str = _resolve_xdg_path(
    "XDG_STATE_HOME", os.path.join("~", ".local", "state")
)
FLAG_FILE: pathlib.Path = pathlib.Path(_STATE_HOME, "work", "flags.wstate")
FLAG_FILE_DEBUG: pathlib.Path = pathlib.Path(_STATE_HOME, "work", "flags-debug.wstate")

# Environment variables
env_prefix: str = "WORK_"
ENV_DEBUG: str = f"{env_prefix}DEBUG"
ENV_NO_SET_FLAGS: str = f"{env_prefix}DONT_SET_FLAGS"

# Formats
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"

# Patterns
INFO_FILE_CONTENT = "work-time-protocol/protocol-v{}/last-edit:{}/checksum:{}\n"
INFO_FILE_PATTERN = INFO_FILE_CONTENT.format(
    r"(\d{1,2})", r"(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2})", r"(\d+)"
)

TIME_PATTERN = r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}"
YEAR_DIR_PATTERN = r"\d{4}"
MONTH_DIR_PATTERN = r"(0[1-9]|1[0-2])"
DAY_PATTERN = r"([0-2][0-9]|3[0-1])"
DAY_FILE_PATTERN = DAY_PATTERN + r"\." + PROTOCOL_FILE_EXTENSION

# Values
WEEKDAYS: List[str] = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
ALLOWED_WORK_HOURS: Tuple[float, float] = (0.0, 24.0)
