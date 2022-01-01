"""Contains useful functions for parsing that are not themselves parsing functions."""
import datetime
import re
from typing import List


DATE_STR = r"\d{4}[/-]\d{2}[/-]\d{2}"
TIME_STR = r"\d{2}:\d{2}(:\d{2}(.\d*)?)?"
TIMEZONE_STR = r"[A-Za-z]{3}"


def apply_column_mask(data: str, mask: List[bool]) -> List[str]:
    """Apply a mask to a single row of data

    :param data: the row of data to break up
    :param mask: a string with - for every character to be included as an element
    """
    PLACEHOLDER = "@"  # pragma: no mutate
    data = data.rstrip().ljust(len(mask))
    masked = [
        c if i >= len(mask) or mask[i] else PLACEHOLDER for i, c in enumerate(data)
    ]
    out = "".join(masked).split(PLACEHOLDER)
    while "" in out:
        out.remove("")
    return out


def format_string(fortrantype: str, width: int, decimals: int) -> str:
    """Construct an appropriate format string for the given type

    :param fortrantype: the type the data is expected to be
    :param width: the number of characters the data may take up
    :param decimals: the number of characters after a decimal a float is intended to use
    """
    fortrantype = fortrantype.strip().upper()
    if fortrantype in ["F"]:
        return f"F{width}.{decimals}"
    elif fortrantype in ["E"]:
        return f"E{width}.{decimals}"
    elif fortrantype in ["I"]:
        return f"I{width}"
    elif fortrantype.upper() in ["YYYY/MM/DD", "HH:MM", "HH:MM:SS", "HH:MM:SS.SS"]:
        return f"A{len(fortrantype)+1}"
    elif fortrantype in ["' '", "NQ"]:
        return f"A{width}"
    else:
        return fortrantype


def _to_timezone_offset(name: str) -> int:
    if name.upper() in ["UTC", "GMT"]:
        return 0
    elif name.upper() in ["ADT"]:
        return -3
    elif name.upper() in ["MDT"]:
        return -6
    elif name.upper() in ["PDT", "MST"]:
        return -7
    elif name.upper() in ["PST"]:
        return -8
    else:
        raise ValueError(f"Unknown time zone: {name}.")


def to_date(contents: str) -> datetime.date:
    date_info = [int(part) for part in contents.strip().replace("-", "/").split("/")]
    year = date_info[0]
    month = date_info[1]
    day = date_info[2]
    return datetime.date(year, month, day)


def to_time(contents: str, tzinfo=datetime.timezone.utc) -> datetime.time:
    time_info = [
        int(part) for piece in contents.strip().split(":") for part in piece.split(".")
    ]
    hour = time_info[0] % 24
    minute = time_info[1] % 60
    second = time_info[2] % 60 if len(time_info) > 2 else 0
    return datetime.time(hour=hour, minute=minute, second=second, tzinfo=tzinfo)


def _to_datetime(tz: str, date: str, time: str) -> datetime.datetime:
    tzoffset = _to_timezone_offset(tz)
    date_obj = to_date(date)
    tz_obj = datetime.timezone(datetime.timedelta(hours=tzoffset))
    if time != "":
        time_obj = to_time(time, tz_obj)
        return datetime.datetime.combine(date_obj, time_obj)
    else:
        return datetime.datetime(
            date_obj.year, date_obj.month, date_obj.day, tzinfo=tz_obj
        )


def to_datetime(value: str) -> datetime.datetime:
    # attempting to cover "Unknown" and "Unk.000"
    if value == "" or "unk" in value.lower():
        return datetime.datetime.min
    match_date = f"(?P<date>{DATE_STR})"
    match_tz = f"(?P<tz>{TIMEZONE_STR})"
    match_time = f"(?P<time>{TIME_STR})"
    # separate matches are required in order to avoid reusing group names
    if m := re.match(f"{match_date} {match_time}", value):
        return _to_datetime(tz="UTC", **m.groupdict())
    elif m := re.match(
        f"{match_tz} {match_date}( {match_time})?",
        value,
    ):
        return _to_datetime(**m.groupdict(""))
    elif m := re.match(
        f"{match_date}( {match_time})? {match_tz}",
        value,
    ):
        return _to_datetime(**m.groupdict(""))
    else:
        raise ValueError(f"Unknown time format: {value}")


def _get_coord(raw_coord: str, positive_marker: str, negative_marker: str) -> float:
    coord = raw_coord.split("!")[0]
    degrees, minutes, direction = coord.split()
    out = float(degrees) + float(minutes) / 60.0
    if direction.upper() == positive_marker.upper():
        return out
    elif direction.upper() == negative_marker.upper():
        return out * -1.0  # pragma: no mutate
    else:
        raise ValueError("Coordinate contains unknown direction marker")


def get_latitude(coord: str) -> float:
    return _get_coord(coord, "N", "S")


def get_longitude(coord: str) -> float:
    return _get_coord(coord, "E", "W")


def is_section_heading(s: str) -> bool:
    return re.match(r"\*[A-Z ]+(\n|$)", s) is not None
