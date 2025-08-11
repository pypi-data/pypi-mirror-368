#!/usr/bin/env python3
"""Argument names and the `Arguments` class."""

import argparse
import datetime as dt
import sys
import textwrap
from typing import Dict, List, Optional

from work.components import consts
from work.components.util import Color

NAME = "work"

# Commands
# fmt: off
START_NAME =    "start"
STOP_NAME =     "stop"
CANCEL_NAME =   "cancel"
RESUME_NAME =   "resume"
SWITCH_NAME =   "switch"
ADD_NAME =      "add"
STATUS_NAME =   "status"
HOURS_NAME =    "hours"
LIST_NAME =     "list"
VIEW_NAME =     "view"
EXPORT_NAME =   "export"
EDIT_NAME =     "edit"
REMOVE_NAME =   "remove"
RECESS_NAME =   "free-days"

CONFIG_NAME =   "config"
REHASH_NAME =   "rehash"
MAINTENANCE_NAMES = [CONFIG_NAME, REHASH_NAME]
# fmt: on


class Mode:
    """Definition of a 'mode', such as `work start`."""

    def __init__(
        self,
        name: str,
        help_text: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        self.names = [name]
        self.help = help_text
        self.description = description or help_text
        self.parents: List[argparse.ArgumentParser] = []

    def add_aliases(self, aliases: List[str]) -> None:
        """Add alternative names ("aliases") to this mode."""
        self.names.extend(aliases)

    def add_as_parser(self, subparsers) -> argparse.ArgumentParser:
        """
        Add this mode to the subparsers action as a new mode parser and
        return the created parser object.
        """
        aliases = self.names[1:] if len(self.names) > 1 else []
        return subparsers.add_parser(
            self.names[0],
            aliases=aliases,
            help=self.help,
            description=self.description,
            parents=self.parents,
        )

    def create_fish_completion(self, all_modes: List[str]) -> str:
        """Convert given arguments to fish completion."""
        for field in ["help", "description"]:
            if self.__dict__[field]:
                self.__dict__[field] = self.__dict__[field].replace('"', '\\"')

        # Right now, we intentionally ignore aliases.
        return (
            f"complete --command {NAME}"
            f' --arguments "{" ".join(self.names)}"'
            f' --description "{self.help or self.description or ""}"'
            f' --condition "not __fish_seen_subcommand_from {" ".join(all_modes)}"'
        )


MODES: Dict[str, Mode] = {
    START_NAME: Mode(START_NAME, help_text="Start work"),
    STOP_NAME: Mode(STOP_NAME, help_text="Stop work"),
    ADD_NAME: Mode(ADD_NAME, help_text="Add a log entry"),
    SWITCH_NAME: Mode(
        SWITCH_NAME,
        help_text="Short-hand for stop & start",
        description=(
            "Short-hand for stop & start. Can be used to log two adjacent entries "
            "with a differing category or message. Category and message are passed "
            "to stop, meaning they refer to the stopped run."
        ),
    ),
    CANCEL_NAME: Mode(CANCEL_NAME, help_text="Cancel the current run"),
    RESUME_NAME: Mode(
        RESUME_NAME, help_text='Resume the last run today (undo "work stop")'
    ),
    STATUS_NAME: Mode(STATUS_NAME, help_text="Print the current status"),
    HOURS_NAME: Mode(HOURS_NAME, help_text="Calculate hours worked"),
    LIST_NAME: Mode(
        LIST_NAME,
        help_text="List work records",
        description=(
            "List work records (by default the current day)."
            " For other ranges use the optional arguments."
        ),
    ),
    VIEW_NAME: Mode(
        VIEW_NAME,
        help_text="Views on work records",
        description=(
            "Views on work records (by default of the current day). "
            "Similar to list, but groups by aspects other than date."
        ),
    ),
    EXPORT_NAME: Mode(EXPORT_NAME, help_text="Export records as CSV"),
    EDIT_NAME: Mode(
        EDIT_NAME,
        help_text="Edit work records",
        description="Edit work records (by default from the current day)",
    ),
    REMOVE_NAME: Mode(
        REMOVE_NAME,
        help_text="Remove records from the log",
        description="Remove records from the log (by default from the current day)",
    ),
    RECESS_NAME: Mode(
        RECESS_NAME,
        help_text="Manage free days (vacation, holidays, part-time days)",
        description="Manage free days (vacation, holidays, part-time days). Default mode: --list",
    ),
    CONFIG_NAME: Mode(
        CONFIG_NAME, help_text="Check and interact with the configuration"
    ),
    REHASH_NAME: Mode(
        REHASH_NAME, help_text="Recompute verification checksum after manual edits"
    ),
}


class Arguments:
    """Allows creating parsers or completions."""

    @staticmethod
    def inject_aliases(alias_mapping: Dict[str, List[str]]) -> None:
        """Inject aliases into modes. Ensures that the parser recognizes configured
        aliases and that they are printed in the help output."""
        for mode, aliases in alias_mapping.items():
            MODES[mode].add_aliases(aliases)

    @staticmethod
    def substitute_macros(macros_mapping: Dict[str, str]) -> None:
        """Replace any detected macros in `sys.argv` with the value(s) provided in
        the given mapping."""
        for macro, replacement in macros_mapping.items():
            if macro not in sys.argv:
                continue

            macro_index = sys.argv.index(macro)
            if any(
                # Check if there is a valid mode argument before the macro
                mode in sys.argv and sys.argv.index(mode) < macro_index
                for mode in MODES
            ):
                # Do not raise. A macro name may overlap an argument name or value,
                # in which case the macro is "found" when that value is passed.
                continue

            sys.argv[macro_index : macro_index + 1] = replacement.split(" ")

    @staticmethod
    def create_argparser(program) -> argparse.ArgumentParser:
        """Create an `ArgumentParser` instance and return it."""

        parser = argparse.ArgumentParser(
            prog=NAME,
            description="Time tracking with an interaction model inspired by Git.",
            epilog="To find out more, check the help page of individual modes.",
        )
        # fmt: off
        parser.add_argument("-H", "--help-verbose", action="store_true",
            help="show a longer help output, similar to a man page, and exit")
        parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {consts.VERSION}")
        parser.add_argument("-d", "--debug", action="store_true", help=argparse.SUPPRESS)
        parser.add_argument("-y", "--dry-run", action="store_true", help="only print output")
        # fmt: on

        modes = parser.add_subparsers(
            title="modes", dest="mode", metavar="{start, stop, add, status, list, ...}"
        )

        # Shared help texts
        day_help_text = (
            "Can be a date or name. "
            'For dates, specify at the minimum the day (e.g., "12."), optionally '
            'also month and year ("1.1." or "5.09.19"). '
            'Valid names are "today", "yesterday", and weekdays (e.g., "monday"). '
            'It suffices to specify any unique prefix, e.g.: "to", "Mon", or "su". '
            "Specifying a weekday selects from the past seven days excluding today."
        )

        # TODO Consider if / how the keyword "again" should be documented
        time_help_text = (
            'Either a time (such as "1:20" or "12:1") or "now" for the current time '
            "(rounded)."
        )

        ## Parent parser for optional entry fields ##

        category_message_parent = argparse.ArgumentParser(add_help=False)
        category_message_parent.add_argument(
            "-c",
            "--category",
            metavar="C",
            help=(
                "Categorize the entry. Anything is allowed, but this will be used for "
                "summarization."
            ),
        )
        category_message_parent.add_argument(
            "-m", "--message", metavar="M", help="Free-text description of the entry."
        )

        MODES[STOP_NAME].parents.append(category_message_parent)
        MODES[ADD_NAME].parents.append(category_message_parent)
        MODES[SWITCH_NAME].parents.append(category_message_parent)

        ## Parent parsers for dates ##

        single_date_sel_parent = argparse.ArgumentParser(add_help=False)
        single_date_sel_modes = single_date_sel_parent.add_mutually_exclusive_group()
        multi_date_sel_parent = argparse.ArgumentParser(add_help=False)
        multi_date_sel_modes = multi_date_sel_parent.add_mutually_exclusive_group()

        # The alternative (two disjunct parents) would not allow the exclusivity guarantee
        for date_sel_modes in [single_date_sel_modes, multi_date_sel_modes]:
            date_sel_modes.add_argument(
                "-d",
                "--day",
                metavar="DAY",
                help=(f"Any DAY – {day_help_text}"),
            )
            date_sel_modes.add_argument(
                "-1",
                "--yesterday",
                action="store_const",
                dest="day",
                const="yesterday",
                help="Short-hand for --day yesterday.",
            )
        multi_date_sel_modes.add_argument(
            "-p",
            "--period",
            metavar="DAY",
            nargs=2,
            help="A specified period, defined by two DAYs.",
        )
        multi_date_sel_modes.add_argument(
            "-s",
            "--since",
            metavar="DAY",
            help="The period between DAY and today.",
        )
        multi_date_sel_modes.add_argument(
            "-w",
            "--week",
            metavar="W",
            type=int,
            nargs="?",
            const=-1,
            help="The current week (no argument) or week no. W of this year.",
        )
        multi_date_sel_modes.add_argument(
            "-m",
            "--month",
            metavar="DAY",
            nargs="?",
            const="today",
            help="The current month (no argument) or the month containing DAY.",
        )

        # Single date selection
        MODES[ADD_NAME].parents.append(single_date_sel_parent)
        MODES[EDIT_NAME].parents.append(single_date_sel_parent)
        MODES[REMOVE_NAME].parents.append(single_date_sel_parent)

        # Multi date selection
        MODES[LIST_NAME].parents.append(multi_date_sel_parent)
        MODES[VIEW_NAME].parents.append(multi_date_sel_parent)
        MODES[EXPORT_NAME].parents.append(multi_date_sel_parent)

        # SINGLE TIME modes

        start_mode = MODES[START_NAME].add_as_parser(modes)
        start_mode.set_defaults(func=program.start)
        start_mode.add_argument(
            "--force",
            action="store_true",
            help="Start anew even if a run is already active.",
        )

        stop_mode = MODES[STOP_NAME].add_as_parser(modes)
        stop_mode.set_defaults(func=program.stop)
        stop_mode.add_argument(
            "--force",
            action="store_true",
            help="Stop even if the new entry would overlap an existing one.",
        )

        # start / stop have a single time argument
        for single_time_mode in [start_mode, stop_mode]:
            single_time_mode.add_argument("time", metavar="TIME", help=time_help_text)

        # DOUBLE TIME modes

        add_mode = MODES[ADD_NAME].add_as_parser(modes)
        add_mode.set_defaults(func=program.add)
        add_mode.add_argument(
            "time_from", metavar="TIME", help="Start time. " + time_help_text
        )
        add_mode.add_argument(
            "time_to", metavar="TIME", help="End time. " + time_help_text
        )
        add_mode.add_argument(
            "--force",
            action="store_true",
            help=(
                "Add even if an existing entry overlaps. "
                "This can result in three outcomes: The old entry will be... "
                "(1) subsumed (removed). "
                "(2) cut (shortened) to make space. "
                "(3) split in two parts, which are then cut (see 2)."
            ),
        )

        switch_mode = MODES[SWITCH_NAME].add_as_parser(modes)
        switch_mode.set_defaults(func=program.switch)
        switch_mode.add_argument(
            "time",
            metavar="TIME",
            help=("The time to switch runs at. TIME: " + time_help_text),
        )
        switch_modifier = switch_mode.add_mutually_exclusive_group()
        switch_modifier.add_argument(
            "-s",
            "--start",
            metavar="TIME",
            help="Instead of restarting immediately, start the next run at TIME.",
        )
        switch_modifier.add_argument(
            "--stop",
            action="store_true",
            help="Do not restart after stopping.",
        )
        switch_mode.add_argument(
            "--force",
            action="store_true",
            help="Pass --force to stop and start.",
        )

        # STATE dependent modes

        cancel_mode = MODES[CANCEL_NAME].add_as_parser(modes)
        cancel_mode.set_defaults(func=program.cancel)

        resume_mode = MODES[RESUME_NAME].add_as_parser(modes)
        resume_mode.set_defaults(func=program.resume)
        resume_mode.add_argument(
            "--force",
            action="store_true",
            help="Resume even if a run is active.",
        )

        status_mode = MODES[STATUS_NAME].add_as_parser(modes)
        status_mode.set_defaults(func=program.status)
        status_mode.add_argument(
            "-o", "--oneline", action="store_true", help="Print status in one line."
        )

        hours_mode = MODES[HOURS_NAME].add_as_parser(modes)
        hours_mode.set_defaults(func=program.hours)
        hours_mode.add_argument(
            "-u",
            "--until",
            metavar="H:M",
            dest="h_until",
            help="Also show the hours that will have been worked at the given time.",
        )
        hours_target = hours_mode.add_mutually_exclusive_group()
        hours_target.add_argument(
            "-t",
            "--target",
            metavar="H:M",
            dest="h_target",
            help="Also show the end time for a workday of the specified length in "
            + "hours:minutes.",
        )
        hours_target.add_argument(
            "-8",
            "--eight",
            action="store_const",
            dest="h_target",
            const="8",
            help="Short-hand for --target 8.",
        )
        hours_balance = hours_mode.add_mutually_exclusive_group()
        hours_balance.add_argument(
            "-b",
            "--for-balance",
            metavar="H[:M][+]",
            dest="h_balance_target",
            help=(
                "Also show the end time for the given target balance in hours:minutes. "
                "Target balance is assumed to be undertime; append the postfix '+' for "
                'overtime targets, e.g. "2+"'
            ),
        )
        hours_balance.add_argument(
            "-d",
            "--workday",
            action="store_const",
            dest="h_balance_target",
            const="0",
            help="Short-hand for --balance-target 0.",
        )
        # Modifiers
        hours_mode.add_argument(
            "-p",
            "--pause",
            metavar="H:M",
            dest="h_pause",
            help="Assume for all calculations that work will be paused hours:minutes.",
        )
        hours_mode.add_argument(
            "-s",
            "--start",
            metavar="H:M",
            dest="h_start",
            help=(
                "Override the start time assumed by hours. May only be used when no "
                "run is active."
            ),
        )

        # PROTOCOL interaction modes

        list_mode = MODES[LIST_NAME].add_as_parser(modes)
        list_mode.set_defaults(func=program.list_entries)
        list_mode.add_argument(
            "-e", "--list-empty", action="store_true", help="Include empty days."
        )
        list_mode.add_argument(
            "-i",
            "--include-active",
            action="store_true",
            help="Include the active run.",
        )
        list_mode.add_argument(
            "-b", "--with-breaks", action="store_true", help="Also show break lengths."
        )
        list_mode.add_argument(
            "-t",
            "--only-time",
            action="store_true",
            help="Only show record times and omit all optional record attributes.",
        )

        view_mode = MODES[VIEW_NAME].add_as_parser(modes)
        view_mode.set_defaults(func=program.view)
        view_mode.add_argument(
            "mode",
            help=(
                "View mode. by-category summarizes based on category instead of date. "
                "balance shows balance development over time."
            ),
            choices=["by-category", "balance"],
        )

        for listing_mode in [list_mode, view_mode]:
            # Note: The order of the flags is intentionally "reversed" (long - short),
            # as the "short flag" is actually a long flag.
            listing_mode.add_argument(
                "--filter-category",
                "--Fc",
                metavar="PATTERN",
                help=(
                    "Filter: Only include records with matching category. Supports "
                    "glob patterns. Filtering is case-insensitive, except if the "
                    "search term includes at least one capital letter ('smart case')."
                ),
            )
            listing_mode.add_argument(
                "--filter-message",
                "--Fm",
                metavar="PATTERN",
                help="Filter: Like --filter-category, but for the message.",
            )

        export_mode = MODES[EXPORT_NAME].add_as_parser(modes)
        export_mode.set_defaults(func=program.export)
        export_mode.add_argument(
            "format",
            help=("Export format. Note: Only csv includes all stored record data."),
            choices=["csv", "tng"],
        )

        edit_mode = MODES[EDIT_NAME].add_as_parser(modes)
        edit_mode.set_defaults(func=program.edit)

        remove_mode = MODES[REMOVE_NAME].add_as_parser(modes)
        remove_mode.set_defaults(func=program.remove)

        for selection_mode in [edit_mode, remove_mode]:
            selection_skip = selection_mode.add_mutually_exclusive_group()
            selection_skip.add_argument(
                "--all",
                action="store_const",
                dest="selection_skip",
                const="all",
                help="Skip selection and directly select all entries.",
            )
            selection_skip.add_argument(
                "--last",
                action="store_const",
                dest="selection_skip",
                const="last",
                help="Skip selection and directly select the last entry.",
            )

        # RECESS management

        recess_mode = MODES[RECESS_NAME].add_as_parser(modes)
        recess_mode.set_defaults(func=program.recess)
        recess_mode_modes = recess_mode.add_mutually_exclusive_group()
        recess_mode_modes.add_argument(
            "--add-vacation",
            nargs="+",
            metavar="DAY",
            help="Add a vacation. Either a single day or a begin and end. DAY: "
            + day_help_text,
        )
        recess_mode_modes.add_argument(
            "--add-holiday",
            metavar="DAY",
            help="Add a holiday on DAY (see DAY).",
        )
        recess_mode_modes.add_argument(
            "--add-reduced-day",
            nargs=2,
            metavar=("DAY", "HOURS"),
            help=(
                "Add a reduced hour day on DAY (see DAY) with HOURS being a value in "
                "({}, {}).".format(*consts.ALLOWED_WORK_HOURS)
            ),
        )
        recess_mode_modes.add_argument(
            "--remove", nargs="+", metavar="DAY", help="Remove free day(s)."
        )
        recess_mode_modes.add_argument(
            "--list",
            metavar="YEAR",
            type=int,
            nargs="?",
            const=dt.date.today().year,
            help="List free days of YEAR (default: current year)",
        )

        # MAINTENANCE modes

        config_mode = MODES[CONFIG_NAME].add_as_parser(modes)
        config_mode.set_defaults(func=program.config)
        config_mode_modes = config_mode.add_mutually_exclusive_group()
        config_mode_modes.add_argument(
            "-p",
            "--path",
            action="store_true",
            help="Default mode: Print the path of the runtime configuration file.",
        )
        config_mode_modes.add_argument(
            "--default",
            action="store_true",
            help="Print the content of the default runtime configuration.",
        )
        config_mode_modes.add_argument(
            "--see",
            choices=["dir", "expected-hours", "aliases", "macros"],
            help="Check how work is configured.",
        )

        rehash_mode = MODES[REHASH_NAME].add_as_parser(modes)
        rehash_mode.set_defaults(func=program.rehash)

        return parser

    @staticmethod
    def print_verbose_help(parser: argparse.ArgumentParser) -> None:
        """Print the parser's help with more detailed help below it."""

        parser.print_help()

        two_spaces: str = " " * 2

        def fill(text: str):
            return textwrap.fill(
                text,
                width=80,
                initial_indent=two_spaces,
                subsequent_indent=two_spaces,
                replace_whitespace=False,
                drop_whitespace=False,
            )

        def new_epilog(title: str, content: List[str]):
            return "\n\n" + title + ":\n" + "\n".join(map(fill, content))

        print("\n\n" + Color.bold("EXTENDED HELP"), end="")

        # fmt: off
        print(
            new_epilog(
                title="rounding",
                content=[
                    "Times are rounded in your favor, to the next full 15 minutes, when "
                        'you enter "now" instead of an exact time. For example:',
                    '- "work start now" at 10:14 starts at 10:00',
                    '- "work stop now" at 19:01 stops at 19:15',
                    'To override the rounding mode, use the keywords "now+", "now-", or '
                        '"now!", which coerce rounding up, down, or prevent rounding, '
                        "respectively."
                ],
            )
            + new_epilog(
                title="expected hours",
                content=[
                    "For some sub-functions (mainly status and hours), you will be nudged to work "
                        "no more, but also no less, than the expected hours. By default, work will "
                        "expect 8 hours for every workday (Mon–Fri). Change the default by editing "
                        "the run-time configuration. To define individual days where less hours "
                        "should be expected, use the free-days command:",
                    '- "free-days --add-vacation" for vacations (expect 0 hours)',
                    '- "free-days --add-holiday" for public holidays (expect 0 hours)',
                    '- "free-days --add-reduced-day" for part-time days (expect < 8 hours)',
                ],
            )
            + new_epilog(
                title="balance",
                content=[
                    "Based on the expected hours and the time worked, two balances are "
                        "calculated:",
                    '1) Week balance (shown in "status"): Total over-/undertime accumulated over '
                        "the current week (starting Monday), up to the day before today.",
                    '2) Current balance (shown in "hours"): This shows the hours you need to work '
                        "on the current day and how many are remaining.",
                    'To check your balance development over other periods, use "view balance".'
                ],
            )
        )
        # fmt: on
