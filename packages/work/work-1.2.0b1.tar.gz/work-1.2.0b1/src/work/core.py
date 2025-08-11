#!/usr/bin/env python3

import datetime as dt
import pathlib
import sys
from collections import defaultdict, namedtuple
from dataclasses import dataclass
from itertools import chain, cycle, islice
from typing import (
    Callable,
    Collection,
    DefaultDict,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    cast,
)

import work.components.dt_format as dt_format
import work.components.timestamps as ts
from work.components import consts, dt_parse, migrate, util
from work.components.arguments import (
    ADD_NAME,
    MAINTENANCE_NAMES,
    START_NAME,
    STOP_NAME,
    SWITCH_NAME,
    Arguments,
)
from work.components.consts import (
    DIRECTORY,
    DIRECTORY_DEBUG,
    FLAG_FILE,
    FLAG_FILE_DEBUG,
    RC_FILE,
)
from work.components.container import (
    OverlapError,
    ProtocolDay,
    ProtocolMeta,
    Record,
    ShadowProtocolDay,
    sort_and_merge,
)
from work.components.dao import env
from work.components.dao.core import WorkDao
from work.components.dao.flags import Flags
from work.components.dao.rc import RC
from work.components.dao.recess import Holiday, RecessDao, ReducedHourDay, Vacation
from work.components.dt_format import DATE_FORMAT, DATE_FORMAT_FULL, TIME_FORMAT
from work.components.export import Exporter
from work.components.util import Color, PrinTable

__version__: str = consts.VERSION

assert sys.version_info >= (3, 8)


class Work:
    """Main class"""

    # Allow external access to debug flag independent of instance
    debug: bool = False

    def __init__(self):
        """Initialize instance variables and load the RC."""
        self.base_dir: pathlib.Path
        self.dao: WorkDao
        self.recess_dao: RecessDao
        self.configuration: RC
        self.flags: Flags
        self.dry_run: bool = False

        # Load environment variables
        Work.debug = env.get_bool(consts.ENV_DEBUG)

        # Load and check configuration (may raise)
        self.configuration = RC()

    def _connect(self, base_dir: pathlib.Path) -> None:
        """Connect the DAOs."""
        self.dao = WorkDao(base_dir)
        self.recess_dao = RecessDao(base_dir)

    def main(self) -> None:
        """Main program flow."""

        # Aliases and macros
        Arguments.inject_aliases(self.configuration.aliases)
        Arguments.substitute_macros(self.configuration.macros)

        # Argument parsing
        parser = Arguments.create_argparser(program=self)
        args = parser.parse_args()

        if args.help_verbose:
            Arguments.print_verbose_help(parser)
            sys.exit(0)

        # For lack of a required=True argument
        if args.mode is None:
            parser.print_help()
            sys.exit(2)

        # Debug flag can be set in environment or via arguments
        Work.debug = Work.debug or args.debug

        if Work.debug:
            print("\n\n" + Color.color("   ! Debug mode active !", Color.RED) + "\n\n")

        # Dry run flag can only be set via arguments
        self.dry_run = args.dry_run

        if self.dry_run:
            print(">>> Dry run: Only output <<<")

        # Load flags (no checks)
        flag_file: pathlib.Path = FLAG_FILE if not Work.debug else FLAG_FILE_DEBUG
        no_set_flags: bool = env.get_bool(consts.ENV_NO_SET_FLAGS)
        self.flags = Flags(flag_file, no_set_flags)

        # Connect DAO with normal or debug dir and load RC file
        self.base_dir = DIRECTORY if not Work.debug else DIRECTORY_DEBUG
        self._connect(base_dir=self.base_dir)

        # Only verify the protocol and state for non-maintenance modes
        if args.mode not in MAINTENANCE_NAMES:
            self.run_checks()

        # Print "what's new" message once for each release
        migrate.print_whats_new_in(__version__, self.flags)

        # Offer to migrate entries
        migrate.offer_midnight_migration_if_not_denied(self.flags, self.dao)

        args.func(args)

    def run_checks(self) -> None:
        """
        Run all integrity checks. May exit if deemed necessary or requested by the user.
        """
        self.dao.ensure_protocol_integrity()
        # Restore the state if erroneous.
        self.fix_state()

    def fix_state(self) -> None:
        """
        Fix a possibly invalid state. Exits if an invalid state is detected.
        Currently only checks for a lingering active run.
        """

        # Lingering active run: Started yesterday and running for more than 8 hours
        active_start: Optional[dt.datetime] = self.dao.get_start_time()
        if (
            active_start is None
            or active_start.date() == dt.date.today()
            or self._minutes_active_run() <= (8 * 60)
        ):
            return

        # Probably forgot to stop a run – prevent surprises when trying to switch or add
        print(
            "Invalid state detected!\n  A run started at "
            f"{dt_format.readable_dt(active_start)} is still active.\n"
        )

        # Read input, strip and lower
        user_says: str = (
            input(
                "Press [Enter] to end the run and add it to log, or\n"
                'Enter "cancel" to cancel it.\n\n> '
            )
            .strip()
            .lower()
        )

        if user_says == "cancel":
            self.dao.cancel_run()
        else:
            self._collect_input_to_fix_state(active_start)

        print("\nState fixed. Retrying...")
        # Checks should now pass
        self.run_checks()

    def _collect_input_to_fix_state(self, active_start: dt.datetime):
        """Prompt the user to add data to end their forgotten run."""

        time_str: str = input(
            "End time? (H[:M]; enter hours > 24 for times after midnight): "
        )
        # If the string is not parseable, this will raise an exception
        parsed_time: ts.Timestamp = dt_parse.parse_time_str(time_str)
        end_time: dt.datetime = parsed_time.combined(active_start)

        category: str = input("Category? (leave empty for none): ")
        message: str = input("Message?  (leave empty for none): ")
        run_length: float = self._stop(
            end_time=end_time, category=category, message=message
        )
        print(
            f"Stopped work at {dt_format.readable_dt(end_time)} "
            f"({self._timedelta_str(run_length)} recorded)"
        )

    ### Argument parsing / Step two ###

    def get_single_time(self, args) -> dt.datetime:
        """Resolve the single time argument (start, stop, switch)."""

        allowed_modes: Dict[str, List[str]] = dict()
        # Also add aliases for the modes, as they are not replaced on the command line.
        for mode in [START_NAME, STOP_NAME, SWITCH_NAME]:
            allowed_modes[mode] = [mode] + self.configuration.aliases.get(mode, [])

        # `chain.from_iterable()` joins together iterables in an iterable.
        if args.mode not in chain.from_iterable(allowed_modes.values()):
            raise ValueError("Expecting start, stop, or switch mode!")

        time_arg = args.time

        # start and stop do not allow a date other than today
        baseline_date: dt.date = dt.date.today()
        rounding_mode: dt_parse.RoundingMode = dt_parse.RoundingMode.DOWN
        if args.mode in allowed_modes[STOP_NAME]:
            rounding_mode = dt_parse.RoundingMode.UP

        # Only start should understand "again"
        if args.mode in allowed_modes[START_NAME] and time_arg == "again":
            entries_today: List[Record] = self.dao.get_entries(date=dt.date.today())
            if not entries_today:
                raise ValueError(
                    'The keyword "again" only works if at least one entry was recorded today.'
                )
            last_entry_ends: dt.datetime = entries_today[-1].end
            assert last_entry_ends.date() == dt.date.today()
            return last_entry_ends

        single_time: dt.datetime = dt_parse.resolve_time_argument(
            argument=time_arg, baseline_date=baseline_date, rounding_mode=rounding_mode
        )

        return single_time

    def get_time_from_and_to(
        self, args, baseline_date: dt.date
    ) -> Tuple[dt.datetime, dt.datetime]:
        """Resolve the from and to time arguments."""

        if args.mode not in [ADD_NAME, SWITCH_NAME]:
            raise ValueError("Expecting add or switch mode!")

        # Add and pause work in reverse: when adding / pausing with "now now" at 12:50, we
        # expect it to resolve to "12:45 13:00", not to "12:50 12:50" or "13:00 12:45".
        from_rounding_mode = dt_parse.RoundingMode.DOWN
        to_rounding_mode = dt_parse.RoundingMode.UP

        time_from: dt.datetime = dt_parse.resolve_time_argument(
            argument=args.time_from,
            baseline_date=baseline_date,
            rounding_mode=from_rounding_mode,
        )
        time_to: dt.datetime = dt_parse.resolve_time_argument(
            argument=args.time_to,
            baseline_date=baseline_date,
            rounding_mode=to_rounding_mode,
        )

        return (time_from, time_to)

    def get_selected_date(self, args) -> dt.date:
        """
        Evaluate the args to find the selected date -- for single day selection modes
        (add, edit, remove).

        Modes:
        - --day V       : Parse specified date (including --yesterday) or weekday
        - (no input)    : Today
        """

        if args.day:
            return dt_parse.resolve_day_argument(argument=args.day)

        # No date given – use today
        return dt.date.today()

    def get_selected_period(self, args) -> List[dt.date]:
        """
        Evaluate the args to find the selected days -- for multi day selection modes
        (list, view, export).

        Multi selection (handled here):
        - --period X Y  : A period defined by two dates
        - --since X     : Equivalent to --period X today
        - --week        : Current week
        - --month       : Current month

        Single selection (delegated to `get_selected_days_single()`):
        - --day
        - (no input)
        """

        if args.since:
            args.period = (args.since, dt.date.today().strftime(DATE_FORMAT))

        if args.period:
            period_start, period_end = [
                dt_parse.resolve_day_argument(x) for x in args.period
            ]
            return util.get_period(period_start=period_start, period_end=period_end)

        if args.month:
            parsed_date: dt.date = dt_parse.resolve_day_argument(argument=args.month)
            return self._containing_month(day=parsed_date)

        if args.week:
            return self._containing_week(week_no=args.week)

        # Single selection modes are delegated
        return [self.get_selected_date(args=args)]

    ### Modes ###

    # start #

    def start(self, args) -> None:
        """Start the protocol based on the given arguments."""

        start_time: dt.datetime = self.get_single_time(args)
        self._start(start_time=start_time, force=args.force)
        print(f"Started work at {dt_format.readable_t(start_time, dt.date.today())}")

    def ensure_valid_start_time(
        self,
        start_time: dt.datetime,
        action: str = "start work",
        time_desc: str = "starting time",
    ) -> None:
        """Check if a run could be started with the given start time.
        Raises `InvalidOperationWarning` if not."""

        if self.dao.has_entry(start_time=start_time):
            raise InvalidOperationWarning.cant(
                action, f"an existing record overlaps with the specified {time_desc}"
            )

        # Check left side: May start as early as desired, as long as it's today.
        if start_time.date() < dt.date.today():
            raise InvalidOperationWarning.cant(action, f"{time_desc} needs to be today")

        # Check right side: May start only a few minutes early.
        # Explicitly allowed to be on the following day (including 24:00 / 00:00)!
        ten: float = 10
        if start_time > (dt.datetime.now() + dt.timedelta(minutes=ten)):
            raise InvalidOperationWarning.cant(
                action, f"{time_desc} may not be more than {ten} minutes in the future"
            )

    def _start(self, start_time: dt.datetime, force: bool = False) -> None:
        """
        Start the protocol with the given start time.

        force: If a run is active, overwrite it silently.
        """

        if not force and self.dao.run_active():
            raise InvalidOperationWarning.cant(
                "start work", "a run is still active (add --force to override)"
            )

        self.ensure_valid_start_time(start_time=start_time)

        if not self.dry_run:
            self.dao.start_run(start_time, force=force)

    # stop #

    def stop(self, args) -> None:
        """Stop the protocol based on the given arguments."""
        end_time: dt.datetime = self.get_single_time(args)
        run_length: float = self._stop(
            end_time=end_time,
            category=args.category,
            message=args.message,
            force=args.force,
        )
        print(
            f"Stopped work at {dt_format.readable_dt(end_time)} "
            f"({self._timedelta_str(run_length)} recorded)"
        )

    def _stop(
        self, end_time: dt.datetime, category: str, message: str, force: bool = False
    ) -> float:
        """Stop the protocol with the given end time.
        Returns the recorded run length in minutes."""

        start_time: Optional[dt.datetime] = self.dao.get_start_time()

        if start_time is None:
            raise InvalidOperationWarning.cant(
                "stop work", "no run is currently active"
            )

        if end_time == start_time:
            self.dao.cancel_run()
            raise InvalidOperationWarning(
                "End time is identical to start time – run cancelled."
            )

        self._can_i_add_this(
            start_time=start_time, end_time=end_time, operation="stop work", force=force
        )

        # Preconditions met: Run can be stopped.
        if not self.dry_run:
            self.dao.stop_run(
                end_time=end_time, category=category, message=message, force=force
            )
        return util.minutes_difference(start=start_time, end=end_time)

    # add #

    def add(self, args) -> None:
        """Add a protocol entry consisting of start time, end time and optional date flag."""

        start_time: dt.datetime
        end_time: dt.datetime
        baseline_date: dt.date = self.get_selected_date(args)
        start_time, end_time = self.get_time_from_and_to(args, baseline_date)

        self._can_i_add_this(
            start_time=start_time,
            end_time=end_time,
            operation="add entry",
            force=args.force,
        )

        if not self.dry_run:
            self.dao.add_protocol_entry(
                start_time=start_time,
                end_time=end_time,
                category=args.category,
                message=args.message,
                force=args.force,
            )

        formatted_start: str = start_time.strftime(TIME_FORMAT)
        # We specifically do not use ts.date_equals, as this also applies to midnight.
        if start_time.date() != end_time.date():
            formatted_start = dt_format.readable_dt(start_time)
        print(
            "Added a record from {} to {}".format(
                formatted_start, dt_format.readable_dt(end_time)
            )
        )

    def _can_i_add_this(
        self,
        start_time: dt.datetime,
        end_time: dt.datetime,
        operation: str,
        force: bool = False,
    ) -> None:
        """
        Shared checks for valid start and end time of a run.
        Raises InvalidOperationWarning if not.
        """

        if (
            error := self.dao.invalid_start_and_end_error(start_time, end_time)
        ) is not None:
            raise InvalidOperationWarning.cant(operation, error)

        if not force and self.dao.has_entry(start_time=start_time, end_time=end_time):
            raise InvalidOperationWarning.cant(
                operation,
                "an existing record overlaps with the specified time (add --force to override)",
            )

    # switch #

    def switch(self, args) -> None:
        """
        Switch based on the given arguments. Convenience function for stop + start.

        Two functions:
        - switch A B -> stop at time A, start at B (e.g. after taking a break)
        - switch A -> stop at A and immediately start again (e.g. after switching tasks)
        """

        switch_time: dt.datetime = self.get_single_time(args)

        # If --stop is specified, only stop
        if args.stop:
            return self.stop(args)

        # If not specified otherwise, restart immediately at switch time.
        restart_time: dt.datetime = switch_time
        if args.start:
            restart_time = dt_parse.resolve_time_argument(
                args.start, dt.date.today(), rounding_mode=dt_parse.RoundingMode.DOWN
            )

        run_length: float = self._switch(
            switch_time=switch_time,
            restart_time=restart_time,
            category=args.category,
            message=args.message,
            force=args.force,
        )

        def readable_switch_time(time: dt.datetime) -> str:
            return dt_format.readable_t(time, base=dt.date.today())

        if not args.start:
            print(
                f"Switched work at {readable_switch_time(switch_time)} "
                f"({self._timedelta_str(run_length)} recorded)"
            )
        else:
            print(
                "Stopped work at {} ({} recorded) and restarted at {}".format(
                    switch_time.strftime(TIME_FORMAT),
                    self._timedelta_str(run_length),
                    readable_switch_time(restart_time),
                )
            )

    def _switch(
        self,
        switch_time: dt.datetime,
        restart_time: dt.datetime,
        category: str,
        message: str,
        force: bool,
    ) -> float:
        """
        Switch tasks at the given time points.

        `category` and `message` will be added to the stopped run.

        Returns the recorded run length in minutes.
        """

        active_run_start: Optional[dt.datetime] = self.dao.get_start_time()
        if active_run_start is None:
            raise InvalidOperationWarning.cant("switch", "no run is currently active")

        if active_run_start == switch_time:
            switch_time_identical: str = (
                "Switch time is identical to the start time of the active run"
            )
            if switch_time == restart_time:
                raise InvalidOperationWarning(f"{switch_time_identical} – did nothing.")

            raise InvalidOperationWarning(
                f"{switch_time_identical}, but restart time differs. To "
                'move the start time, use "start --force".\nDid nothing.'
            )

        if switch_time > restart_time:
            raise InvalidOperationWarning.cant(
                "switch", "specified stop time needs to lie before the restart time"
            )

        if active_run_start > switch_time:
            raise InvalidOperationWarning.cant(
                "switch", "end / switch time lies before the active run's start time"
            )

        self.ensure_valid_start_time(
            start_time=restart_time, action="switch", time_desc="restart time"
        )

        # Stop at the beginning of the pause, restart at the end of the pause
        run_length: float = self._stop(
            end_time=switch_time, category=category, message=message, force=force
        )
        self._start(start_time=restart_time, force=force)
        return run_length

    # cancel #

    def cancel(self, args) -> None:
        """Cancels the current run."""

        if not self.dao.run_active():
            print("No active run")
            return

        if not self.dry_run:
            self.dao.cancel_run()
        print("Run cancelled")

    # resume #

    def resume(self, args) -> None:
        """Resumes the last run."""

        if not args.force and self.dao.run_active():
            raise InvalidOperationWarning.cant(
                "resume run", "a run is currently active (add --force to override)"
            )

        protocol: ProtocolMeta = self.dao.get_container(dt.date.today())
        records_today: List[Record] = list(protocol.entries)

        if not records_today:
            raise InvalidOperationWarning.cant(
                "resume run", "no records stored for today"
            )

        last_today: Record = records_today[-1]
        if not self.dry_run:
            protocol.remove(record=last_today)
            self.dao.update_info_file()

        print(f"Record {last_today.strftime(TIME_FORMAT)} removed. Resuming...")
        self._start(start_time=last_today.start, force=args.force)

    # status #

    def status(self, args) -> None:
        """Print the current status."""

        today: dt.date = dt.date.today()
        active_start: Optional[dt.datetime] = self.dao.get_start_time()
        minutes_protocol, minutes_active_run = self._total_minutes_worked()

        output: str

        if active_start is None:
            output = "Inactive"
        elif active_start > dt.datetime.now():
            output = (
                Color.color("Scheduled", Color.BLUE)
                + f" to start work at {dt_format.readable_dt(active_start)}"
            )
        else:
            output = Color.color("Active", Color.BLUE) + " since {} ({})".format(
                dt_format.readable_dt(active_start),
                self._timedelta_str(minutes_active_run),
            )

        if args.oneline:
            print(output)
            return

        total_minutes_worked = minutes_protocol + minutes_active_run
        entries_today: List[Record] = self.dao.get_entries(date=today)
        output += (
            "\n> " + self._timedelta_str(total_minutes_worked) + " worked until now – "
        )
        if minutes_protocol > 0:
            num: int = len(entries_today)
            output += "{} {} on record".format(num, "entry" if num == 1 else "entries")
        else:
            output += "nothing on record"
        if entries_today:
            # We assume the entries are sorted by time in ascending order.
            output += (
                f"\n> Last entry ends at {entries_today[-1].end.strftime('%H:%M')}"
            )

        def new_section(title: str):
            return f"\n\n{title}:"

        def new_section_line():
            return "\n\t"

        # How many hours are we expected to work?
        output += new_section("Workweek status")

        # Delta until (including) yesterday – a negative delta represents overtime
        delta_yesterday: float = self._minute_balance_up_to(day=today)
        minutes_expected: float = self._minutes_per_day(day=today)

        minutes_to_work: float = minutes_expected + delta_yesterday

        minutes_left_today: float = minutes_to_work - total_minutes_worked
        minutes_left_delta_str: str = self._timedelta_str(abs(minutes_left_today))

        output += new_section_line()

        if minutes_left_today <= 0:
            done_msg = "Done"
            if minutes_left_today < 0:
                done_msg += " (" + minutes_left_delta_str + " over)"
            output += Color.color(done_msg, Color.GREEN)
        else:
            prospective_start: dt.datetime = self._prospective_start(active_start)
            work_until: dt.datetime = prospective_start + dt.timedelta(
                minutes=minutes_to_work - minutes_protocol
            )
            output += "{} left (until {})".format(
                minutes_left_delta_str, work_until.strftime(TIME_FORMAT)
            )

            output += new_section_line() + "Week balance: "
            if delta_yesterday == 0:
                output += Color.color("On time", Color.GREEN)
            else:
                # _timedelta_str() only allows positive arguments
                time_str: str = self._timedelta_str(abs(delta_yesterday))
                if delta_yesterday > 0:
                    output += Color.color(time_str + " undertime", Color.ORANGE)
                elif delta_yesterday < 0:
                    output += Color.color(time_str + " overtime", Color.GREEN)

        if (associated_recess := self.recess_dao.get_recess_for(today)) is not None:
            recess_name: str = {  # pyright: ignore[reportArgumentType]
                Vacation: "vacation day",
                Holiday: "holiday",
                ReducedHourDay: "reduced hour day",
            }[type(associated_recess)]
            output += new_section_line()
            output += (
                f"Note: {recess_name.capitalize()} "
                + f"({self._timedelta_str(minutes_expected)} expected)"
            )

        print(output)

    # hours #

    def hours(self, args):
        """Print the hours worked until a specified time or related things."""

        today: dt.date = dt.date.today()
        minutes_logged, minutes_active_run = self._total_minutes_worked()

        def new_section():
            return "\n> "

        header: str = "{} on record, {} active run".format(
            self._timedelta_str(minutes_logged),
            self._timedelta_str(minutes_active_run) if self.dao.run_active() else "no",
        )

        minutes_to_work: float = self._minutes_to_work_today()
        balance_message = self._get_day_balance_msg(
            minutes_to_work=minutes_to_work,
            total_minutes_worked=minutes_logged + minutes_active_run,
        )
        header += f" | {balance_message}"

        ## Optional modes

        optional_output: str = ""

        start_time: Optional[dt.datetime] = self.dao.get_start_time()

        # prospective_start | Either start_time or "now" (rounded)
        prospective_start: dt.datetime = self._prospective_start(start_time)

        start_argument: bool = args.h_start is not None
        if start_argument:
            # Time calculation incorporates minutes worked in the active run so far.
            # Therefore, we can't override the active run start time.
            if start_time is not None:
                raise InvalidOperationWarning(
                    "Flag --start may only be used if no run is active"
                )
            prospective_start = dt_parse.resolve_time_argument(
                args.h_start,
                baseline_date=dt.date.today(),
                rounding_mode=dt_parse.RoundingMode.NONE,
            )

        # worked_towork_split | The time where the worked_minutes end.
        #                       By default, we base on the prospective start time.
        #                       If a run was started in the past, worked_minutes
        #                       includes the minutes up to now, so we have to remove
        #                       those by basing on _dt_now_stripped().
        worked_towork_split: dt.datetime = prospective_start
        if start_time is not None and start_time < dt.datetime.now():
            worked_towork_split = self._dt_now_stripped()

        # If requested by the user, an extra pause is added to the calculation.
        extra_pause_minutes: float = 0.0
        if args.h_pause:
            pause_hours, pause_minutes = dt_parse.parse_time_period_str(args.h_pause)
            extra_pause_minutes = pause_minutes + 60 * pause_hours

        hours_data: Work.HoursData = Work.HoursData(
            minutes_logged=minutes_logged,
            minutes_active_run=minutes_active_run,
            minutes_to_work_today=minutes_to_work,
            prospective_start=prospective_start,
            run_active=start_time is not None,
            start_argument=start_argument,
            worked_towork_split=worked_towork_split,
            extra_pause_minutes=extra_pause_minutes,
        )

        # For multi-day runs, the output time counts the complete active run, even
        # though that run will only partially be logged on the current day.
        if args.h_until:
            target: dt.datetime = dt_parse.resolve_time_argument(
                argument=args.h_until,
                baseline_date=today,
                rounding_mode=dt_parse.RoundingMode.UP,
            )

            # Verify input correctness
            if target.date() < today or target < prospective_start:
                raise InvalidOperationWarning(
                    "The target time supplied to --until needs to be after the "
                    f"(prospective) start time {dt_format.readable_dt(prospective_start)}."
                )

            optional_output += new_section()
            optional_output += self._get_hours_worked_until_msg(
                target_time=target, hours_data=hours_data
            )

        # Calculate the end time to achieve the given target hours today.
        if args.h_target:
            target_hours, target_minutes = dt_parse.parse_time_period_str(args.h_target)

            target_hours_data = hours_data

            # For multi-day runs, we only count the minutes worked *today*
            if start_time is not None and start_time.date() < dt.date.today():
                pretend_start_time = dt.datetime.combine(dt.date.today(), dt.time())
                pretend_minutes_active_run = util.minutes_difference(
                    start=pretend_start_time, end=self._dt_now_stripped()
                )
                target_hours_data = Work.HoursData(
                    minutes_logged=hours_data.minutes_logged,
                    minutes_active_run=pretend_minutes_active_run,
                    minutes_to_work_today=hours_data.minutes_to_work_today,
                    prospective_start=hours_data.prospective_start,
                    run_active=hours_data.run_active,
                    start_argument=hours_data.start_argument,
                    worked_towork_split=hours_data.worked_towork_split,
                    extra_pause_minutes=hours_data.extra_pause_minutes,
                )

            optional_output += new_section()
            optional_output += self._get_target_end_time_msg(
                target_hours=target_hours,
                target_minutes=target_minutes,
                hours_data=target_hours_data,
            )

        # Calculate the remaining hours for a full workday (respecting the week balance)
        if args.h_balance_target:
            # Parse balance target and classify into over-/undertime
            balance_target: str = args.h_balance_target
            target_is_overtime: bool = False
            if args.h_balance_target.endswith("+"):
                balance_target = util.remove_suffix(balance_target, "+")
                target_is_overtime = True
            target_hours, target_minutes = dt_parse.parse_time_period_str(
                balance_target
            )

            optional_output += new_section()
            optional_output += self._get_balance_target_end_time_msg(
                balance_target=target_minutes + target_hours * 60,
                target_is_overtime=target_is_overtime,
                hours_data=hours_data,
            )

        # If any of the above routines have added to the output, we need a note.
        note_str: str = ""
        warning_str: str = ""
        if optional_output:
            assumption_str: str
            assumption_str, warning_str = self._build_hours_assumption_str(
                hours_data=hours_data
            )
            note_str = "\n\n{}:".format(assumption_str) if assumption_str else ""
            warning_str = f"\n{warning_str}" if warning_str else ""

        print(f"{header}{note_str}{optional_output}{warning_str}")

    def _prospective_start(self, start_time: Optional[dt.datetime]):
        """Return prospective start for hours calculation.

        If start_time is not None, it is simply returned. Otherwise, assume a run is
        started with argument "now" and return the according start time."""
        if start_time is not None:
            return start_time

        return dt_parse.resolve_time_argument(
            argument="now",
            baseline_date=dt.date.today(),
            rounding_mode=dt_parse.RoundingMode.DOWN,
        )

    @dataclass
    class HoursData:
        """Storage container for data used in hours sub-functions."""

        minutes_logged: float
        minutes_active_run: float
        minutes_to_work_today: float
        prospective_start: dt.datetime
        run_active: bool
        start_argument: bool
        worked_towork_split: dt.datetime
        extra_pause_minutes: float

        @property
        def total_minutes_worked(self) -> float:
            """Return the sum of the logged minutes and the active run minutes."""
            return self.minutes_logged + self.minutes_active_run

    def _get_hours_worked_until_msg(self, target_time, hours_data):
        # type: (dt.datetime, Work.HoursData) -> str
        """Compute and stringify the worked hours at a given target time."""

        minutes_from_now: float = (
            target_time - hours_data.worked_towork_split
        ) / dt.timedelta(minutes=1)
        total_minutes: float = hours_data.total_minutes_worked + minutes_from_now

        if hours_data.extra_pause_minutes > 0:
            total_minutes -= hours_data.extra_pause_minutes

        remaining_minutes_until: float = (
            hours_data.minutes_to_work_today - total_minutes
        )

        return (
            f"You will have worked {self._timedelta_str(minutes=total_minutes)} "
            f"at target time {target_time.strftime(TIME_FORMAT)}. "
            f"| Balance then: {self._balance_readable(remaining_minutes_until)}"
        )

    def _get_target_end_time_msg(self, target_hours, target_minutes, hours_data):
        # type: (int, int, Work.HoursData) -> str
        """Compute and stringify the status towards a given time target."""

        target_time: str = f"{target_hours}:{target_minutes:0>2}"
        target_minutes += target_hours * 60

        return self._get_end_time_msg(
            target_minutes=target_minutes,
            hours_data=hours_data,
            target_explainer=f"for a {target_time} hour day",
            completed_msg=(
                f"Target of {target_time} hours {Color.color('achieved', Color.GREEN)}!"
            ),
        )

    def _get_balance_target_end_time_msg(
        self, balance_target, target_is_overtime, hours_data
    ):
        # type: (float, bool, Work.HoursData) -> str
        """
        Compute and stringify the end time for a full workday, respecting the current
        week balance.
        """

        minutes_today: float = self._minutes_per_day(day=dt.date.today())
        minute_balance_up_to_today: float = self._minute_balance_up_to(
            day=dt.date.today()
        )
        target_minutes: float = minutes_today + minute_balance_up_to_today

        # Shift minutes target based on targeted balance (negative for undertime)
        if not target_is_overtime:
            balance_target *= -1
        target_minutes += balance_target

        # Simplify message if balance target is zero
        completed_msg: str = f"Workday {Color.color('finished', Color.GREEN)}!"
        target_explainer: str = "for a full workday"
        if balance_target != 0:
            completed_msg = f"Balance target {Color.color('achieved', Color.GREEN)}!"
            target_explainer = "for your balance target"

        return self._get_end_time_msg(
            target_minutes=target_minutes,
            hours_data=hours_data,
            target_explainer=target_explainer,
            completed_msg=completed_msg,
        )

    def _get_end_time_msg(
        self, target_minutes, hours_data, target_explainer, completed_msg
    ):
        # type: (float, Work.HoursData, str, str) -> str
        """
        Compute the end time for a day of the specified hours.
        Returns: Compiled message for printing.
        """

        # If the expected hours were already reached before this run, we can immediately return.
        if hours_data.minutes_logged >= target_minutes:
            return completed_msg

        delta_minutes: float = target_minutes - hours_data.total_minutes_worked

        if hours_data.extra_pause_minutes > 0:
            delta_minutes += hours_data.extra_pause_minutes

        # If a run was started in the past, worked_minutes includes the minutes up to now,
        # so we have to calculate the end from _dt_now_stripped().
        prospective_end: dt.datetime = hours_data.worked_towork_split
        prospective_end += dt.timedelta(minutes=delta_minutes)

        # The end time might lie on the next day. Then, the target is unachievable.
        if prospective_end.date() != dt.date.today():
            return "Given target hours can't be completed anymore today!"

        # End time has already been reached
        if prospective_end <= self._dt_now_stripped():
            return completed_msg

        # End time not yet reached

        remaining_minutes_then: float = (
            hours_data.minutes_to_work_today - target_minutes
        )

        message: str = (
            f"Work until {prospective_end.strftime(TIME_FORMAT)} "
            f"{target_explainer.strip()}. "  # explainer, such as "for a 7 hour day"
            f"| Balance then: {self._balance_readable(remaining_minutes_then)}"
        )

        return message

    def _get_day_balance_msg(
        self, minutes_to_work: float, total_minutes_worked: float
    ) -> str:
        """Compute and stringify the week balance including the current workday,
        taking into account all worked hours."""

        remaining_minutes: float = minutes_to_work - total_minutes_worked
        message: str = "Current balance: "

        balance_readable: str = self._balance_readable(remaining_minutes)
        message += balance_readable

        mtw_timedelta, mtw_sign = self._timedelta_str_signed(minutes_to_work)
        mtw_prefix: str = "" if minutes_to_work >= 0 else f"{mtw_sign} "
        return f"{message} ({mtw_prefix}{mtw_timedelta} to work today)"

    def _balance_readable(self, remaining_minutes: float) -> str:
        """Create a readable string explaining the balance, i.e. remaining minutes."""
        remaining_timedelta: str = self._timedelta_str(abs(remaining_minutes))
        rm_postfix: str = "remaining" if remaining_minutes > 0 else "overtime"
        if remaining_minutes == 0:
            return "+/- 0"
        return f"{remaining_timedelta} {rm_postfix}"

    def _build_hours_assumption_str(self, hours_data):
        # type: (Work.HoursData) -> Tuple[str, str]
        """
        Build a string describing assumptions used in the calculation.

        Returns: assumption_str, warning_str
        """

        # Assumptions
        assumption_str: str = ""

        start_time_strf: str = hours_data.prospective_start.strftime("%H:%M")
        if hours_data.start_argument:
            assumption_str += f"you start at {start_time_strf}"
        elif not hours_data.run_active:
            assumption_str += f"you start now ({start_time_strf})"

        if hours_data.extra_pause_minutes > 0:
            if len(assumption_str) > 0:
                assumption_str += " and"
            else:
                assumption_str += "you"
            pause_str: str = self._timedelta_str(hours_data.extra_pause_minutes)
            assumption_str += f" take {pause_str} of breaks"

        if len(assumption_str) > 0:
            assumption_str = f"Assuming {assumption_str}"

        # Simple warning for overlaps – if any run lies in the future, warn.
        warning_str: str = ""
        if self.dao.has_entry(
            start_time=hours_data.prospective_start,
            end_time=dt.datetime.combine(dt.date.today(), dt.time(23, 59)),
        ):
            warning_str = (
                "Warning: A logged run overlaps the current period, which could "
                "make the calculation invalid. Please check for overlaps manually."
            )

        return assumption_str, warning_str

    # list #

    def list_entries(self, args) -> None:
        """List protocol entries."""
        selected_days: List[dt.date] = self.get_selected_period(args)
        self._list(
            days=selected_days,
            list_empty=args.list_empty,
            include_active=args.include_active,
            print_breaks=args.with_breaks,
            only_time=args.only_time,
            filter_category=args.filter_category,
            filter_message=args.filter_message,
        )

    def _list(
        self,
        days: List[dt.date],
        list_empty: bool,
        include_active: bool,
        print_breaks: bool,
        only_time: bool,
        filter_category: Optional[str] = None,
        filter_message: Optional[str] = None,
    ) -> None:
        """Print the given list of dates. For more than one date: Print a summary."""

        if not days:
            raise ValueError("At least one element is required")

        active_start: Optional[dt.datetime] = self.dao.get_start_time()
        # This variable stores two properties: whether to include the active run (if
        # it is set or not) and the dates to include (which values it contains)
        include_active_days: List[dt.date] = []
        if active_start is not None and include_active:
            include_active_days = [
                active_day
                for active_day in util.get_period(active_start.date(), dt.date.today())
                if active_day in days
            ]
            if not include_active_days:
                raise InvalidOperationWarning.cant(
                    "list the active run",
                    because="the selected period doesn't cover it",
                )

        output: List[str] = []
        total_includes_active_run: bool = False

        total_number_of_records: int = 0
        total_minutes_worked: float = 0.0
        for day in days:
            records: List[Record] = self.dao.get_entries(date=day)

            active_run_to_include: Optional[Record] = None
            # Only include the active run (segment) if requested and it covers this day.
            if day in include_active_days:
                active_start = cast(dt.datetime, active_start)
                zero_o_clock = dt.time(hour=0, minute=0)
                # Only add minutes that cover the listed day
                active_run_to_include = Record(
                    # If started before this day, we only include the time from midnight
                    start=max(dt.datetime.combine(day, zero_o_clock), active_start),
                    # The fictional end time is chosen to be...
                    end=min(
                        max(  # now (default) or start (future run) - run started this day
                            self._dt_now_stripped(), active_start
                        ),
                        # or midnight of the listed day, if the other options are later
                        dt.datetime.combine(day + dt.timedelta(days=1), zero_o_clock),
                    ),
                )

            # Filter entries based on passed filter parameters
            records = self.filter_records(
                records, filter_category=filter_category, filter_message=filter_message
            )

            if len(records) == 0 and not list_empty and active_run_to_include is None:
                continue

            output_lines = self._evaluate_day(
                day=day,
                records=records,
                print_breaks=print_breaks,
                only_time=only_time,
                active_run_to_include=active_run_to_include,
            )
            total_number_of_records += len(records)
            output.extend(output_lines)
            output.append("")
            total_minutes_worked += self._minutes_worked(records)

            # If we want to include the active run and it is today, add those minutes.
            if active_run_to_include is not None:
                total_minutes_worked += active_run_to_include.get_minutes()
                total_includes_active_run = True

        # Add info if no result (when omitting empty records)
        if not output:
            output.append(self._none_found_msg(days))
        # Remove empty last line if no summary is added
        elif len(days) <= 1:
            output = output[:-1]
        # Add summary if more than one element
        else:
            output.append(
                Color.bold(
                    "Total: {} records{}, {} worked".format(
                        total_number_of_records,
                        " (+ active run)" if total_includes_active_run else "",
                        self._timedelta_str(total_minutes_worked),
                    )
                )
            )

        for line in output:
            print(line)

    @staticmethod
    def filter_records(
        records: List[Record],
        filter_category: Optional[str],
        filter_message: Optional[str],
    ) -> List[Record]:
        """Filter the list of records based on category and message."""
        catfilter: str = filter_category or "*"
        msgfilter: str = filter_message or "*"

        filtered_records: List[Record] = []
        for record in records:
            category_matched: bool = util.fnmatch_smartcase(record.category, catfilter)
            message_matched: bool = util.fnmatch_smartcase(record.message, msgfilter)
            if category_matched and message_matched:
                filtered_records.append(record)
        return filtered_records

    def _evaluate_day(
        self,
        day: dt.date,
        records: List[Record],
        print_breaks: bool,
        only_time: bool,
        active_run_to_include: Optional[Record] = None,
    ) -> List[str]:
        """
        Produce a list of output strings describing the records stored on the given day.
        Return the output list as well as the number of records.

        :param print_breaks: If true, intertwine the break times with the listed entries.
        :param only_time: If true, omit optional record fields from output.
        :param active_start_to_include: If given, the "active run" will be added to the output.
        """

        if active_run_to_include is not None and active_run_to_include.date != day:
            raise ValueError("Invalid day for active_start_to_include passed.")

        # Add the year to the printout if it's not the current year
        date_fmt: str = dt_format.date_fmt(day)

        # Merge entries for only_time
        record_count: int = len(records)
        if only_time:
            for i in range(len(records)):  # pylint: disable=consider-using-enumerate
                records[i] = Record(start=records[i].start, end=records[i].end)
            records = sort_and_merge(entries=records, output=False)

        result: List[str] = []
        result.append(
            "{: <3}, {}: {} records{}{}".format(
                day.strftime("%a"),
                day.strftime(date_fmt),
                record_count,
                (
                    f" (merged to {len(records)})"
                    if only_time and len(records) != record_count
                    else ""
                ),
                " (+ active run)" if active_run_to_include is not None else "",
            )
        )

        if active_run_to_include is not None:
            # Check and warn if active run would overlap the listed entries
            for other in records:
                if active_run_to_include.overlaps(other):
                    raise InvalidOperationWarning.cant(
                        "list active run", "it overlaps with an already stored entry"
                    )
                if other.start >= active_run_to_include.start:
                    raise InvalidOperationWarning.cant(
                        "list active run",
                        "you have logged a future run, which is an undefined case",
                    )

            records.append(active_run_to_include)

        total_minutes: float = 0.0
        total_break_minutes: float = 0.0
        prin_table: PrinTable = PrinTable()

        for i, record in enumerate(records):
            minutes: float = record.get_minutes()
            total_minutes += minutes
            row: List[str] = [
                f"{record.strftime(TIME_FORMAT)}",
                f" | {self._timedelta_str(minutes)}",
            ]

            # Add optional attributes
            if not only_time:
                category: str = f"  ({record.category})" if record.category else " "
                message: str = f' "{record.message}"' if record.message else " "
                row.extend([category, message])

            prin_table.add_row(row)

            # Add break info after all but the last entry
            if print_breaks:
                break_str, break_length = self._break_str(records, i)
                total_break_minutes += break_length
                if break_length > 0:
                    prin_table.add_row(["", Color.color(break_str, Color.GRAY)])

        # Replace time of active run with start time only, colored in blue.
        if active_run_to_include is not None:
            active_run_row: List[str] = prin_table.rows.pop()
            active_run_time_str: str = active_run_to_include.strftime(TIME_FORMAT)
            # active_run_time_str = active_run_time_str.replace("–", "~")
            # Do not print the end time if the listed day is today, which covers the
            # fictional 'end' of the active run (now)
            if ts.date_equals(day, dt.date.today()):
                assert len(active_run_time_str) == 13 and " – " in active_run_time_str
                active_run_time_str = active_run_time_str[:-7] + "~      "
            active_run_row[0] = Color.color(active_run_time_str, Color.BLUE)
            prin_table.add_row(active_run_row)

        for printable_row in prin_table.printable_str():
            result.append(printable_row)

        if len(records) > 0:
            result[0] = Color.bold(result[0])
            result.append(" " * 13 + f" = {self._timedelta_str(minutes=total_minutes)}")
            if print_breaks:
                result[-1] = result[-1] + Color.color(
                    f" (+ {self._timedelta_str(total_break_minutes)} of breaks)",
                    Color.GRAY,
                )

        return result

    @staticmethod
    def _none_found_msg(selected_days: List[dt.date]) -> str:
        """Create a message that no entry was found, matching the given day selection."""
        none_found_msg: str = "No records found"
        # Single day
        if len(selected_days) == 1:
            none_found_msg += " on " + selected_days[0].strftime(DATE_FORMAT_FULL)
        # Continuous period (each two consecutive list elements are directly adjacent days)
        elif all(
            selected_days[i - 1] == selected_days[i] - dt.timedelta(days=1)
            for i in range(1, len(selected_days))
        ):
            none_found_msg += " for the period from {} to {}".format(
                selected_days[0].strftime(DATE_FORMAT),
                selected_days[-1].strftime(DATE_FORMAT),
            )
        else:
            none_found_msg += " for the selected days:\n{}".format(
                ", ".join([d.strftime(DATE_FORMAT) for d in selected_days])
            )
        return none_found_msg

    def _break_str(self, records: List[Record], i: int) -> Tuple[str, float]:
        """Create a break string for the given row. Skips last row."""
        if i == len(records) - 1:
            return "", 0

        break_length: float = util.minutes_difference(
            start=records[i].end, end=records[i + 1].start
        )

        if break_length == 0:
            return "", 0
        return f" ~ {self._timedelta_str(break_length)} break", break_length

    # view #

    def view(self, args) -> None:
        """View protocol entries by attributes."""

        selected_days: List[dt.date] = self.get_selected_period(args)
        selected_records: List[Record] = list(
            chain(*[self.dao.get_entries(day) for day in selected_days])
        )
        filtered_records: List[Record] = self.filter_records(
            records=selected_records,
            filter_category=args.filter_category,
            filter_message=args.filter_message,
        )

        total_minutes_worked: float = self._minutes_worked(records=filtered_records)
        output: List[str] = []

        # Mode selection

        # View by category
        if args.mode == "by-category":
            if not filtered_records:
                print(self._none_found_msg(selected_days))
                return

            view_by_category: List[str] = self.view_by_category(
                records=filtered_records, total_minutes_worked=total_minutes_worked
            )
            output.extend(view_by_category)
        elif args.mode == "balance":
            view_balance: List[str] = self.view_balance(
                period=selected_days, records=filtered_records
            )
            output.extend(view_balance)
        # Unknown mode
        else:
            raise RuntimeError(f"Mode {args.mode} encountered, but not understood.")

        for line in output:
            print(line)

    def view_by_category(
        self, records: List[Record], total_minutes_worked: float
    ) -> List[str]:
        """Create a view for the given protocol records by category."""

        result: List[str] = []
        records_by_category: DefaultDict[str, List[Record]] = defaultdict(list)
        for record in records:
            records_by_category[record.category].append(record)
        num_categories: int = len(records_by_category.keys())
        if "" in records_by_category:
            # Caution: If any access on the dict with this key is made before, an empty
            # list will have been created, which would lead to problems below.
            if len(records_by_category[""]) == 0:
                raise RuntimeError("Invalid state of internal dict encountered.")
            num_categories -= 1

        table_data: List[Tuple[str, int, float]] = []
        for category, cat_records in records_by_category.items():
            table_data.append(
                (category, len(cat_records), self._minutes_worked(records=cat_records))
            )

        prin_table: PrinTable = PrinTable(padding="  ")
        prin_table.add_row(
            [Color.bold(x) for x in ["category", "hours", "%", "records"]]
        )
        prin_table.add_line("-")

        for category, num_of_records, minutes_worked in sorted(
            table_data, key=lambda i: i[2], reverse=True
        ):
            row: List[str] = [
                "{}".format(category if category != "" else "∅"),
                f"{self._timedelta_str(minutes_worked)}",
                "{:<3.0%}".format(minutes_worked / total_minutes_worked),
                f"{num_of_records}",
            ]
            prin_table.add_row(row)

        prin_table.add_line("-")
        prin_table.add_row(
            [
                Color.bold("Total"),
                Color.bold(f"{self._timedelta_str(total_minutes_worked)}"),
                "",
                Color.bold(f"{len(records)}"),
            ]
        )

        for printable_row in prin_table.printable_str():
            result.append(printable_row)
        return result

    def view_balance(self, period: List[dt.date], records: List[Record]) -> List[str]:
        """Create a view of the balance development over the given records."""

        if not util.is_continuous_period(period):
            raise NotImplementedError("Expecting continuous period!")

        filtered_records_by_day: Dict[dt.date, List[Record]] = defaultdict(list)
        for record in records:
            filtered_records_by_day[record.date].append(record)

        date_buckets = Work.DateBuckets(period=period)
        bucket_selector = date_buckets.to_selector
        BucketData = namedtuple("BucketData", ["expected", "worked"])
        buckets_data: Dict[str, BucketData] = defaultdict(lambda: BucketData(0.0, 0.0))

        total_expected: float = 0.0
        total_worked: float = 0.0
        total_balance: float = 0.0

        for day in period:
            days_records: List[Record] = filtered_records_by_day[day]
            minutes_expected: float = self._minutes_per_day(day)
            minutes_worked: float = self._minutes_worked(days_records)

            total_expected += minutes_expected
            total_worked += minutes_worked
            total_balance += minutes_expected - minutes_worked

            stored_expected, stored_worked = buckets_data[bucket_selector(day)]
            buckets_data[bucket_selector(day)] = BucketData(
                expected=stored_expected + minutes_expected,
                worked=stored_worked + minutes_worked,
            )

        # Balance graph: To properly size it, we need the maximum minutes for each side
        typical_expected_max: float = sum(
            # Given the typical expected minutes of a work week, sort them in reverse
            # (largest first) and then cylce and take from the infinite list until
            # <bucket size> elements were retrieved. Finally, sum up. Thereby, we
            # get the "maximum" expected hours for a period of that length.
            islice(
                cycle(sorted(self._expected_minutes(), reverse=True)), date_buckets.size
            )
        )
        max_minutes: float = max(
            chain(
                # maximum expected for a period of that length
                [typical_expected_max],
                # maximum expected this period
                [data.expected for data in buckets_data.values()],
                # maximum deviation from expected (maximum bar size)
                [abs(data.expected - data.worked) for data in buckets_data.values()],
            )
        )

        prin_table: PrinTable = PrinTable(padding="  ")
        date_column_title: str = "Date range"
        if all(len(dates) == 1 for dates in date_buckets.mapped_dates.values()):
            date_column_title = "Date"
        prin_table.add_row(
            [
                Color.bold(x)
                for x in [
                    f"{date_buckets.name.capitalize()}",
                    f"{date_column_title}",
                    "Days",
                    "Expected",
                    "Worked",
                    "Balance graph",
                ]
            ]
        )
        prin_table.add_line("-")
        b_id: str
        b_data: BucketData
        for b_id, b_data in buckets_data.items():
            bucket_name, bucket_range = date_buckets.descriptor(b_id)
            balance_graph: str = self._balance_graph(
                b_data.expected, b_data.worked, max_minutes
            )
            expected_str = self._timedelta_str(b_data.expected)
            worked_str = self._timedelta_str(b_data.worked)
            if b_data.expected == 0.0:
                expected_str = "-"
            if b_data.worked == 0.0:
                worked_str = "-"
            prin_table.add_row(
                [
                    f"{bucket_name}",
                    f"{bucket_range}",
                    f"{len(date_buckets.mapped_dates[b_id])}",
                    expected_str,
                    worked_str,
                    f"{balance_graph}",
                ]
            )
        prin_table.add_line("-")
        prin_table.add_row(
            [
                Color.bold(x)
                for x in [
                    "Total",
                    "",
                    f"{len(period)}",
                    f"{self._timedelta_str(total_expected)}",
                    f"{self._timedelta_str(total_worked)}",
                    f"{self._balance_readable(total_balance)}",
                ]
            ]
        )

        result: List[str] = []
        for printable_row in prin_table.printable_str():
            result.append(printable_row)
        return result

    class DateBuckets:
        """Grouping of `date`s in "buckets" – used in view balance."""

        def __init__(self, period: List[dt.date]) -> None:
            if not util.is_continuous_period(period):
                raise ValueError("DateBuckets requires continuous date period.")
            self._period: List[dt.date] = period
            self.name: str
            self._set_name()

            self.mapped_dates: Dict[str, List[dt.date]]  # contained dates
            self._map_dates()

        def _set_name(self) -> None:
            """Based on the period, set name."""
            self.name = "month"
            if len(self._period) < 7 * 16:
                self.name = "week"
            if len(self._period) < 16:
                self.name = "day"

        def _map_dates(self) -> None:
            """Based on the selector, map the dates to buckets."""
            self.mapped_dates = defaultdict(list)
            for day in self._period:
                self.mapped_dates[self.to_selector(day)].append(day)

        @property
        def size(self) -> int:
            """Return the (maximum) length of each bucket in days."""
            return {
                "day": 1,
                "week": 7,
                "month": 31,
            }[self.name]

        def to_selector(self, given_date: dt.date) -> str:
            """Transform given date to bucket selector."""

            # Handle special case of a week that spans multiple years...
            if (
                self.name == "week"
                and given_date.month == 1
                and given_date.isocalendar()[1] >= 52
            ):
                # ...by always using Monday of that week for the selector.
                given_date -= dt.timedelta(days=given_date.weekday())

            formatter: str = {
                "day": "%Y-%m-%d",
                "week": "%V-%G",
                "month": "%m/%Y",
            }[self.name]
            return given_date.strftime(formatter)

        @property
        def date_format(self) -> str:
            """Date format used, based on the bucket period."""
            date_format: str = "%d.%m."
            if (
                self._period[0].year != self._period[-1].year
                or self._period[0].year != dt.date.today().year
            ):
                date_format += "%y"
            return date_format

        def descriptor(self, bucket_id: str) -> Tuple[str, str]:
            """
            Create a readable "explanation" for the bucket based on content.

            Returns a tuple with (name, date (range)), e.g. ("Mon", "12.01.").
            """
            name_format: str = {
                "day": "%a",
                "week": "w. %V",
                "month": "%b",
            }[self.name]

            bucket_dates: List[dt.date] = self.mapped_dates[bucket_id]
            formatted_dates: str = bucket_dates[0].strftime(self.date_format)
            if len(bucket_dates) > 1:
                assert util.is_continuous_period(bucket_dates)
                formatted_dates += f" – {bucket_dates[-1].strftime(self.date_format)}"

            return (bucket_dates[0].strftime(name_format), formatted_dates)

    @staticmethod
    def _balance_graph(expected: float, worked: float, max_minutes: float) -> str:
        """Create a 2D balance graph to visualize over- or undertime.
        Example: |  ===|     |"""
        side_length: int = 8
        unbroken_side: str = " " * side_length
        ctr: str = "|"
        bar_char: str = "="
        brd: str = "|"

        deviation: float = expected - worked
        percent_deviation: float = abs(deviation / max_minutes)
        if percent_deviation < 0.05:
            return f"{brd}{unbroken_side}{ctr}{unbroken_side}{brd}"

        bar_size: int = int(round(percent_deviation * side_length, 0))
        # pylint: disable=blacklisted-name
        bar: str = bar_size * bar_char
        if deviation < 0:  # overtime to the right
            bar = bar.ljust(side_length, " ")
            result = f"{unbroken_side}{ctr}{bar}"
        else:
            bar = bar.rjust(side_length, " ")
            result = f"{bar}{ctr}{unbroken_side}"
        return f"{brd}{result}{brd}"

    # export #

    def export(self, args) -> None:
        """Export any day or range of days in a chosen format."""
        if not getattr(Exporter, args.format, False):
            raise RuntimeError(f"Formatting option {args.format} not understood")

        selection = {
            date: self.dao.get_entries(date=date)
            for date in self.get_selected_period(args)
        }

        exporter = Exporter(target=sys.stdout, selection=selection)
        if args.format == "csv":
            exporter.csv()
        elif args.format == "tng":
            exporter.tng(self.recess_dao)
        else:
            raise ValueError(f'Unknown export format "{args.format}"')

    # edit + remove #

    def edit(self, args) -> None:
        """Edit protocol entries. Currently supports changing the time."""

        selection = self._start_manipulation_mode(args, "edit")
        if not selection:
            return

        protocol: ProtocolMeta
        selected_records: List[Record]
        protocol, selected_records = selection

        edited: int = 0
        modification_buffer: List[Tuple[Record, Record]] = []

        for record in selected_records:
            print(f"\n > Selected record: {record.strf(TIME_FORMAT)}\n")

            new_start: dt.datetime = self._new_time_or_not("start", record.start)
            new_end: dt.datetime = self._new_time_or_not(
                "end", record.end, base=record.start
            )
            new_category: str = self._new_text_field_or_not("category", record.category)
            new_message: str = self._new_text_field_or_not("message", record.message)
            new_record: Record = Record(new_start, new_end, new_category, new_message)

            if new_record == record:
                print("Unchanged")
                continue

            # Check if the edited entry would overlap the currently active run
            active_start: Optional[dt.datetime] = self.dao.get_start_time()
            if active_start is not None and new_record.overlaps(
                Record.one_minute_record(start=active_start)
            ):
                print()
                raise InvalidOperationWarning.cant(
                    "update entry",
                    f"the new time slot {new_record.strftime(TIME_FORMAT)} overlaps "
                    + f"the run started at {active_start.strftime(TIME_FORMAT)}",
                )

            user_choice = input(
                "Change\n\t{}\nto\n\t{}\n? [Y/n]\n".format(
                    record.strf(TIME_FORMAT), new_record.strf(TIME_FORMAT)
                )
            )
            if user_choice.lower() in ["", "y"]:
                modification_buffer.append((record, new_record))
                edited += 1
                print("Done")
            else:
                print("Skipped")

        # Backup should we need to abort
        protocol = cast(ProtocolDay, protocol)
        shadow: ShadowProtocolDay = ShadowProtocolDay.copy(protocol)

        # Remove all entries we are about to edit to ensure that invalid intermediate
        # states (overlaps that are resolved by other edits) do not occur.
        for record, _ in modification_buffer:
            protocol.remove(record)
        try:
            for _, new_record in modification_buffer:
                protocol.add(new_record)
        except OverlapError as ovl_err:
            # Return state to original state
            shadow.overwrite(protocol)
            raise InvalidOperationWarning(
                "Edits would lead to overlap of the following entries:\n"
                f"  {ovl_err.left.strf(TIME_FORMAT)}\n"
                f"  {ovl_err.right.strf(TIME_FORMAT)}\n"
                "Aborting."
            ) from ovl_err

        # We implement the dry run indirectly, by reverting the changes again.
        if self.dry_run:
            shadow.overwrite(protocol)

        self._end_manipulation_mode(num_edited=edited, verb="edited")

    def _new_time_or_not(
        self, time_name: str, old_val: dt.datetime, base: Optional[dt.date] = None
    ) -> dt.datetime:
        """User interaction: Ask for a new time (or no change)."""

        message = f"New {time_name} time? ({dt_format.readable_t(old_val, base)}) "
        user_choice = input(message)
        if user_choice == "":
            return old_val

        try:
            date_part: dt.date = base or old_val.date()
            new_val = dt_parse.resolve_time_argument(
                argument=user_choice,
                baseline_date=date_part,
                rounding_mode=dt_parse.RoundingMode.NONE,
            )
            if not ts.date_equals(old_val, new_val):
                raise ValueError("New time must lie on the same date (<= 24:00).")
            return new_val
        except ValueError as val_err:
            print(f"{Color.color('Parse error', Color.RED)}: {str(val_err)}")
            return self._new_time_or_not(time_name, old_val)

    def _new_text_field_or_not(self, field_name: str, old_val: str) -> str:
        """User interaction: Ask for a new text field, field removal, or no change."""

        user_choice: str = input(
            f'New {field_name} or remove ["-"]? ({old_val}) '
        ).strip()

        if user_choice == "":
            return old_val
        elif user_choice == "-":
            return ""

        return user_choice

    def remove(self, args) -> None:
        """Remove protocol entries."""

        selection = self._start_manipulation_mode(args, "remove")
        if not selection:
            return

        protocol: ProtocolMeta
        selected_records: List[Record]
        protocol, selected_records = selection

        for record in selected_records:
            protocol.remove(record)

        self._end_manipulation_mode(num_edited=len(selected_records), verb="removed")

    def _start_manipulation_mode(
        self, args, verb: str
    ) -> Optional[Tuple[ProtocolMeta, List[Record]]]:
        """Common functionality for both manipulation modes."""

        date: dt.date = self.get_selected_date(args)
        protocol: ProtocolMeta = self.dao.get_container(date=date)
        records: List[Record] = list(protocol.entries)
        date_str: str = date.strftime(DATE_FORMAT_FULL)

        if not records:
            print(f"No entries on selected date: {date_str}")
            return None

        print(verb.capitalize() + " mode – " + date_str)

        all_indices: List[int] = list(range(len(records)))
        zipped_records: Dict[int, Record] = dict(zip(all_indices, records))

        print()
        for i, record in zipped_records.items():
            print(f"[{i}] {record.strf(TIME_FORMAT)}")
        print()

        selection_skip: str = getattr(args, "selection_skip", "")
        if not selection_skip:
            print(
                f"Enter nothing to cancel, or\n"
                f"Enter one or more indices [{0}..{len(records) - 1}] separated by a space, or\n"
                f'Enter "all" to {verb} all entries, or "last" for the last.\n'
            )

            selected_indices = self._get_user_selection(valid_indices=all_indices)
            if selected_indices is None:
                return None
        else:
            print(f'Interactive selection skipped – selecting "{selection_skip}".')
            # Skip the selection by passing the selection keyword directly.
            selected_indices = self._get_index_selection(
                user_choice=selection_skip, valid_indices=all_indices
            )

        return protocol, [zipped_records[i] for i in selected_indices]

    def _get_user_selection(self, valid_indices: List[int]) -> Optional[List[int]]:
        """Ask the user for a choice from the `valid_indices`. Recursively retries."""

        user_choice: str = input("Which entries? > ")

        if user_choice == "":
            return None

        try:
            return self._get_index_selection(user_choice, valid_indices)
        except IndexError as idx_err:
            print(f" {idx_err}")
            # Recursively retry
            return self._get_user_selection(valid_indices)

    def _get_index_selection(
        self, user_choice: str, valid_indices: List[int]
    ) -> List[int]:
        """
        Match a user input to the chosen indices. Allows 1-many indices or "all".
        Returns list of unique indices sorted in ascending order.

        Raises `IndexError` for invalid selections.
        """

        if user_choice == "all":
            return sorted(set(valid_indices))
        elif user_choice == "last":
            return [max(valid_indices)]

        try:
            selection: Set[int] = {int(u) for u in user_choice.split(" ") if len(u) > 0}
        except ValueError as val_err:
            raise IndexError("Not a number!") from val_err

        if selection.difference(valid_indices):
            raise IndexError("Invalid index chosen!")

        return sorted(selection)

    def _end_manipulation_mode(self, num_edited: int, verb: str) -> None:
        """Print result message, update checksum."""

        print(verb.capitalize() + f" {util.pluralize(num_edited, 'record')}")

        # Only update the checksum if we actually changed something (double-check)
        if num_edited > 0:
            self.dao.update_info_file()

    # recess #

    def recess(self, args) -> None:
        """Manage recess days, a.k.a. vacation days or holidays (add, remove, list)."""

        action: Optional[Callable] = None
        output: str = ""

        if args.add_vacation:
            if len(args.add_vacation) not in [1, 2]:
                raise ValueError("Expects either one or two arguments!")
            action, output = self._recess_add_vacation(args.add_vacation)
        elif args.add_holiday:
            holi_day: dt.date = dt_parse.resolve_day_argument(args.add_holiday)
            action = lambda: self.recess_dao.add_holiday(date=holi_day)  # noqa: E731
            output = f"Added holiday on {holi_day.strftime(DATE_FORMAT)}"
        elif args.add_reduced_day:
            assert len(args.add_reduced_day) == 2
            redu_day: dt.date = dt_parse.resolve_day_argument(args.add_reduced_day[0])
            try:
                hours: float = float(args.add_reduced_day[1])
            except ValueError as val_err:
                raise ValueError(
                    f"Invalid value {args.add_reduced_day[1]} for HOURS; expects float."
                ) from val_err
            action = lambda: self.recess_dao.add_reduced_hour_day(  # noqa: E731
                date=redu_day, hours=hours
            )
            output = (
                f"Added reduced hour day on {redu_day.strftime(DATE_FORMAT)} "
                f"with {hours} hours"
            )
        elif args.remove:
            remove_dates: List[dt.date] = [
                dt_parse.resolve_day_argument(r) for r in args.remove
            ]
            action = lambda: self.recess_dao.remove(dates=remove_dates)  # noqa: E731
            output = (
                f"Removed {', '.join([r.strftime(DATE_FORMAT) for r in remove_dates])}"
            )

        if action is None:
            # Default: List (even if no mode was selected)
            list_year = args.list or dt.date.today().year
            self._list_recess_days(year=list_year)
            return

        if not self.dry_run:
            action()
        print(output)

    def _recess_add_vacation(self, date_args: List[str]) -> Tuple[Callable, str]:
        """Add a vacation for the given period. May be either one or two arguments."""
        assert len(date_args) in [1, 2]

        dates: List[dt.date] = [dt_parse.resolve_day_argument(d) for d in date_args]
        first: dt.date = dates[0]
        last: dt.date = dates[-1]  # may be the same as `first`

        if first > last:
            raise InvalidOperationWarning.cant(
                "add vacation", because="begin date lies after end date"
            )

        vacation_period: List[dt.date] = util.get_period(first, last)

        days_to_remove: List[dt.date] = []
        non_working_in_period: List[dt.date] = []
        holidays_in_period: List[dt.date] = []

        for day in vacation_period:
            if self._is_non_working_day(day):
                non_working_in_period.append(day)

            its_recess = self.recess_dao.get_recess_for(day)
            if isinstance(its_recess, ReducedHourDay):
                return (
                    lambda: None,
                    "Selected period overlaps a reduced hour day. Did nothing.",
                )
            elif isinstance(its_recess, Holiday):
                holidays_in_period.append(day)

        if non_working_in_period:
            user_says: str = input(
                "The vacation overlaps with configured non-working day(s): "
                + ", ".join(
                    [nwip.strftime("%d.%m.%Y (%A)") for nwip in non_working_in_period]
                )
                + "\nShould non-working days be removed from the vacation before it "
                + "is added?\n[Y/n] "
            )
            if user_says.lower().strip() != "n":
                days_to_remove.extend(non_working_in_period)

        if holidays_in_period:
            user_says = input(
                "The vacation overlaps with configured holiday(s): "
                + ", ".join(
                    [hdip.strftime("%d.%m.%Y (%A)") for hdip in holidays_in_period]
                )
                + "\nHolidays must be removed from the vacation before it can be "
                + "added. Remove?\n[Y/n] "
            )
            # Free days cannot overlap, so we do nothing if the holidays are kept.
            if user_says.lower().strip() == "n":
                return lambda: None, "Selected period overlaps a holiday. Did nothing."

            days_to_remove.extend(holidays_in_period)

        # Remove non-working days and/or holidays if requested above
        vacation_period = [day for day in vacation_period if day not in days_to_remove]
        if len(vacation_period) == 0:
            return lambda: None, "No vacation days remained. Did nothing."

        def action():
            self.recess_dao.add_vacation(period=vacation_period)

        if len(date_args) == 1:
            assert first == last
            return action, f"Added vacation on {first.strftime(DATE_FORMAT)}"

        return action, (
            f"Added vacation from {first.strftime(DATE_FORMAT)} "
            f"to {last.strftime(DATE_FORMAT)}"
        )

    def _list_recess_days(self, year: int) -> None:
        """List recess days of the given year."""
        if not self.recess_dao.has_days(year=year):
            print(f"No free days stored for {year}.")
            return

        if holidays := self.recess_dao.get_holidays(year=year):
            print(f"Holidays ({util.pluralize(len(holidays), 'day')}):")
            for holi in holidays:
                print(f"  {holi.date.strftime(DATE_FORMAT)}")
            print()

        if reduced_hour_days := self.recess_dao.get_reduced_hour_days(year=year):
            print(
                f"Reduced hour days ({util.pluralize(len(reduced_hour_days), 'day')}):"
            )
            for redu in reduced_hour_days:
                print(f"  {redu.date.strftime(DATE_FORMAT)} ({redu.hours} hours)")
            print()

        if vacations := self.recess_dao.get_vacations(year=year):
            print(f"Vacations ({util.pluralize(len(vacations), 'day')}):")
            for vaca_period in util.continuous_periods([v.date for v in vacations]):
                formatted_string = "  "
                postfix = ""
                if len(vaca_period) > 1:
                    formatted_string += vaca_period[0].strftime("%d.%m – ")
                    postfix = f" ({len(vaca_period)} days)"
                formatted_string += vaca_period[-1].strftime(DATE_FORMAT)
                print(f"{formatted_string}{postfix}")
            print()

        print(
            f"Total: {len(holidays + reduced_hour_days + vacations)} free days"  # type: ignore
        )

    # rehash #

    def rehash(self, args) -> None:
        """Recompute the info file checksum (after reconfirming)."""
        # pylint: disable=unused-argument

        user_says: str = input(
            "Do you really want to update the verification checksum?\n"
            + "This will validate all possibly erroneous manual edits!\n"
            + "[y/N] "
        )
        if user_says.lower() == "y":
            self.dao.update_info_file()
            print("Checksum updated")
        else:
            print("Cancelled")

    # config #

    def config(self, args) -> None:
        """
        Check and interact with the configuration (RC and hardcoded).
        Formerly `rc()` and `see()`.
        """

        if args.default:
            print(RC.default_rc_content())
            return
        elif args.see:
            self._see(s_target=args.see)
            return

        # Default: Print configuration path
        print(f"{RC_FILE}")

    def _see(self, s_target) -> None:
        """See configuration details."""

        if s_target == "dir":
            print(
                f"Records directory:   {self.dao.records_directory}\n"
                f"Free days directory: {self.recess_dao.directory}\n"
                f"Configuration file:  {RC_FILE}\n"
                f"Flags file:          {FLAG_FILE}"
            )
        elif s_target == "expected-hours":
            for weekday, expected in self.configuration.expected_hours.items():
                print(f"{weekday:<10}: {expected}")
        elif s_target == "aliases":
            for mode, aliases in self.configuration.aliases.items():
                for alias in aliases:
                    print(f"{alias} = {mode}")
        elif s_target == "macros":
            for macro, expansion in self.configuration.macros.items():
                print(f"{macro:<} = {expansion}")
        # When adding a new option, make sure to update the "choices" of the ArgumentParser!
        else:
            raise NotImplementedError(f"Target {s_target} unknown")

    ### Shared functionality ###

    def _minutes_logged_on(self, requested_date: dt.date) -> float:
        """Return the minutes logged on the requested date."""
        the_days_records: List[Record] = self.dao.get_entries(date=requested_date)
        return self._minutes_worked(the_days_records)

    @staticmethod
    def _minutes_worked(records: List[Record]) -> float:
        """Return the summed up work times contained in the given records."""
        return sum(r.get_minutes() for r in records)

    def _minutes_active_run(self) -> float:
        """Return the minutes the current run has been active. Raises if no run is active."""

        active_start: Optional[dt.datetime] = self.dao.get_start_time()
        if active_start is None:
            raise RuntimeError("No active run – can't calculate minutes!")

        minutes_active_run: float = util.minutes_difference(
            start=active_start, end=self._dt_now_stripped()
        )
        # Fixes bug for future start in which case a negative number is returned.
        return max(minutes_active_run, 0)

    def _total_minutes_worked(self) -> Tuple[float, float]:
        """
        Return the total minutes worked today.
        Includes all recorded protocol entries, as well as the current run (if active).
        """

        minutes_protocol = self._minutes_logged_on(requested_date=dt.date.today())
        minutes_active_run: float = 0.0
        active_start: Optional[dt.datetime] = self.dao.get_start_time()
        if active_start is not None:
            minutes_active_run = self._minutes_active_run()

        return minutes_protocol, minutes_active_run

    @staticmethod
    def _timedelta_str(minutes: float) -> str:
        """
        Return a string representing the minutes (e.g. 150.0) as HH:MM (e.g. 2 h 30 m).
         minutes : Positive-valued number of minutes to translate.
        """

        if minutes < 0:
            raise ValueError(
                "Timedelta can only be computed for positive minute values."
            )

        only_hours: int = int(minutes // 60)
        only_minutes: int = int(minutes % 60)
        # Handle the corner case of both rounding down to zero; happens for inputs 0, m < 1
        if only_hours + only_minutes == 0:
            return "0 m"

        hour_part: str = "" if only_hours == 0 else f"{only_hours} h"
        minute_part: str = "" if only_minutes == 0 else f"{only_minutes} m"

        return f"{hour_part} {minute_part}".strip()

    def _timedelta_str_signed(self, minutes: float) -> Tuple[str, str]:
        """Return a timedelta string and its sign. Allows negative values."""

        sign: str = "+"
        if minutes < 0:
            sign = "-"
        timedelta_str: str = self._timedelta_str(abs(minutes))
        return timedelta_str, sign

    def _expected_minutes(self) -> List[float]:
        """Return a list of minutes to work on a regular week.

        Does not consider recess days."""
        normal_hours: Collection[float] = self.configuration.expected_hours.values()
        assert len(normal_hours) == 7
        return [hour * 60.0 for hour in normal_hours]

    def _is_non_working_day(self, day: dt.date) -> bool:
        """Check if the given day is a free day, based only on the configured expected
        hours."""
        return self._expected_minutes()[day.weekday()] == 0

    def _minutes_per_days(self, days: List[dt.date]) -> List[Tuple[dt.date, float]]:
        """Return a list of the minutes to work on the given days. Considers recess days."""

        # This method is the single place where expected hours are calculated.
        # That means that we only need to consider vacations or holidays here.

        result: List[Tuple[dt.date, float]] = []
        normal_minutes: List[float] = self._expected_minutes()

        for day in days:
            # We don't need the list index of the day, but its relative "index" in its week.
            minutes = normal_minutes[day.weekday()]
            # If a day is added twice, this always returns the lowest hour value.
            if (reduced_hours := self.recess_dao.reduced_hours(day)) is not None:
                minutes = reduced_hours * 60.0
            result.append((day, minutes))

        return result

    def _minutes_per_day(self, day: dt.date) -> float:
        """Return the minutes to work on the given day. Considers recess days."""

        mins_per_days = self._minutes_per_days(days=[day])[0]
        _, minutes = mins_per_days
        return minutes

    def _minutes_to_work_today(self) -> float:
        """Calculate the remaining minutes to work today based on the current balance."""
        minutes_to_work: float = self._minutes_per_day(
            day=dt.date.today()
        ) + self._minute_balance_up_to(day=dt.date.today())
        return minutes_to_work

    def _minute_balance(self, week: List[dt.date]) -> float:
        """
        Return the minute balance for the given days.
        Negative delta = Overtime
         week : The list may be shorter than seven elements; then only the first
         len(week) days will be assumed.
        """

        if len(week) > 7:
            raise ValueError("A week has no more than seven days.")

        deltas: List[float] = []

        for day, minutes_expected in self._minutes_per_days(days=week):
            minutes_logged: float = self._minutes_logged_on(requested_date=day)
            deltas.append(minutes_expected - minutes_logged)

        return sum(deltas)

    def _minute_balance_up_to(self, day: dt.date) -> float:
        """
        Return the minute balance for all days in the given day's week, excluding itself.
        Correctly handles Monday and Sunday.
         see: `_minute_balance()`
        """

        week_no: int = day.isocalendar()[1]
        week: List[dt.date] = self._containing_week(week_no=week_no)
        week_up_to: List[dt.date] = week[: week.index(day)]

        return self._minute_balance(week=week_up_to)

    ### Convenience functions ###

    def _dt_now_stripped(self) -> dt.datetime:
        """Return the current time, with seconds and microseconds set to 0."""
        return dt.datetime.now().replace(second=0, microsecond=0)

    @staticmethod
    def _containing_week(week_no: int) -> List[dt.date]:
        """
        Return the week specified by the given week number.

        week: Either a valid week number, or -1 for the current week.
        """

        current_year, current_week, _ = dt.date.today().isocalendar()

        # If -1 is given as a week number, the current week is requested.
        if week_no == -1:
            week_no = current_week

        # The weekday is a 0-6 number for Mon-Sun
        monday: dt.date = dt.date.fromisocalendar(
            year=current_year, week=week_no, day=1
        )
        sunday: dt.date = monday + dt.timedelta(days=6)
        week: List[dt.date] = util.get_period(period_start=monday, period_end=sunday)

        return week

    @staticmethod
    def _containing_month(day: dt.date) -> List[dt.date]:
        """Return the month that contains the given day."""

        first: dt.date = day.replace(day=1)
        # Get a day from the following month
        date_next_month: dt.date = first + dt.timedelta(days=32)
        # 7th - 7 = last of month before
        last = date_next_month - dt.timedelta(days=date_next_month.day)

        return util.get_period(period_start=first, period_end=last)


### Other classes ###


class InvalidOperationWarning(Warning):
    """Warn that an operation cannot be executed due to state or preconditions."""

    # pylint: disable-msg=invalid-name
    @staticmethod
    def cant(do: str, because: str):
        """Produce a warning that `do` is impossible due to `because`."""
        return InvalidOperationWarning(f"Can't {do} – {because}!")
