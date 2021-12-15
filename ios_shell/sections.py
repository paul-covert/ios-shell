from dataclasses import dataclass
import datetime
import numpy
import typing

@dataclass
class Version:
    version_no: str
    date1: str
    date2: str
    tag: str = ""

class Channel:
    no: int # acts as an identifier
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
        empty = ["' '", "n/a"]
        self.minimum = numpy.nan if minimum.strip() in empty else float(minimum)
        self.maximum = numpy.nan if maximum.strip() in empty else float(maximum)

class ChannelDetail:
    no: int # acts as an identifier
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
        empty = ["", "' '"]
        self.no = int(no)
        self.pad = float(pad) if pad.strip() not in empty else numpy.nan
        self.start = start
        self.width = int(width) if width.strip() not in empty else 0
        self.format = format
        self.type = type
        self.decimal_places = int(decimal_places) if decimal_places.strip() not in empty else 0

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
    channels: list[Channel]
    channel_details: list[ChannelDetail]
    remarks: str
    raw: dict[str, typing.Any]

@dataclass
class Administration:
    mission: str
    agency: str
    country: str
    project: str
    scientist: str
    platform: str
    remarks: str
    raw: dict[str, typing.Any]

@dataclass
class Location:
    geographic_area: str
    station: str
    event_number: int
    latitude: float
    longitude: float
    water_depth: float
    remarks: str
    raw: dict[str, typing.Any]

@dataclass
class Instrument:
    type: str
    model: str
    remarks: str
    raw: dict[str, typing.Any]

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
    channels: list[list[str]]
    remarks: str
    raw: dict[str, typing.Any]

@dataclass
class History:
    programs: list[Program]
    remarks: str
    raw: dict[str, typing.Any]

@dataclass
class Calibration:
    corrected_channels: list[dict[str, str]]
    raw: dict[str, typing.Any]
