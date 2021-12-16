import datetime
import fortranformat as ff
import functools
import logging
import re
import typing

from . import sections, utils
from .keys import *


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


DATE_STR = r"\d{4}[/-]\d{2}[/-]\d{2}"
TIME_STR = r"\d{2}:\d{2}:\d{2}(.\d*)?"


def get_modified_date(contents: str) -> tuple[datetime.datetime, str]:
    rest = contents.lstrip()
    if m := re.match(fr"\*({DATE_STR} {TIME_STR})", rest):
        rest = rest[m.end() :]
        # trim sub-second information to make parsing using datetime easier
        raw_datetime = m.group(1).replace("/", "-").split(".")[0]
        return (datetime.datetime.fromisoformat(raw_datetime), rest)
    else:
        raise ValueError("No modified date at start of string")


def get_header_version(contents: str) -> tuple[sections.Version, str]:
    # TODO: capture all sections of version
    rest = contents.lstrip()
    if m := re.match(
        fr"\*IOS HEADER VERSION +(?P<version_no>\d+.\d+) +(?P<date1>{DATE_STR})( +(?P<date2>{DATE_STR})( +(?P<tag>[a-zA-Z0-9.]+))?)?",
        rest,
    ):
        rest = rest[m.end() :]
        return (sections.Version(**m.groupdict("")), rest)
    else:
        raise ValueError("No header version in string")


def get_section(contents: str, section_name: str) -> tuple[dict[str, typing.Any], str]:
    rest = contents.lstrip()
    prefix = f"*{section_name.upper()}\n"
    section_info = {}
    if not rest.startswith(prefix):
        first_line = rest.split("\n", 1)[0]
        raise ValueError(
            f"{section_name.upper()} section not present, found {first_line} instead"
        )
    rest = rest[len(prefix) :]
    while not utils.is_section_heading(rest.lstrip()):
        rest = rest.lstrip()
        if rest.startswith("!"):
            # skip comments
            rest = rest.split("\n", 1)[1]
            continue
        elif m := re.match(r"\$TABLE: ([^\n]+)\n", rest):
            # handle table
            table_name = m.group(1).lower()
            rest = rest[m.end() :]
            # table column names
            line, rest = rest.split("\n", 1)
            column_names_line = line
            # table column mask
            line, rest = rest.split("\n", 1)
            mask = [c == "-" for c in line]
            # apply column mask in case names contain spaces
            column_names = [
                name.lower().strip().replace(" ", "_")
                for name in utils.apply_column_mask(column_names_line, mask)
            ]
            # values
            section_info[table_name] = []
            while not rest.lstrip().startswith("$END"):
                line, rest = rest.split("\n", 1)
                section_info[table_name].append(
                    {
                        column_names[i]: v
                        for i, v in enumerate(utils.apply_column_mask(line, mask))
                    }
                )
            _, rest = rest.lstrip().split("\n", 1)
        elif m := re.match(r"\$REMARKS", rest):
            # handle remarks
            rest = rest[m.end() :]
            remarks = []
            while not rest.lstrip().startswith("$END"):
                line, rest = rest.split("\n", 1)
                remarks.append(line)
            section_info[REMARKS] = "\n".join(remarks)
            _, rest = rest.lstrip().split("\n", 1)
        else:
            # handle single entry
            line, rest = rest.split("\n", 1)
            key, value = line.split(":", 1)
            section_info[key.strip().lower()] = value.strip()
    return section_info, rest


def get_file(contents: str) -> tuple[sections.FileInfo, str]:
    file_dict, rest = get_section(contents, "file")
    start_time = (
        utils.to_iso(file_dict[START_TIME])
        if START_TIME in file_dict
        else datetime.datetime.fromtimestamp(0)
    )
    end_time = (
        utils.to_iso(file_dict[END_TIME])
        if END_TIME in file_dict
        else datetime.datetime.fromtimestamp(0)
    )
    time_zero = (
        utils.to_iso(file_dict[TIME_ZERO])
        if TIME_ZERO in file_dict
        else datetime.datetime.fromtimestamp(0)
    )
    number_of_records = int(file_dict[NUMBER_OF_RECORDS])
    data_description = (
        file_dict[DATA_DESCRIPTION] if DATA_DESCRIPTION in file_dict else ""
    )
    file_type = file_dict[FILE_TYPE] if FILE_TYPE in file_dict else ""
    number_of_channels = int(file_dict[NUMBER_OF_CHANNELS])
    channels = (
        [sections.Channel(**elem) for elem in file_dict[CHANNELS]]
        if CHANNELS in file_dict
        else []
    )
    channel_details = (
        [sections.ChannelDetail(**elem) for elem in file_dict[CHANNEL_DETAIL]]
        if CHANNEL_DETAIL in file_dict
        else []
    )
    remarks = file_dict[REMARKS] if REMARKS in file_dict else ""
    data_type = file_dict[DATA_TYPE] if DATA_TYPE in file_dict else ""
    to_remove = " \n\t'"
    if FORMAT in file_dict:
        format_str = file_dict[FORMAT].strip(to_remove)
        if CONTINUED in file_dict:
            format_str += file_dict[CONTINUED].strip(to_remove)
    else:
        format_info = [
            utils.format_string(detail.format, detail.width, detail.decimal_places)
            for detail in channel_details
        ]
        format_str = "({})".format(",".join(format_info))
    file_info = sections.FileInfo(
        start_time=start_time,
        end_time=end_time,
        time_zero=time_zero,
        number_of_records=number_of_records,
        data_description=data_description,
        file_type=file_type,
        format=format_str,
        data_type=data_type,
        number_of_channels=number_of_channels,
        channels=channels,
        channel_details=channel_details,
        remarks=remarks,
        raw=file_dict,
    )
    return file_info, rest


def get_administration(contents: str) -> tuple[sections.Administration, str]:
    admin_dict, rest = get_section(contents, "administration")
    mission = admin_dict[MISSION] if MISSION in admin_dict else ""
    agency = admin_dict[AGENCY] if AGENCY in admin_dict else ""
    country = admin_dict[COUNTRY] if COUNTRY in admin_dict else ""
    project = admin_dict[PROJECT] if PROJECT in admin_dict else ""
    scientist = admin_dict[SCIENTIST] if SCIENTIST in admin_dict else ""
    platform = admin_dict[PLATFORM] if PLATFORM in admin_dict else ""
    remarks = admin_dict[REMARKS] if REMARKS in admin_dict else ""
    admin_info = sections.Administration(
        mission=mission,
        agency=agency,
        country=country,
        project=project,
        scientist=scientist,
        platform=platform,
        remarks=remarks,
        raw=admin_dict,
    )
    return admin_info, rest


def get_location(contents: str) -> tuple[sections.Location, str]:
    location_dict, rest = get_section(contents, "location")
    geographic_area = (
        location_dict[GEOGRAPHIC_AREA] if GEOGRAPHIC_AREA in location_dict else ""
    )
    station = location_dict[STATION] if STATION in location_dict else ""
    event_number = (
        int(location_dict[EVENT_NUMBER]) if EVENT_NUMBER in location_dict else -1
    )
    latitude = utils.get_latitude(location_dict[LATITUDE])
    longitude = utils.get_longitude(location_dict[LONGITUDE])
    water_depth = (
        float(location_dict[WATER_DEPTH])
        if WATER_DEPTH in location_dict and location_dict[WATER_DEPTH] not in [""]
        else -1
    )
    remarks = location_dict[REMARKS] if REMARKS in location_dict else ""
    location_info = sections.Location(
        geographic_area=geographic_area,
        station=station,
        event_number=event_number,
        latitude=latitude,
        longitude=longitude,
        water_depth=water_depth,
        remarks=remarks,
        raw=location_dict,
    )
    return location_info, rest


def get_instrument(contents: str) -> tuple[sections.Instrument, str]:
    instrument_dict, rest = get_section(contents, "instrument")
    kind = instrument_dict[TYPE] if TYPE in instrument_dict else ""
    model = instrument_dict[MODEL] if MODEL in instrument_dict else ""
    remarks = instrument_dict[REMARKS] if REMARKS in instrument_dict else ""
    instrument_info = sections.Instrument(
        type=kind,
        model=model,
        remarks=remarks,
        raw=instrument_dict,
    )
    return instrument_info, rest


def get_history(contents: str) -> tuple[sections.History, str]:
    history_dict, rest = get_section(contents, "history")
    programs = (
        [sections.Program(*elem) for elem in history_dict[PROGRAMS]]
        if PROGRAMS in history_dict
        else []
    )
    remarks = history_dict[REMARKS] if REMARKS in history_dict else ""
    history_info = sections.History(
        programs=programs,
        remarks=remarks,
        raw=history_dict,
    )
    return history_info, rest


def get_calibration(contents: str) -> tuple[sections.Calibration, str]:
    calibration_dict, rest = get_section(contents, "calibration")
    corrected_channels = (
        calibration_dict[CORRECTED_CHANNELS]
        if CORRECTED_CHANNELS in calibration_dict
        else []
    )
    calibration_info = sections.Calibration(
        corrected_channels=corrected_channels,
        raw=calibration_dict,
    )
    return calibration_info, rest


def get_raw(contents: str) -> tuple[sections.Raw, str]:
    raw_dict, rest = get_section(contents, "raw")
    channels = raw_dict[CHANNELS] if CHANNELS in raw_dict else []
    remarks = raw_dict[REMARKS] if REMARKS in raw_dict else ""
    raw_info = sections.Raw(
        channels=channels,
        remarks=remarks,
        raw=raw_dict,
    )
    return raw_info, rest


def get_comments(contents: str) -> tuple[str, str]:
    rest = contents.lstrip()
    if m := re.match(r"\*COMMENTS\n", rest):
        rest = rest[m.end() :]
        lines = []
        while not utils.is_section_heading(rest):
            line, rest = rest.split("\n", 1)
            lines.append(line)
        return "\n".join(lines), rest
    else:
        raise ValueError("No COMMENTS section found")


def _replace_unexpected(s: str) -> str:
    unexpected = ["?", "*"]
    for c in unexpected:
        s = s.replace(c, " ")
    return s

def get_data(contents: str, format: str, records: int) -> tuple[list[typing.Any], str]:
    rest = contents.lstrip()
    if m := re.match(r"\*END OF HEADER\n", rest):
        rest = rest[m.end() :]
        lines = rest.split("\n")
        while "" in lines:
            lines.remove("")
        reader = ff.FortranRecordReader(format)
        # FIXME: This is a quick workaround for the problem of unexpected characters in the data section of the file.
        # Ideally such characters never show up, but in case they do, we may need a more robust method of handling them.
        data = [reader.read(_replace_unexpected(line)) for line in lines[:records]]
        rest = "\n".join(lines[records:])
        return data, rest
    else:
        raise ValueError("No data in file")
