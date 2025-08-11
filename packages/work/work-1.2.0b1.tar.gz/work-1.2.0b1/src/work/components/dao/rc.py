#!/usr/bin/env python3

# pylint: disable-msg=invalid-name

"""The DAO for the runtime configuration file."""

import json
from collections import ChainMap
from typing import (
    IO,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Optional,
)

from work.components import consts
from work.components.arguments import MODES
from work.components.consts import RC_FILE

# When a new key is to be added:
# - Add key string as class variable
# - Add default value to default_config
# - Implement check in _ensure_config_correctness()
#
# In work.py:
# - Add actual functionality related to the configuration
# - (optional) Add see target to see()


TIME_FORMAT = "%H:%M"


class RCError(OSError):
    """Error in runtime configuration file"""

    def __init__(self, msg):
        super().__init__("RC file erroneous! {}".format(msg))


class RC:
    """Runtime configuration"""

    expected_hours_k = "expected_hours"
    aliases_k = "aliases"
    macros_k = "macros"
    rounding_precision_k = "rounding_precision"

    default_config: Dict[str, Any] = {
        expected_hours_k: dict(zip(consts.WEEKDAYS, [8.0] * 5 + [0.0] * 2)),
        aliases_k: {
            "status": ["s"],
            "hours": ["h"],
            "list": ["ls"],
            "edit": ["e"],
            "remove": ["rm"],
        },
        macros_k: {
            "day": "list --include-active --with-breaks --list-empty",
            "macros": "config --see macros",  # aliases can be seen with work -h
        },
        rounding_precision_k: 15,
    }

    instance: Optional["RC"] = None

    def __new__(cls):
        """Initialize config with default values and user configuration.

        If any RC file exists, retrieve it. If not, create a basic file."""

        if RC.instance is not None:
            return RC.instance

        if not RC_FILE.exists():
            with RC_FILE.open("w", encoding="utf-8", newline="\n") as rc_file:
                rc_file.write(RC.default_rc_content())
            print(
                f"Configuration file with default values created at {RC_FILE}\n"
                '  Check and edit the file with "$EDITOR (work config --path)".\n'
            )

        user_config: Dict
        with RC_FILE.open("r", encoding="utf-8") as rc_file:
            try:
                user_config = json.load(rc_file)
            except json.JSONDecodeError as json_err:
                raise RCError(
                    f"Invalid JSON encountered around line {json_err.lineno} – did you "
                    "forget quotes or add an (invalid) trailing comma to a list?"
                ) from json_err

        RC._ensure_config_correctness(user_config)
        try:
            RC._ensure_config_correctness(RC.default_config)
        except RCError as rc_err:
            raise RuntimeError("Invalid default configuration") from rc_err

        RC.instance = super().__new__(cls)
        RC.instance._config = ChainMap(user_config, RC.default_config)
        return RC.instance

    def __init__(self):
        """Noop. Defines instance variables (but does NOT set them)."""
        self._config: ChainMap

    @property
    def expected_hours(self) -> Dict[str, float]:
        """The hours expected on each day of the week."""
        return self._config[RC.expected_hours_k]

    @property
    def aliases(self) -> Dict[str, List[str]]:
        """Aliases for work commands."""
        return self._config[RC.aliases_k]

    @property
    def macros(self) -> Dict[str, str]:
        """Macros that expand to command and argument(s) or flag(s)."""
        return self._config[RC.macros_k]

    @property
    def rounding_precision(self) -> int:
        """Bucket size of rounding (in minutes)."""
        return self._config[RC.rounding_precision_k]

    @property
    def _user_config(self) -> MutableMapping:
        """In-memory representation of the user configuration."""
        return self._config.maps[-2]

    ### I/O ###

    def dump(self, rc_file: IO) -> None:
        """Write this RC's user configuration to file."""

        # Data have been verified on instantiation
        json.dump(self._user_config, rc_file, indent="\t", ensure_ascii=False)

    ### Static methods ###

    @staticmethod
    def default_rc_content() -> str:
        """Create the contents of an example RC file, setting all keys."""
        return json.dumps(RC.default_config, indent="\t")

    @staticmethod
    def set_test_config(**kwargs) -> None:
        """Add a configuration that overrides the default and user configurations."""
        rc = RC()
        if len(rc._config.maps) < 3:
            rc._config = rc._config.new_child(dict())
        rc._config.update(kwargs)

    @staticmethod
    def _ensure_config_correctness(data: Mapping) -> None:
        """Ensure that the mapping is fit for JSON (de)serialization. Raises if not."""

        expected_keys: Iterable[str] = RC.default_config.keys()
        for k in data:
            if k not in expected_keys:
                raise RCError(f'Unexpected key "{k}"')

        verifiers: Dict[str, Callable] = {
            RC.expected_hours_k: RC._verify_expected_hours,
            RC.aliases_k: RC._verify_aliases,
            RC.macros_k: RC._verify_macros,
            RC.rounding_precision_k: RC._verify_rounding_precision,
        }

        for key, verifier in verifiers.items():
            if key in data:
                verifier(data[key])

    @staticmethod
    def _verify_expected_hours(expected_hours) -> None:
        """Verify the value for expected hours. Raises RCError if invalid."""

        # Should be a mapping of day to hours: { "Monday": 8.0, Tuesday: 0.0, ... }
        if not isinstance(expected_hours, Mapping):
            raise RCError(f'"{RC.expected_hours_k}" expects a mapping.')

        if unexpected_days := set(expected_hours.keys()) - set(consts.WEEKDAYS):
            raise RCError(
                f'Unexpected key(s) for "{RC.expected_hours_k}": '
                + ", ".join(unexpected_days)
                + f"; expects one of: {', '.join(consts.WEEKDAYS)}"
            )

        if missing_days := set(consts.WEEKDAYS) - set(expected_hours.keys()):
            raise RCError(
                f'Missing expected key(s) for "{RC.expected_hours_k}": '
                + ", ".join(missing_days)
            )

        if list(expected_hours.keys()) != consts.WEEKDAYS:
            raise RCError(
                f'Keys for "{RC.expected_hours_k}" are sorted incorrectly; '
                + f"expects: {', '.join(consts.WEEKDAYS)}"
            )

        min_hours, max_hours = consts.ALLOWED_WORK_HOURS
        if invalid_hours := [
            expected_hour_value
            for expected_hour_value in expected_hours.values()
            if expected_hour_value < min_hours or expected_hour_value > max_hours
        ]:
            raise RCError(
                f'Invalid value(s) for "{RC.expected_hours_k}": '
                + ", ".join([str(i_h) for i_h in invalid_hours])
                + f"; expects values in ({min_hours}, {max_hours})."
            )

    @staticmethod
    def _verify_aliases(aliases) -> None:
        """Verify the value for aliases. Raises RCError if invalid."""

        # Should be a mapping of commands to list of aliases: { "status": ["s"], "edit": [] }
        if not isinstance(aliases, Mapping):
            raise RCError(f'"{RC.aliases_k}" expects a mapping.')

        for key in aliases.keys():
            if key not in MODES:
                raise RCError(
                    f'Key "{key}" is not a valid command name. '
                    f"Must be one of: {MODES.keys()}"
                )

        for value in aliases.values():
            if not isinstance(value, list):
                raise RCError(f"Expected a list; got: {value}")

    @staticmethod
    def _verify_macros(macros) -> None:
        """Verify the value for macros. Raises RCError if invalid."""

        # Should be a mapping of commands to list of aliases: { "status": ["s"], "edit": [] }
        if not isinstance(macros, Mapping):
            raise RCError(f'"{RC.macros_k}" expects a mapping.')

        for key, value in macros.items():
            if key.startswith("-"):
                raise RCError(f'Macros may not start with "-"; found: "{key}"')

            if key in MODES:
                raise RCError(
                    f'Macros may not override existing commands; found: "{key}"'
                )

            if not isinstance(value, str):
                raise RCError(f"Expected a string; got: {value}")

            if "  " in value:
                raise RCError(f'Macro "{key}" contains extra spaces: "{value}"')

    @staticmethod
    def _verify_rounding_precision(rounding_precision) -> None:
        """Verify the value for rounding_precision. Raises RCError if invalid."""

        # Should be an integer in [1, 60]
        try:
            rounding_precision = int(rounding_precision)
        except ValueError as val_err:
            raise RCError(
                f"Expected an integer; got: {rounding_precision}"
            ) from val_err

        if rounding_precision not in range(1, 61):
            raise RCError(f"Expected a value between 1–60; got: {rounding_precision}")
