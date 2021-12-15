import datetime

def apply_column_mask(data: str, mask: list[bool]) -> list[str]:
    """ Apply a mask to a single row of data

    Parameters
    data: the row of data to break up
    mask: a string with - for every character to be included as an element
    """
    PLACEHOLDER = "$"
    data = data.rstrip().ljust(len(mask))
    masked = [c if mask[i] else PLACEHOLDER for i, c in enumerate(data)]
    out = "".join(masked).split(PLACEHOLDER)
    while "" in out:
        out.remove("")
    return out

def format_string(fortrantype: str, width: int, decimals: int) -> str:
    """ Construct an appropriate format string for the given type

    Parameters
    fortrantype: the type the data is expected to be
    width: the number of characters the data may take up
    decimals: the number of characters after a decimal a float is intended to use
    """
    fortrantype = fortrantype.strip()
    if fortrantype in ["F"]:
        return f"F{width}.{decimals}"
    elif fortrantype in ["I", "NQ"]:
        return f"I{width}"
    elif fortrantype in ["YYYY/MM/DD"]:
        return "A11"
    elif fortrantype in ["HH:MM"]:
        return "A6"
    elif fortrantype in ["' '"]:
        return f"A{width}"
    else:
        return fortrantype

def validate_keys(keys: list[str], expected_keys: list[str], section: str):
    bad_keys = [key for key in keys if key not in expected_keys]
    if len(bad_keys) > 0:
        raise ValueError(f"Unknown keys in {section.upper()} section: {bad_keys}")

def to_iso(value: str) -> datetime.datetime:
    value_no_comment = value.split("!")[0]
    # TODO: handle time zone
    tz, date, time = value_no_comment.split(" ")
    return datetime.datetime.fromisoformat("T".join([date.replace("/", "-"), time]))

def _get_coord(raw_coord: str, positive_marker: str, negative_marker: str) -> float:
    coord = raw_coord.split("!")[0]
    pieces = coord.split()
    out = float(pieces[0]) + float(pieces[1]) / 60.0
    if pieces[2] == positive_marker:
        return out
    elif pieces[2] == negative_marker:
        return out * 1.0
    else:
        raise ValueError("Coordinate contains unknown direction marker")

def get_latitude(coord: str) -> float:
    return _get_coord(coord, "N", "S")

def get_longitude(coord: str) -> float:
    return _get_coord(coord, "E", "W")

