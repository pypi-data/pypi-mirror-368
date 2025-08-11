"""The DAO for the environment."""

import os
from typing import Optional


def get_bool(key: str, default: bool = False) -> bool:
    env_value: Optional[str] = os.getenv(key)
    if env_value is None:
        return default
    return env_value.casefold() == "true"
