"""Temporary migration code between program versions."""

import textwrap
from typing import Dict, Optional

from work.components import dt_parse
from work.components.protocols import IFlags, IMigratable
from work.components.timestamps import Timestamp
from work.components.util import Color

# <MIGRATE-midnight> Added in v1.1, to be removed in v1.3 #


def offer_midnight_migration_if_not_denied(flags: IFlags, dao: IMigratable):
    """Hint at migrate functionality if that was not denied."""
    migration_flag: str = "migrate:records_touching_midnight"
    if flags.is_set(migration_flag):
        return

    # If no entries are stored yet, this migration does not make sense.
    # Notable example: First run
    if dao.protocol_empty():
        flags.set(migration_flag)
        return

    print(
        textwrap.indent(
            "\nNote: work now handles runs that end at or extend beyond midnight.\n\n"
            "If you have previously worked around the missing functionality by\n"
            "ending runs at, e.g., 23:59, they can be automatically migrated.\n\n",
            prefix="  ",
        )
        + (
            "Press [Enter] to ask again on next startup,\n"
            'Enter "deny" to permanently disable this message, or\n'
            'Enter "migrate" to start migration.\n'
        )
    )
    user_says: str = input("> ").strip().casefold()
    if user_says == "deny":
        flags.set(migration_flag)
        return
    elif user_says != "migrate":
        print("Deferred.")
        return

    # User has requested migration
    print(
        "\nMigration requested.\n\n"
        "Please enter the "
        + Color.bold("earliest end time")
        + " that should be considered.\nMeaning, entries that end "
        + Color.bold("on or after")
        + " that time will be extended\nto end at midnight (24:00) instead.\n"
    )
    selected_time: Optional[Timestamp] = None
    while selected_time is None:
        try:
            selected_time = dt_parse.parse_time_str(input("> ").strip())
        except ValueError as val_err:
            # Print error and retry
            print(Color.color("Parse error", Color.RED) + ":" + str(val_err))
            pass
        # Force retry if time is not in a reasonable time frame (23:30–23:59)
        if selected_time and (
            selected_time < Timestamp(23, 30) or selected_time > Timestamp(23, 59)
        ):
            selected_time = None
            print(
                Color.color("Implausible value", Color.ORANGE)
                + ": Enter a time in [23:30, 23:59]"
            )

    print(f"\nSelected bound: ≥ {selected_time.hour:0>2}:{selected_time.minute:0>2}\n")
    dao.migrate_records_touching_midnight(selected_time)
    flags.set(migration_flag)


def noop_records_midnight() -> None:
    """Mark migration of entries that touched midnight."""


# To be kept #


def print_whats_new_in(version: str, flags: IFlags):
    """Print 'what's new' message for given version."""
    whatsnew_messages: Dict[str, Dict[str, str]] = {
        "0": {
            "100": """Configurable aliases and macros
Configuration file location moved to match XDG Base Directory Specification
Force rounding with arguments "now+", "now-", or prevent with "now!"
Improved listing of free days in "free-days --list" """,
        },
        "1": {
            "0": """New name on PyPI: work-time-log is now work!
Skip interactive selection (edit, remove) with --all or --last
Filtering applies smart case
Day names and dates can be used interchangeably
Flags --date and -D are deprecated""",
            "1": """Entries can now cover midnight – try end time "24:00" or "1:30"!
Multi-day entries can be added by entering hours ≥ 24; e.g. "add 22 25"
Hours calculation ("hours") and entry listing ("list") handle multi-day runs
Force stop / switch with "--force" to add an entry that overlaps a stored one
Vacation days that would overlap a stored holiday can be interactively removed""",
        },
    }

    major, minor, *_ = version.split(".")
    if major not in whatsnew_messages or minor not in whatsnew_messages[major]:
        return

    message_shown_flag: str = f"whatsnew:{major}.{minor}"
    if flags.is_set(message_shown_flag):
        return
    flags.set(message_shown_flag)

    print(
        f"work has been upgraded to version {major}.{minor}!\n\n"
        "Here's a summary of what's new:"
    )
    print(textwrap.indent(whatsnew_messages[major][minor], "  - "))
    print("\nRead more: https://vauhoch.zett.cc/work/releases/\n")
