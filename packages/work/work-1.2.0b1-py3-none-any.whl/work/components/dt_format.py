#!/usr/bin/env python3
"""Date/time formatting"""

import datetime as dt
from typing import Optional

# Formats
TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%d.%m.%Y"
DATE_FORMAT_FULL = "%A, " + DATE_FORMAT


def readable_d(date: dt.date) -> str:
    """Convert the given datetime.date to a human readable string with the day."""
    if date == dt.date.today():
        return "today"
    elif date == (dt.date.today() + dt.timedelta(days=1)):
        return "tomorrow"
    elif date == (dt.date.today() - dt.timedelta(days=1)):
        return "yesterday"
    else:
        return "on " + date.strftime(DATE_FORMAT_FULL)


def readable_t(time: dt.datetime, base: Optional[dt.date] = None) -> str:
    """Convert the given datetime.datetime to a human-readable string.
    If `base` is given, format the hour relative to that date."""
    time_format = TIME_FORMAT
    delta = 0 if base is None else (time.date() - base).days
    if delta != 0:
        hour_formatted = f"{time.hour + (24 * delta):0>2}"
        time_format = TIME_FORMAT.replace("%H", hour_formatted)
    return time.strftime(time_format)


def readable_dt(date_and_time: dt.datetime, base: Optional[dt.date] = None) -> str:
    """Convert the given datetime.datetime to a human readable string with the time
    and day. If `base` is given, format the hour relative to that date."""
    base = base or date_and_time.date()
    result: str = readable_t(date_and_time, base)
    result += " " + readable_d(base)
    return result


def date_fmt(date_to_format: dt.date) -> str:
    """Return date format that only includes the year if it's not the current one."""
    if date_to_format.year == dt.date.today().year:
        return "%d.%m."
    return "%d.%m.%Y"
