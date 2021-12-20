import datetime
import logging
import re
from typing import List


def apply_column_mask(data: str, mask: List[bool]) -> List[str]:
    """Apply a mask to a single row of data

    Parameters
    data: the row of data to break up
    mask: a string with - for every character to be included as an element
    """
    PLACEHOLDER = "$"
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

    Parameters
    fortrantype: the type the data is expected to be
    width: the number of characters the data may take up
    decimals: the number of characters after a decimal a float is intended to use
    """
    fortrantype = fortrantype.strip()
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


def _to_timezone_offset(name: str) -> str:
    if name.upper() in ["UTC", "GMT"]:
        return "+00:00"
    elif name.upper() in ["MDT"]:
        return "-06:00"
    elif name.upper() in ["PDT", "MST"]:
        return "-07:00"
    elif name.upper() in ["PST"]:
        return "-08:00"
    else:
        logging.warning(f"Unknown time zone: {name}. Defaulting to UTC")
        return "+00:00"


def _to_iso(tz: str, date: str, time: str = "") -> datetime.datetime:
    formatted_date = date.replace("/", "-")
    if time.startswith("24"):
        logging.warning(f"Invalid time: {time}")
        time = "00" + time[2:]
    if time != "":
        time = " " + time
        tzinfo = _to_timezone_offset(tz)
        date_string = formatted_date + time + tzinfo
        return datetime.datetime.fromisoformat(date_string)
    else:
        return datetime.datetime.fromisoformat(formatted_date)


def to_iso(value: str) -> datetime.datetime:
    value_no_comment = value.split("!")[0].strip()
    time_vals = value_no_comment.split(" ")
    return _to_iso(*time_vals)


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
