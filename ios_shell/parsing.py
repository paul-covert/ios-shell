import datetime
import functools
import logging
import re
import typing

from .keys import *
from .sections import *
from .utils import *

def fallible(name):
    def decorator_fallible(fn: typing.Callable[[str], tuple[typing.Any, str]]):
        @functools.wraps(fn)
        def wrapper(contents: str) -> tuple[typing.Union[typing.Any, None], str]:
            try:
                return fn(contents)
            except Exception as e:
                logging.warning(f"Could not find valid {name.upper()} section: {e}")
                return None, contents
        return wrapper
    return decorator_fallible

DATE_STR = r"\d{4}/\d{2}/\d{2}"
TIME_STR = r"\d{2}:\d{2}:\d{2}(.\d*)?"

def get_modified_date(contents: str) -> tuple[datetime.datetime, str]:
    rest = contents.lstrip()
    if (m := re.match(fr"\*({DATE_STR} {TIME_STR})", rest)):
        rest = rest[m.end():]
        # trim sub-second information to make parsing using datetime easier
        raw_datetime = m.group(1).replace("/", "-").split(".")[0]
        return (datetime.datetime.fromisoformat(raw_datetime), rest)
    else:
        raise ValueError("No modified date at start of string")

def get_header_version(contents: str) -> tuple[str, str]:
    rest = contents.lstrip()
    if (m := re.match(fr"\*IOS HEADER VERSION (\d+.\d+) {DATE_STR} {DATE_STR}", rest)):
        rest = rest[m.end():]
        return (m.group(1), rest)
    else:
        raise ValueError("No header version in string")

def get_section(contents: str, section_name: str) -> tuple[dict[str, typing.Any], str]:
    rest = contents.lstrip()
    prefix = f"*{section_name.upper()}"
    section_info = {}
    if rest.startswith(prefix):
        rest = rest[len(prefix)+1:]
        while not rest.lstrip().startswith("*"):
            rest = rest.lstrip()
            if (m := re.match(r"\$TABLE: ([^\n]+)\n", rest)):
                # handle table
                table_name = m.group(1).lower()
                rest = rest[m.end():].lstrip()
                # table column names
                line, rest = rest.split("\n", 1)
                column_names = [name.lower() for name in line.lstrip()[1:].split()]
                # table column mask
                line, rest = rest.split("\n", 1)
                mask = [c == "-" for c in line]
                # values
                section_info[table_name] = []
                while not rest.lstrip().startswith("$END"):
                    line, rest = rest.split("\n", 1)
                    section_info[table_name].append(
                        {column_names[i]: v for i, v in enumerate(apply_column_mask(line, mask))})
                _, rest = rest.lstrip().split("\n", 1)
            else:
                # handle single entry
                line, rest = rest.split("\n", 1)
                key, value = line.split(":", 1)
                section_info[key.strip().lower()] = value.strip()
        return section_info, rest
    else:
        raise ValueError(f"Section {section_name.upper()} not present")

def get_file(contents: str) -> tuple[FileInfo, str]:
    file_dict, rest = get_section(contents, "file")
    validate_keys(file_dict.keys(), FILE_KEYS, "file")
    start_time = to_iso(file_dict[START_TIME]) if START_TIME in file_dict else datetime.datetime.fromtimestamp(0)
    end_time = to_iso(file_dict[END_TIME]) if END_TIME in file_dict else datetime.datetime.fromtimestamp(0)
    time_zero = to_iso(file_dict[TIME_ZERO]) if TIME_ZERO in file_dict else datetime.datetime.fromtimestamp(0)
    number_of_records = int(file_dict[NUMBER_OF_RECORDS])
    data_description = file_dict[DATA_DESCRIPTION] if DATA_DESCRIPTION in file_dict else ""
    file_type = file_dict[FILE_TYPE] if FILE_TYPE in file_dict else ""
    number_of_channels = int(file_dict[NUMBER_OF_CHANNELS])
    channels = [Channel(**elem) for elem in file_dict[CHANNELS]] if CHANNELS in file_dict else []
    channel_details = [ChannelDetail(**elem) for elem in file_dict[CHANNEL_DETAIL]] if CHANNEL_DETAIL in file_dict else []
    remarks = file_dict[REMARKS] if REMARKS in file_dict else ""
    data_type = file_dict[DATA_TYPE] if DATA_TYPE in file_dict else ""
    to_remove = " \n\t'"
    if FORMAT in file_dict:
        format_str = file_dict[FORMAT].strip(to_remove)
        if CONTINUED in file_dict:
            format_str += file_dict[CONTINUED].strip(to_remove)
    else:
        format_info = [format_string(detail.format, detail.width, detail.decimal_places) for detail in channel_details]
        format_str = "({})".format(",".join(format_info))
    file_info = FileInfo(
        start_time,
        end_time,
        time_zero,
        number_of_records,
        data_description,
        file_type,
        format_str,
        data_type,
        number_of_channels,
        channels,
        channel_details,
        remarks,
    )
    return file_info, rest

@fallible("administration")
def get_administration(contents: str) -> tuple[Administration, str]:
    admin_dict, rest = get_section(contents, "administration")
    validate_keys(admin_dict.keys(), ADMINISTRATION_KEYS, "administration")
    mission = admin_dict[MISSION] if MISSION in admin_dict else ""
    agency = admin_dict[AGENCY] if AGENCY in admin_dict else ""
    country = admin_dict[COUNTRY] if COUNTRY in admin_dict else ""
    project = admin_dict[PROJECT] if PROJECT in admin_dict else ""
    scientist = admin_dict[SCIENTIST] if SCIENTIST in admin_dict else ""
    platform = admin_dict[PLATFORM] if PLATFORM in admin_dict else ""
    admin_info = Administration(
        mission,
        agency,
        country,
        project,
        scientist,
        platform,
    )
    return admin_info, rest

@fallible("location")
def get_location(contents: str) -> tuple[Location, str]:
    location_dict, rest = get_section(contents, "location")
    validate_keys(location_dict.keys(), LOCATION_KEYS, "location")
    geographic_area = location_dict[GEOGRAPHIC_AREA] if GEOGRAPHIC_AREA in location_dict else ""
    station = location_dict[STATION] if STATION in location_dict else ""
    event_number = int(location_dict[EVENT_NUMBER]) if EVENT_NUMBER in location_dict else -1
    latitude = get_latitude(location_dict[LATITUDE])
    longitude = get_longitude(location_dict[LONGITUDE])
    location_info = Location(
        geographic_area,
        station,
        event_number,
        latitude,
        longitude,
    )
    return location_info, rest

@fallible("instrument")
def get_instrument(contents: str) -> tuple[Instrument, str]:
    instrument_dict, rest = get_section(contents, "instrument")
    validate_keys(instrument_dict.keys(), INSTRUMENT_KEYS, "instrument")
    kind = instrument_dict[TYPE] if TYPE in instrument_dict else ""
    model = instrument_dict[MODEL] if MODEL in instrument_dict else ""
    instrument_info = Instrument(
        kind,
        model,
    )
    return instrument_info, rest

@fallible("history")
def get_history(contents: str) -> tuple[History, str]:
    history_dict, rest = get_section(contents, "history")
    validate_keys(history_dict.keys(), HISTORY_KEYS, "history")
    programs = [Program(*elem) for elem in history_dict[PROGRAMS]] if PROGRAMS in history_dict else []
    remarks = history_dict[REMARKS] if REMARKS in history_dict else ""
    history_info = History(
        programs,
        remarks,
    )
    return history_info, rest

@fallible("comments")
def get_comments(contents: str) -> tuple[str, str]:
    rest = contents.lstrip()
    if (m := re.match(r"\*COMMENTS", rest)):
        rest = rest[m.end():]
        lines = []
        while not rest.lstrip().startswith("*"):
            line, rest = rest.split("\n", 1)
            lines.append(line)
        return "\n".join(lines), rest
    else:
        raise ValueError("No COMMENTS section found")

def get_data(contents: str, format: str, records: int) -> tuple[list[typing.Any], str]:
    # TODO: do formatted read of the data
    # TODO: read given number of records
    rest = contents.lstrip()
    if (m := re.match(r"\*END OF HEADER", rest)):
        rest = rest[m.end():]
        data = []
        while len(rest) > 0:
            line, rest = rest.split("\n", 1)
            if len(line) == 0:
                # skip blank lines
                continue
            data.append(line)
        return data, rest
    else:
        raise ValueError("No data in file")
