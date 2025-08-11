#!/usr/bin/env python3

"""Protocol wrappers"""

import atexit
import csv
import datetime as dt
import os
import pathlib
import re
import shutil
import tempfile
from typing import Iterable, List, Optional

import work.components.timestamps as ts
from work.components import util
from work.components.consts import (
    DATETIME_FORMAT,
    DAY_FILE_PATTERN,
    MONTH_DIR_PATTERN,
    PROTOCOL_FILE_EXTENSION,
    TIME_FORMAT,
    YEAR_DIR_PATTERN,
)

### Record container classes ###


class Record:
    """A protocol record. Invariant: start <= end"""

    def __init__(
        self,
        start: dt.datetime,
        end: dt.datetime,
        category: Optional[str] = None,
        message: Optional[str] = None,
    ):
        if start > end:
            raise ValueError("Record start has to lie before its end!")
        if not ts.date_equals(start, end):
            raise ValueError("Record start date has to equal its end date!")
        self._start = start
        self._end = end
        self._category = category.strip() if category else ""
        self._message = message.strip() if message else ""

    @property
    def start(self) -> dt.datetime:
        return self._start

    @property
    def end(self) -> dt.datetime:
        return self._end

    @property
    def date(self) -> dt.date:
        """This record's date. Raises if start date != end date."""
        return ts.single_shared_date(self.start, self.end)

    @property
    def category(self) -> str:
        return self._category

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, new: str) -> None:
        self._message = new

    def get_minutes(self) -> float:
        """Return the total minutes in this record."""
        return util.minutes_difference(start=self.start, end=self.end)

    def overlaps(self, other) -> bool:
        """Check if the given `Record` overlaps this."""
        # Either other starts within us or we start within other. For start, we allow
        # equality (in case of an exact overlap), but for end we don't (touching is
        # not overlapping).
        return (
            self.start <= other.start < self.end
            or other.start <= self.start < other.end
        )

    def touches(self, other) -> bool:
        """Check if the given `Record` touches this."""
        return self.start == other.end or self.end == other.start

    def merge(self, other):
        # type: (Record) -> Record
        """
        Try to merge two records. Can only merge touching or overlapping records that
        are otherwise identical.

        Raises if the merge is unsuccessful.
        """

        if not (self.overlaps(other) or self.touches(other)):
            raise Record.UnmergeableError("Time does not overlap or touch.")

        if not (self.category == other.category and self.message == other.message):
            raise Record.UnmergeableError("Category or message differ.")

        return Record(
            start=min((self.start, other.start)),
            end=max((self.end, other.end)),
            category=self.category,
            message=self.message,
        )

    def to_protocol_row(self) -> List[str]:
        """Create a row for a protocol file from this record."""
        return [
            self.start.strftime(DATETIME_FORMAT),
            self.end.strftime(DATETIME_FORMAT),
            self.category,
            self.message,
        ]

    def strftime(self, format_s: str) -> str:
        """Formatted start and end."""
        end_formatted: str = self.end.strftime(format_s)
        # If the end date lies after the start date, format the hour relative to start
        if self.end.date() == (self.start.date() + dt.timedelta(days=1)):
            hour_formatted = f"{self.end.hour + 24:0>2}"
            end_formatted = self.end.strftime(format_s.replace("%H", hour_formatted))
        return "{} – {}".format(self.start.strftime(format_s), end_formatted)

    def strf(self, format_s: str) -> str:
        """Formatted Record."""
        return '{} ({}) "{}"'.format(
            self.strftime(format_s),
            self.category or "",
            self.message,
        )

    def __repr__(self) -> str:
        """String representation (simple)"""
        return "Record(start={!r}, end={!r}, category={!r}, message={!r})".format(
            self.start,
            self.end,
            self.category,
            self.message,
        )

    def __eq__(self, other) -> bool:
        if other is None or type(other) is not Record:
            return False
        return (
            self.start == other.start
            and self.end == other.end
            and self.category == other.category
            and self.message == other.message
        )

    @staticmethod
    def from_protocol_row(row):
        # type: (List[str]) -> Record
        """
        Parse one row of a protocol file in the form of
        ["start", "end", "category", "message"].
        """

        if len(row) != 4:
            raise Record.CorruptedProtocolRowError(
                f"expected 4 elements, got {len(row)}"
            )

        start: str
        end: str
        category: str
        message: str
        start, end, category, message = row

        return Record(
            start=dt.datetime.strptime(start, DATETIME_FORMAT),
            end=dt.datetime.strptime(end, DATETIME_FORMAT),
            category=category,
            message=message,
        )

    @staticmethod
    def from_other(record: "Record"):
        return Record(
            start=record.start,
            end=record.end,
            category=record.category,
            message=record.message,
        )

    @staticmethod
    def one_minute_record(start: dt.datetime):
        """Create a `Record` with the given `start` and a length of one minute."""
        return Record(start, start + dt.timedelta(minutes=1))

    @staticmethod
    def split_by_date(start, end, category=None, message=None):
        # type: (dt.datetime, dt.datetime, Optional[str], Optional[str]) -> List[Record]
        """Create valid Record instances even if the given `start` and `end` lie on
        different dates by splitting the timeframe up by date."""
        if ts.date_equals(start, end):
            return [Record(start, end, category, message)]

        if end.date() < start.date():
            raise ValueError("End date may not lie before start date!")

        records: List[Record] = []
        while start.date() < end.date():
            split = (start + dt.timedelta(days=1)).replace(hour=0, minute=0)
            records.append(Record(start, split, category, message))
            start = split
        records.append(Record(start, end, category, message))
        return records

    class UnmergeableError(Exception):
        def __init__(self, msg: str) -> None:
            super().__init__(f"Unmergeable records: {msg}")

    class CorruptedProtocolRowError(Exception):
        def __init__(self, msg: str) -> None:
            super().__init__(
                f"Detected corrupted protocol row ({msg}). Please fix manually."
            )


### Protocol container classes ###


class ProtocolMeta:
    def __init__(self):
        self._path = pathlib.Path("/tmp/WORK_UNDEFINED_PATH")
        raise NotImplementedError()

    @property
    def entries(self) -> Iterable[Record]:
        """The entries in this object's range."""
        raise NotImplementedError()

    @property
    def empty(self) -> bool:
        """Fast check if this container has entries."""
        # As `self.entries` is a generator, a simple `not self.entries` does not work!
        for _ in self.entries:
            return False
        return True

    def add(self, record: Record, force: bool = False) -> None:
        """Add an entry to this object."""
        raise NotImplementedError()

    def remove(self, record: Record) -> None:
        """Remove a record from the protocol. Raises if it does not exist."""
        raise NotImplementedError()

    def replace(self, record: Record, new_record: Record) -> None:
        """Replace an entry in this object."""
        raise NotImplementedError()

    @staticmethod
    def relative_path(
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
    ) -> str:
        """
        Return any protocol path, up to an individual file.

        Path is relative to the protocol directory.
        """

        util.verify_date_arguments(year, month, day)

        year_dir: str = str(year) if year is not None else ""
        month_dir: str = f"{month:0>2}" if month is not None else ""
        day_file: str = (
            "{:0>2}.{}".format(day, PROTOCOL_FILE_EXTENSION) if day is not None else ""
        )

        return os.path.join(year_dir, month_dir, day_file)


class ProtocolDay(ProtocolMeta):
    """Container for a protocol day. Ensures validity on creation."""

    def __init__(self, date: dt.date, root_directory: pathlib.Path):
        """Ctor."""
        self._date = date
        self._path = root_directory.joinpath(
            self.relative_path(year=date.year, month=date.month, day=date.day)
        )

    @property
    def date(self) -> dt.date:
        return self._date

    @property
    def path(self) -> pathlib.Path:
        return self._path

    @property
    def entries(self) -> List[Record]:
        """The entries on this day."""

        if not self.path.exists():
            return []

        entries: List[Record] = []

        # "If csvfile is a file object, it should be opened with newline=''."
        # See: https://docs.python.org/3/library/csv.html
        with self.path.open("r", newline="", encoding="utf-8") as protocol_file:
            reader = csv.reader(protocol_file)
            for row in reader:
                try:
                    record = self._try_parse_from_row(row)
                except Record.CorruptedProtocolRowError as err:
                    raise IOError(f"{err}\n  In: {self.path}") from err
                entries.append(record)

        if 0 == len(entries):
            raise IOError(f"Empty protocol file on disk: {self.path}")

        return entries

    def _try_parse_from_row(self, row: List[str]) -> Record:
        """Check if the record matches this ProtocolDay and raise if not."""
        try:
            record = Record.from_protocol_row(row)
        except ValueError as err:
            raise Record.CorruptedProtocolRowError(str(err))
        if not ts.date_equals(record.start, self.date):
            raise Record.CorruptedProtocolRowError("date does not match file path")
        return record

    def add(self, record: Record, force: bool = False) -> None:
        """
        Store a new entry on disk. Rewrites the file.

        force: Overwrite existing entries if necessary.
        """

        if not ts.date_equals(record.date, self.date):
            raise IOError("Given start or end time lie on a different day!")

        entries: List[Record] = self.entries
        if force:
            entries = self._cut(entries=entries, space_for=record)
        entries.append(record)
        try:
            entries_processed: List[Record] = sort_and_merge(entries)
        except OverlapError as ovl_err:
            ovl_err.message = ovl_err.message + f"\nIn file: {self.path}"
            raise ovl_err

        self._write_out(records=entries_processed)

    def _cut(self, entries: List[Record], space_for: Record) -> List[Record]:
        """Remove any overlaps with `space_for` in the given list of entries."""
        processed_entries: List[Record] = []
        for entry in entries:
            # Non-overlapping and touching entries are kept as-is
            if entry.start >= space_for.end or entry.end <= space_for.start:
                processed_entries.append(entry)
                continue

            entry_str: str = entry.strf(TIME_FORMAT)

            # Full overlap: start at or after start && end before or at end
            # Action: Do nothing == remove
            if entry.start >= space_for.start and entry.end <= space_for.end:
                print(f"Existing record overwritten: {entry_str}")
                continue

            # Internal overlap: start before start && end after end
            # Action: Split entry and add both remaining entries
            if entry.start < space_for.start and entry.end > space_for.end:
                # space_for:         xxxx
                # entry:          zzzzzzzzzzzz
                # entry_left:     zzz
                # entry_right:           zzzzz
                entry_left: Record = Record(
                    start=entry.start,
                    end=space_for.start,
                    category=entry.category,
                    message=entry.message,
                )
                entry_right: Record = Record(
                    start=space_for.end,
                    end=entry.end,
                    category=entry.category,
                    message=entry.message,
                )
                processed_entries.extend([entry_left, entry_right])
                print(
                    f"Existing record split up: {entry_str}\n"
                    f"  ➜  {entry_left.strftime(TIME_FORMAT)}"
                    f"  &  {entry_right.strftime(TIME_FORMAT)}"
                )
                continue

            # Partial overlaps modify start / end time only
            modified_start: dt.datetime = entry.start
            modified_end: dt.datetime = entry.end

            # Partial overlap from left: start before, but end within
            # Action: Shorten at end
            if entry.start < space_for.start:
                assert entry.end <= space_for.end
                modified_end = space_for.start
            # Remaining is a partial overlap from right: start within, but end after
            # Action: Shorten at start
            else:
                assert entry.end > space_for.end and entry.start >= space_for.start
                modified_start = space_for.end

            modified_entry: Record = Record(
                start=modified_start,
                end=modified_end,
                category=entry.category,
                message=entry.message,
            )
            processed_entries.append(modified_entry)
            # Message for both overlap types
            print(
                f"Existing record shortened (was {entry.strftime(TIME_FORMAT)}):"
                f" {modified_entry.strf(TIME_FORMAT)}"
            )

        return processed_entries

    def remove(self, record: Record) -> None:
        """Remove a record from the protocol. Raises if it does not exist."""

        entries: List[Record] = self.entries
        entries.remove(record)

        # If no entries remain, remove the empty file on disk.
        if 0 == len(entries):
            self.path.unlink()
            return

        self._write_out(records=entries)

    def replace(self, record: Record, new_record: Record) -> None:
        """Replace an entry in this object."""
        self.remove(record)
        self.add(new_record)

    def _write_out(self, records: List[Record]) -> None:
        """Write the given records to the file. Overwrites contents."""

        # Ensure a protocol directory exists only when actually writing to it
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

        # "If csvfile is a file object, it should be opened with newline=''."
        # See: https://docs.python.org/3/library/csv.html
        with self.path.open("w", newline="", encoding="utf-8") as protocol_file:
            protocol_writer = csv.writer(protocol_file, lineterminator="\n")
            for record in records:
                row: List[str] = record.to_protocol_row()
                protocol_writer.writerow(row)


class ShadowProtocolDay(ProtocolDay):
    """A `ProtocolDay` with tempfile storage for dry runs or similar."""

    def __init__(self, date: dt.date):
        root: pathlib.Path = pathlib.Path(tempfile.mkdtemp())
        super().__init__(date=date, root_directory=root)
        atexit.register(lambda: shutil.rmtree(root))
        atexit.register(self.path.unlink)

    @staticmethod
    def copy(other):
        # type: (ProtocolDay) -> ShadowProtocolDay
        """Copy `other`s entries to shadow it."""
        shadow = ShadowProtocolDay(other.date)
        for entry in other.entries:
            shadow.add(record=entry)
        return shadow

    def overwrite(self, other: ProtocolDay):
        """Replace `other`s state by own state."""
        for others_entry in other.entries:
            other.remove(record=others_entry)
        for my_entry in self.entries:
            other.add(record=my_entry)


class ProtocolRange(ProtocolMeta):
    """
    Container for an arbitrary time range in the protocol.

    Advantage over individually storing ProtocolDays: Lazy-loading.
    """

    def __init__(self, first: dt.date, last: dt.date, root_directory: pathlib.Path):
        self.range: List[dt.date] = util.get_period(first, last)
        self.root_directory: pathlib.Path = root_directory

    @property
    def entries(self) -> Iterable[Record]:
        """The entries in the range."""
        for day in self.days:
            for entry in day.entries:
                yield entry

    @property
    def days(self) -> Iterable[ProtocolDay]:
        """The `ProtocolDay`s in the range."""
        for date in self.range:
            yield ProtocolDay(date=date, root_directory=self.root_directory)


class Protocol(ProtocolMeta):
    """Container for the protocol."""

    def __init__(self, directory: pathlib.Path):
        """Ctor."""
        self.directory: pathlib.Path = directory

    @property
    def entries(self) -> Iterable[Record]:
        """The entries in the protocol."""
        for day in self.days:
            for entry in day.entries:
                yield entry

    @property
    def days(self) -> Iterable[ProtocolDay]:
        """A list of days in the protocol."""
        for year in Protocol._iterate_dir(
            self.directory,
            YEAR_DIR_PATTERN,
            "year",
            remove_parent_if_empty=False,
        ):
            for month in Protocol._iterate_dir(
                year,
                MONTH_DIR_PATTERN,
                "month",
                remove_parent_if_empty=True,
            ):
                children: List[pathlib.Path] = sorted(
                    month.iterdir(), key=lambda c: c.name
                )

                if not children:
                    month.rmdir()
                    print(f"Info: Removed empty directory {month.resolve()}.")
                    continue

                for child in children:
                    if not child.is_file():
                        raise IOError(
                            "Dirty protocol directory; expected day files, "
                            f'found folder "{child.resolve()}"'
                        )
                    match = re.fullmatch(DAY_FILE_PATTERN, child.name)
                    if not match:
                        raise IOError(
                            "Dirty protocol directory; expected day files, "
                            f'found irregularly named file "{child.resolve()}"'
                            f"Expected pattern: {DAY_FILE_PATTERN}"
                        )
                    yield ProtocolDay(
                        date=dt.date(
                            year=int(year.name),
                            month=int(month.name),
                            day=int(match.group(1)),
                        ),
                        root_directory=self.directory,
                    )

    @staticmethod
    def _iterate_dir(
        parent: pathlib.Path,
        child_pattern: str,
        name_for_error: str,
        remove_parent_if_empty: bool,
    ) -> Iterable[pathlib.Path]:
        """
        Iterate over the given directories' children in alphabetical order.

        Ensures that only sub-directories of the given pattern exist.
        Deletes parent if empty.
        """

        children: List[pathlib.Path] = sorted(parent.iterdir(), key=lambda c: c.name)

        if remove_parent_if_empty and not children:
            parent.rmdir()
            print(f"Info: Removed empty directory {parent.resolve()}.")
            return

        for child in children:
            if not child.is_dir():
                raise IOError(
                    f"Dirty protocol directory; expected {name_for_error} folders, "
                    f'found regular file: "{child.resolve()}"'
                )
            if not re.fullmatch(child_pattern, child.name):
                raise IOError(
                    f"Dirty protocol directory; expected {name_for_error} folders, "
                    f'found irregularly named folder: "{child.resolve()}"\n'
                    f"Expected pattern: {child_pattern}"
                )
            yield child


class OverlapError(ValueError):
    """Entries overlap when they shouldn't."""

    def __init__(self, left: Record, right: Record) -> None:
        super().__init__()
        self.left = left
        self.right = right
        self.message = (
            "Overlapping entries detected – please fix manually. Offending records:\n"
            f"  {left.strf(TIME_FORMAT)}\n"
            f"  {right.strf(TIME_FORMAT)}"
        )

    def __str__(self) -> str:
        return self.message


def sort_and_merge(entries: List[Record], output: bool = True) -> List[Record]:
    """Sort the given entries based on their start time and merge touching and
    mergeable entries."""

    # Before entries are added, the DAO checks and prevents overlaps. Therefore, we can
    # assume that entries should be either apart or "touch" and raise otherwise.

    if not entries:
        return []

    # Intentionally create a copy
    entries = sorted(entries, key=lambda entry: entry.start)
    result: List[Record] = []

    # Merging requires a base entry
    result.append(entries[0])
    last_insert: int = 0
    # Iterate the rest
    for i in range(1, len(entries)):
        next_record: Record = entries[i]
        last_record: Record = result[last_insert]

        if next_record.end <= last_record.start:
            raise RuntimeError("Invalid sorting")

        # Error case (overlapping entries): Should only occur after manual edits
        if next_record.start < last_record.end:
            raise OverlapError(last_record, next_record)

        try:
            merged_record: Record = last_record.merge(next_record)
            # Mergeable: Merge and store
            if output:
                print(
                    "Info: Detected mergeable entries in protocol. Merging...\n"
                    f"    {last_record.strf(TIME_FORMAT)}\n"
                    f"  + {next_record.strf(TIME_FORMAT)}\n"
                    f"  = {merged_record.strf(TIME_FORMAT)}"
                )
            result[last_insert] = merged_record
        except Record.UnmergeableError:
            # Not mergeable: Store
            result.append(next_record)
            last_insert += 1
            continue

    return result
