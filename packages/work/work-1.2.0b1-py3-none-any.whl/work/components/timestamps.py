"""API wrapper and extension for datetime"""

import datetime as dt
from dataclasses import dataclass
from typing import Set


def date_equals(left: dt.date, right: dt.date) -> bool:
    """Compare date equality of arbitrary date or datetime instances.
    Handles comparison of datetime to date."""
    # Intersection is not empty => (at least) one associated date overlaps
    return bool(shared_dates(left, right))


def shared_dates(left: dt.date, right: dt.date) -> Set[dt.date]:
    """Return the date that is shared by both date or datetime instances."""
    if not isinstance(left, dt.date) or not isinstance(right, dt.date):
        raise TypeError("Expected instance of (subclass of) datetime.date.")

    # If both are 0:00 of the same day, both their "dates" would overlap and be returned.
    if isinstance(left, dt.datetime) and left == right:
        return {left.date()}

    left_dates = _associated_dates(left)
    right_dates = _associated_dates(right)

    return left_dates.intersection(right_dates)


def single_shared_date(left: dt.date, right: dt.date) -> dt.date:
    """Return exactly one shared date. Raises if more or less dates are shared."""
    shared = shared_dates(left, right)
    if len(shared) != 1:
        raise ValueError(f"More than one date shared between {left} and {right}.")
    return shared.pop()


def _associated_dates(given: dt.date) -> Set[dt.date]:
    """
    Return the associated date(s) of the given date or datetime.

    - For a date, return {date}.
    - For a datetime with time != 0:00, return {day}
    - For a datetime with time == 0:00, return {day before, day}
    """
    if not isinstance(given, dt.datetime):
        assert isinstance(given, dt.date)
        return {given}
    if given.time() != dt.time(0, 0):
        return {given.date()}
    return {given.date() - dt.timedelta(days=1), given.date()}


@dataclass(init=False, order=True)
class Timestamp:
    hour: int
    minute: int

    def __init__(self, hour: int, minute: int):
        if hour not in range(0, 30):
            raise ValueError("hour must be in 0..29")
        # Check minute for validity by constructing a temporary dt.time object
        dt.time(0, minute)
        self.hour = hour
        self.minute = minute

    def combined(self, date: dt.date) -> dt.datetime:
        """Combine the given date with this timestamp's hour and minute.
        Note: If the hour is > 24, the date will be incremented to match."""
        offset: int = self.hour // 24
        hour: int = self.hour % 24
        time: dt.time = dt.time(hour, self.minute)
        return dt.datetime.combine(date, time) + dt.timedelta(days=offset)
