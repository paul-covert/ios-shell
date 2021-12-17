from dataclasses import dataclass
import datetime
from typing import Any, Dict, List, Union

EMPTY = ["", "' '", "n/a"]
NAN = float("NaN")


@dataclass
class Version:
    version_no: str
    date1: str
    date2: str
    tag: str = ""


class Channel:
    no: int  # acts as an identifier
    name: str
    units: str
    minimum: float
    maximum: float

    def __init__(
        self,
        no="",
        name="",
        units="",
        minimum="",
        maximum="",
    ):
        self.no = int(no)
        self.name = name.strip()
        self.units = units.strip()
        # FIXME: remove when no longer relevant
        if minimum.strip().upper() == "O":
            minimum = "0"
        if maximum.strip().upper() == "O":
            maximum = "0"
        self.minimum = NAN if minimum.strip() in EMPTY else float(minimum)
        self.maximum = NAN if maximum.strip() in EMPTY else float(maximum)


class ChannelDetail:
    no: int  # acts as an identifier
    pad: float
    start: str
    width: int
    format: str
    type: str
    decimal_places: int = -1

    def __init__(
        self,
        no="",
        pad="",
        start="",
        width="",
        format="",
        type="",
        decimal_places="",
    ):
        self.no = int(no)
        self.pad = float(pad) if pad.strip() not in EMPTY else NAN
        self.start = start
        self.width = int(width) if width.strip() not in EMPTY else 0
        self.format = format
        self.type = type
        self.decimal_places = (
            int(decimal_places) if decimal_places.strip() not in EMPTY else 0
        )


@dataclass
class FileInfo:
    start_time: datetime.datetime
    end_time: datetime.datetime
    time_zero: datetime.datetime
    number_of_records: int
    data_description: str
    file_type: str
    format: str
    data_type: str
    number_of_channels: int
    channels: List[Channel]
    channel_details: List[ChannelDetail]
    remarks: str
    raw: Dict[str, Any]


@dataclass
class Administration:
    mission: str
    agency: str
    country: str
    project: str
    scientist: str
    platform: str
    remarks: str
    raw: Dict[str, Any]


@dataclass
class Location:
    geographic_area: str
    station: str
    event_number: int
    latitude: float
    longitude: float
    water_depth: float
    remarks: str
    raw: Dict[str, Any]


@dataclass
class Instrument:
    type: str
    model: str
    remarks: str
    raw: Dict[str, Any]


@dataclass
class Program:
    name: str
    version: str
    date: datetime.date
    time: datetime.time
    records_in: int
    records_out: int


@dataclass
class Raw:
    channels: List[List[str]]
    remarks: str
    raw: Dict[str, Any]


@dataclass
class History:
    programs: List[Program]
    remarks: str
    raw: Dict[str, Any]


@dataclass
class Calibration:
    corrected_channels: List[Dict[str, str]]
    raw: Dict[str, Any]
