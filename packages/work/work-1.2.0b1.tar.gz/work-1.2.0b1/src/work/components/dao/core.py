#!/usr/bin/env python3

"""The DAO for the work module."""

import datetime as dt
import json
import pathlib
import zlib
from types import SimpleNamespace
from typing import Dict, List, Optional, Tuple

import work.components.dt_format as dt_format
from work.components import migrate
from work.components.consts import (
    DATETIME_FORMAT,
    INFO_FILE_NAME,
    PROTOCOL_DIRECTORY_NAME,
    RECORDS_VERSION,
    RUN_FILE_NAME,
    VERSION,
)
from work.components.container import (
    Protocol,
    ProtocolDay,
    ProtocolMeta,
    ProtocolRange,
    Record,
)
from work.components.timestamps import Timestamp


class WorkDao:
    """DAO for the work directory and its children."""

    # work_directory        self.work_directory
    # |- info.winf          self.info_file
    # |- running.wtime      self.run_file
    # |- records/           self.records_directory
    #    |- 2019/ ...       –
    #    |- ...             –
    # |- vacations/         –
    #    |- 2021.wvac       –
    #    |- ...             –
    #
    # (see work.components/consts.py)
    def __init__(self, work_directory: pathlib.Path):
        self.work_directory: pathlib.Path = work_directory
        self.info_file: WorkDao.InfoFileDao = WorkDao.InfoFileDao(
            self.work_directory.joinpath(INFO_FILE_NAME)
        )
        self.run_file: WorkDao.RunFileDao = WorkDao.RunFileDao(
            self.work_directory.joinpath(RUN_FILE_NAME)
        )
        self.records_directory: pathlib.Path = self.work_directory.joinpath(
            PROTOCOL_DIRECTORY_NAME
        )

        # We assume existence of the root directory in many operations.
        self._ensure_work_dir_exists()

    ### <MIGRATE-midnight> To be removed in v1.3 ###

    def migrate_records_touching_midnight(self, end_lower_bound: Timestamp):
        """Extend records touching midnight to end at 24:00."""
        migrate.noop_records_midnight()

        print("Extending records...")

        # Iterate complete protocol
        protocol = self._load_protocol()
        pday: ProtocolDay
        for pday in protocol.days:
            relative_bound: dt.datetime = end_lower_bound.combined(pday.date)
            assert relative_bound.date() == pday.date

            if not pday.entries:
                continue
            last = pday.entries[-1]
            midnight = (last.start + dt.timedelta(days=1)).replace(hour=0, minute=0)
            if last.end < relative_bound or last.end >= midnight:
                continue

            last = pday.entries[-1]
            edited = Record(
                last.start,
                midnight,
                category=last.category,
                message=last.message,
            )
            pday.replace(last, edited)
            print(
                f"✔ Edited {pday.date.strftime(dt_format.DATE_FORMAT)}: "
                f"Last entry extended from {dt_format.readable_t(last.end)} "
                f"to {dt_format.readable_t(edited.end, base=edited.start.date())}"
            )

        # Update the edit time and checksum
        self.update_info_file()
        print("\nConversion done.")

    ### Interface ###

    def start_run(self, start_time: dt.datetime, force: bool = False) -> None:
        """Start a run at the given time. Raises on invalid operation."""

        if not force and self.run_file.exists():
            raise IOError(
                f'File "{self.run_file.resolve()}" exists already! Could not create.'
            )

        self.run_file.write(start_time)

    def stop_run(
        self, end_time: dt.datetime, category: str, message: str, force: bool = False
    ) -> None:
        """Stop a run at the given time. Raises on invalid operation."""

        start_time = self.get_start_time()
        if start_time is None:
            raise RuntimeError("Tried to stop, but no run is active!")

        self.add_protocol_entry(start_time, end_time, category, message, force)
        self.run_file.unlink()

    def invalid_start_and_end_error(
        self, start_time: dt.datetime, end_time: dt.datetime
    ) -> Optional[str]:
        """Returns an error message if the combination of start and end is invalid."""
        if end_time <= start_time:
            return "end time must be after start time"

        # Ensure that start and end lie at most one calendar day apart.
        if end_time.date() not in [sd := start_time.date(), sd + dt.timedelta(days=1)]:
            return "a run end may not lie more than one calendar day after its start"

    def add_protocol_entry(
        self,
        start_time: dt.datetime,
        end_time: dt.datetime,
        category: str,
        message: str,
        force: bool = False,
    ) -> None:
        """
        Add the given elements to the end of the protocol file.
        Checks validity of the info file and updates it after write.
        """

        if self.invalid_start_and_end_error(start_time, end_time) is not None:
            raise ValueError("Invalid combination of start and end time!")

        if not force and self.has_entry(start_time=start_time, end_time=end_time):
            raise RuntimeError("Given time(s) overlap with existing protocol entry!")

        # If start end end lie on different dates, the factory splits them up.
        records = Record.split_by_date(start_time, end_time, category, message)

        for record in records:
            protocol_day: ProtocolDay = self._load_protocol_date(record.date)
            protocol_day.add(record=record, force=force)

        # Update the edit time and checksum
        self.update_info_file()

    def cancel_run(self) -> None:
        """Cancel any currently active run."""
        self.run_file.unlink()

    def run_active(self) -> bool:
        """Convenience function to check if a run is active."""
        return self.get_start_time() is not None

    def get_start_time(self) -> Optional[dt.datetime]:
        """
        Try to retrieve the start time from the run file.

        Returns: None if no run is active.
        """

        if not self.run_file.exists():
            return None

        return self.run_file.read()

    def has_entry(
        self, start_time: dt.datetime, end_time: Optional[dt.datetime] = None
    ) -> bool:
        """Check whether an existing entry overlaps the given time."""

        # Minimum run length: 1 minute
        end_time = end_time or start_time + dt.timedelta(minutes=1)

        start_date: dt.date = start_time.date()
        end_date: dt.date = end_time.date()

        # This comparison works even with our looser definition of "same date".
        if start_date > end_date:
            raise ValueError("Start date lies after end date!")

        # We can "forget" the 0:00 case, as the start time only affects upcoming days.
        current_date: dt.date = start_date
        protocol_days: List[ProtocolDay] = []
        # Add all days covered by start and end time.
        while current_date <= end_date:
            protocol_days.append(self._load_protocol_date(current_date))
            current_date += dt.timedelta(days=1)

        # There may not be any entry on any day overlapping any part of the given slot
        for protocol_day in protocol_days:
            for record in protocol_day.entries:
                # "Touching" of entries (so start_time == existing_end or
                # end_time == existing_start) is allowed
                if record.overlaps(SimpleNamespace(start=start_time, end=end_time)):
                    return True

        return False

    def get_entries(
        self,
        date: Optional[dt.date] = None,
        date_range: Optional[Tuple[dt.date, dt.date]] = None,
    ) -> List[Record]:
        """
        Load stored entries (excluding a possible active run).
        Entries are sorted and overlap-free.

        You may optionally define either one of the optional parameters (but not both):

        : date :  Load a date.

        : range : Load a range.
        """

        entries_container: Optional[ProtocolMeta] = None

        # Nothing specified: Load all
        if date is None and date_range is None:
            entries_container = self._load_protocol()
        # Date specified
        elif date is not None:
            entries_container = self._load_protocol_date(date=date)
        # Range specified
        elif date_range is not None:
            entries_container = self._load_protocol_range(*date_range)
        # Both specified: Invalid arguments
        else:
            raise ValueError("May either specifiy a date or a range, not both.")

        return list(entries_container.entries)

    def get_container(self, date: dt.date) -> ProtocolMeta:
        """Load a ProtocolMeta interface to the entries."""
        return self._load_protocol_date(date)

    def protocol_empty(self) -> bool:
        """Fast check if the protocol is empty."""
        if not self.records_directory.exists():
            return True
        protocol: Protocol = self._load_protocol()
        return protocol.empty

    def ensure_protocol_integrity(self) -> None:
        """
        Check all preconditions for valid file operations.
        - Ensure a valid directory exists, otherwise create it.
        - Check if a protocol exists and the corresponding info file matches it.
        Raises if invalid directory structure or files are found.
        """

        protocol: Protocol = self._load_protocol()
        protocols_exist: bool = not protocol.empty
        protocol_info_exists: bool = self.info_file.file.exists()

        # If no protocols and no info file exist, they can be created safely.
        if not protocols_exist and not protocol_info_exists:
            return

        # If the info file is missing, something has gone wrong.
        if not protocol_info_exists:
            raise IOError(
                "Work info file not found! If you moved to a new computer, "
                'reinitialize it by running "work rehash", then try again.'
            )
        # The reverse case (info file exists, protocol doesn't) is acceptable, as the
        # protocol integrity is verified with the checksum below.

        self.info_file.load()

        # Version as expected?
        if self.info_file.records_version != RECORDS_VERSION:
            raise IOError(
                "Unexpected records version {}, expected {}".format(
                    self.info_file.records_version, RECORDS_VERSION
                )
            )
        # Checksum matches?
        protocol_checksum: int = self._get_protocol_checksum()
        if self.info_file.checksum != protocol_checksum:
            raise IOError(
                "The info file contains a checksum that does not correspond to the "
                "records stored on disk, e.g. because they were manually edited. To "
                'accept these changes, run "work rehash", then try again.'
            )

    def update_info_file(self) -> None:
        """Update the info file with the current time and a new protocol checksum."""
        self.info_file.update(self._get_protocol_checksum())

    ### File I/O ###

    def _get_protocol_checksum(self) -> int:
        """Return an Adler-32 checksum representing the protocol."""

        content: List[str] = []
        protocol: Protocol = self._load_protocol()
        record: Record
        # Entries are always given back in alphabetical order by year, month, and day
        for record in protocol.entries:
            content.append(repr(record))

        checkbytes: bytes = ";".join(content).encode("utf-8")
        checksum: int = zlib.adler32(checkbytes)
        return checksum

    ### Protocol access (high level) ###

    def _load_protocol(self) -> Protocol:
        """Load Protocol (lazily)."""
        return Protocol(directory=self.records_directory)

    def _load_protocol_date(self, date: dt.date) -> ProtocolDay:
        """Load protocol for the given date (lazily)."""
        return ProtocolDay(
            date=date,
            root_directory=self.records_directory,
        )

    def _load_protocol_range(self, r_start: dt.date, r_end: dt.date) -> ProtocolMeta:
        """Load protocol for the given range (lazily)."""
        return ProtocolRange(
            first=r_start,
            last=r_end,
            root_directory=self.records_directory,
        )

    ### File system I/O (low level) ###

    def _ensure_work_dir_exists(self) -> None:
        """Ensure the work and protocol directories exist and create it if it doesn't."""

        directory: pathlib.Path
        for directory in [self.work_directory, self.records_directory]:
            if not directory.exists():
                print(f"Initialized the directory {directory.resolve()}")
            elif not directory.is_dir():
                raise IOError(
                    f"Directory path {directory.resolve()} is taken by a file; please delete it."
                )

        # Nested creation (creates all parent directories, too)
        self.records_directory.mkdir(parents=True, exist_ok=True)

    ### Low level classes ###

    class InfoFileDao:
        """DAO for the info file. Used for grouping of functionality."""

        def __init__(self, file: pathlib.Path) -> None:
            self.file: pathlib.Path = file
            self.program_version: str = VERSION
            self.records_version: int = RECORDS_VERSION
            self.checksum: int = 0

            if self.file.exists():
                self.load()

        def load(self) -> None:
            """Load and store info file contents."""

            with self.file.open(mode="r", encoding="utf-8") as info_file:
                info_file_content = json.load(info_file)

            self.program_version = info_file_content["program version"]
            self.records_version = info_file_content["records format version"]
            self.checksum = info_file_content["checksum"]

        def write(self) -> None:
            """Write info file content to disk. Only changes 'last update' field."""
            info_file_content: Dict = {
                "program version": self.program_version,
                "records format version": self.records_version,
                "last update": dt.datetime.now().strftime(DATETIME_FORMAT),
                "checksum": self.checksum,
            }

            with self.file.open(mode="w", encoding="utf-8", newline="\n") as info_file:
                json.dump(info_file_content, info_file, indent="\t", ensure_ascii=False)

        def update(self, protocol_checksum: int) -> None:
            """Update versions and protocol checksum and write to disk."""

            self.program_version = VERSION
            self.records_version = RECORDS_VERSION
            self.checksum = protocol_checksum
            self.write()

    class RunFileDao:
        """DAO for the run file, useful for caching."""

        def __init__(self, file: pathlib.Path) -> None:
            self.file: pathlib.Path = file
            self.cache: Optional[dt.datetime] = None

        def exists(self) -> bool:
            """Direct interface to file.exists()"""
            return self.file.exists()

        def resolve(self) -> pathlib.Path:
            """Direct interface to file.resolve()"""
            return self.file.resolve()

        def unlink(self) -> None:
            """Direct interface to file.unlink()"""
            self.file.unlink()
            self.cache = None

        def write(self, start_time: dt.datetime) -> None:
            """Wrapper for file.open() and handler.write()"""
            with self.file.open(mode="w", encoding="utf-8", newline="\n") as run_file_h:
                run_file_h.write(start_time.strftime(DATETIME_FORMAT))
            self.cache = start_time

        def read(self) -> dt.datetime:
            """
            Wrapper for file.open(), handler.read(), and strptime(content).

            Utilizes cached file content if available.
            """
            if self.cache is not None:
                return self.cache

            with self.file.open(mode="r", encoding="utf-8") as run_file_h:
                content: str = run_file_h.read()

            try:
                self.cache = dt.datetime.strptime(content.strip(), DATETIME_FORMAT)
                return self.cache
            except ValueError as val_error:
                raise IOError(
                    f"Invalid run file! Please delete or fix. (Path: {self.resolve()})"
                ) from val_error
