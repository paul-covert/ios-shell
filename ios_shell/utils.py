"""Contains useful functions for parsing that are not themselves parsing functions."""
import datetime
import logging
import re
from typing import List, Tuple


def apply_column_mask(data: str, mask: List[bool]) -> List[str]:
    """Apply a mask to a single row of data

    :param data: the row of data to break up
    :param mask: a string with - for every character to be included as an element
    """
    PLACEHOLDER = "@"
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
    elif fortrantype in ["I"]:
        return f"I{width}"
    elif fortrantype.upper() in ["YYYY/MM/DD", "HH:MM", "HH:MM:SS", "HH:MM:SS.SS"]:
        return f"A{len(fortrantype)+1}"
    elif fortrantype in ["' '", "NQ"]:
        return f"A{width}"
    else:
        return fortrantype


def _to_timezone_offset(name: str) -> Tuple[str, int]:
    if name.upper() in ["UTC", "GMT"]:
        return "+00:00", 0
    elif name.upper() in ["ADT"]:
        return "-03:00", -3
    elif name.upper() in ["MDT"]:
        return "-06:00", -6
    elif name.upper() in ["PDT", "MST"]:
        return "-07:00", -7
    elif name.upper() in ["PST"]:
        return "-08:00", -8
    else:
        logging.warning(f"Unknown time zone: {name}. Defaulting to UTC")
        return "+00:00", 0


def to_date(contents: str) -> datetime.date:
    date_info = [int(part) for part in contents.strip().replace("-", "/").split("/")]
    year = date_info[0]
    month = date_info[1]
    day = date_info[2]
    return datetime.date(year, month, day)


def to_time(contents: str, tzinfo=datetime.timezone.utc) -> datetime.time:
    time_info = [int(part) for piece in contents.strip().split(":") for part in piece.split(".")]
    hour = time_info[0] % 24
    minute = time_info[1] % 60
    second = time_info[2] % 60 if len(time_info) > 2 else 0
    return datetime.time(hour=hour, minute=minute, second=second, tzinfo=tzinfo)


def to_datetime(contents: str) -> datetime.datetime:
    # a more naive version of from_iso
    no_comment = contents.split("!")[0].strip()
    date, time = no_comment.split(" ")
    return datetime.datetime.combine(to_date(date), to_time(time))


def _from_iso(tz: str, date: str, time: str = "") -> datetime.datetime:
    formatted_date = date.replace("/", "-")
    tzstr, tzoffset = _to_timezone_offset(tz)
    if time.startswith("24"):
        logging.warning(f"Invalid time: {time}")
        time = "00" + time[2:]
    if time != "":
        time = " " + time
        date_string = formatted_date + time + tzstr
        return datetime.datetime.fromisoformat(date_string)
    else:
        tzinfo = datetime.timezone(datetime.timedelta(hours=tzoffset))
        return datetime.datetime.fromisoformat(formatted_date).replace(tzinfo=tzinfo)


def from_iso(value: str) -> datetime.datetime:
    value_no_comment = value.split("!")[0].strip()
    time_vals = value_no_comment.split(" ")
    if all(value == "" for value in time_vals):
        return None
    return _from_iso(*time_vals)


def _get_coord(raw_coord: str, positive_marker: str, negative_marker: str) -> float:
    coord = raw_coord.split("!")[0]
    pieces = coord.split()
    out = float(pieces[0]) + float(pieces[1]) / 60.0
    if pieces[2].upper() == positive_marker.upper():
        return out
    elif pieces[2].upper() == negative_marker.upper():
        return out * -1.0
    else:
        raise ValueError("Coordinate contains unknown direction marker")


def get_latitude(coord: str) -> float:
    return _get_coord(coord, "N", "S")


def get_longitude(coord: str) -> float:
    return _get_coord(coord, "E", "W")


def is_section_heading(s: str) -> bool:
    return re.match(r"\*[A-Z ]+\n", s) is not None
