"""Export functionality."""

import csv
import datetime as dt
import os
import sys
from functools import partial
from typing import Dict, List, Optional, Tuple

from work.components import consts
from work.components.container import Record, sort_and_merge
from work.components.dao.recess import RecessDao, Vacation


class Exporter:
    """Configure and manage record exports."""

    def __init__(self, target, selection: Dict[dt.date, List[Record]]):
        assert consts.RECORDS_VERSION == 3
        self.target = target
        self.selection = selection

    def csv(self) -> None:
        """Export in "csv" format."""
        writer = csv.writer(self.target, lineterminator=os.linesep)

        assert consts.RECORDS_VERSION == 3
        writer.writerow(["start", "end", "category", "message"])

        for records in self.selection.values():
            record: Record
            for record in records:
                writer.writerow(record.to_protocol_row())

    def tng(self, recess_dao: RecessDao) -> None:
        """Export in "tng" format."""

        my_print = partial(print, file=self.target)
        weekdays = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        warnings: List[str] = []

        date: dt.date
        records: List[Record]
        for i, (date, records) in enumerate(self.selection.items()):
            vacation_record: Optional[Record]
            recess = recess_dao.get_recess_for(date)
            if recess is not None and type(recess) is Vacation:
                vacation_record = Record(
                    dt.datetime.combine(date, dt.time(8, 0)),
                    dt.datetime.combine(date, dt.time(16, 0)),
                    "urlaub",
                )

                if records:
                    warnings.append(
                        f"{date} is recorded as a vacation day, but also has logged "
                        "entries. Exporting both, but the time may overlap."
                    )

                records.append(vacation_record)

            if not records:
                continue

            if i > 0:
                my_print()  # empty line between days

            # Day header
            my_print(f"* {weekdays[date.weekday()]}. {date.strftime('%d.%m.')}")

            # Entries
            merged_messages = TngPreprocessor._pre_merge_messages(records)
            merged_records = sort_and_merge(merged_messages, output=False)
            record: Record
            for record in merged_records:
                message = TngPreprocessor._process_message(record.message)

                my_print(
                    "{} - {} {} {}".format(
                        record.start.strftime("%H:%M"),
                        record.end.strftime("%H:%M"),
                        record.category,
                        message,
                    )
                )

        for warning in warnings:
            print(f"\nWarning: {warning}", file=sys.stderr)


class TngPreprocessor:
    # Separator when merging messages
    MESSAGE_SEPARATOR: str = "; "

    # Maximum length for a message in the export
    MAXIMUM_MESSAGE_LENGTH: int = 500

    @classmethod
    def _pre_merge_messages(cls, entries: List[Record]) -> List[Record]:
        """Merge (combine) messages of touching entries with the same category.
        Entries must already be sorted."""

        if not entries:
            return []

        # Create a copy, as we do in-place edits
        entries = [Record.from_other(entry) for entry in entries]
        # Add non-mergeable entry at the end to simplify loop
        entries.append(
            Record(
                entries[-1].end + dt.timedelta(minutes=1),
                entries[-1].end + dt.timedelta(minutes=2),
                "__non_mergeable__",
                "",
            )
        )

        def reset(index: int) -> Tuple[int, str, List[str]]:
            first_i: int = index
            category: str = entries[index].category
            messages_buffer: List[str] = []
            if msg := entries[index].message:
                messages_buffer.append(msg)
            return first_i, category, messages_buffer

        first_i, category, messages_buffer = reset(0)

        def merge_messages(first: int, exclude: int):
            """Combine the messages of entries at index `first` up to, but excluding,
            `exclude` into a single one and overwrite each affected entry."""
            # Just one entry
            if first + 1 == exclude:
                return

            merged_message: str = cls.MESSAGE_SEPARATOR.join(messages_buffer)
            for i in range(first, exclude):
                entries[i].message = merged_message

        for i in range(1, len(entries)):
            next_record = entries[i]
            not_mergeable: bool = next_record.category != category
            not_mergeable |= not next_record.touches(entries[i - 1])

            # End of message-mergeable entries – also occurs on sentinel element at end
            if not_mergeable:
                merge_messages(first_i, i)
                first_i, category, messages_buffer = reset(i)
                continue

            # Only add non-empty and new messages
            if next_record.message and next_record.message not in messages_buffer:
                messages_buffer.append(next_record.message)

        assert entries[-1].category == "__non_mergeable__"
        entries.pop()

        return entries

    @classmethod
    def _process_message(cls, message: str):
        """Truncate to maximum length and remove non-ASCII characters."""

        truncated: str = message
        if len(message) > cls.MAXIMUM_MESSAGE_LENGTH:
            truncated = message[: cls.MAXIMUM_MESSAGE_LENGTH - 3] + "..."

        result = []
        for char in truncated:
            char_ord = ord(char)
            # Allow ASCII characters + umlauts
            if char_ord < 127 or char_ord in [ord(umlaut) for umlaut in "äöüÄÖÜß"]:
                result.append(char)
                continue

            # Replace em dash
            if char == "–":
                result.append("-")
                continue

            # Replace unknown characters
            result.append("_")

        return "".join(result)
