from dataclasses import dataclass
import datetime

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
        self.name = name
        self.units = units
        self.minimum = float(minimum)
        self.maximum = float(maximum)

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
        self.no = int(no)
        self.pad = float(pad)
        self.start = start
        self.width = int(width) if width not in ["", "' '"] else 0
        self.format = format
        self.type = type
        self.decimal_places = int(decimal_places) if decimal_places not in ["", "' '"] else 0

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

@dataclass
class Administration:
    mission: str
    agency: str
    country: str
    project: str
    scientist: str
    platform: str

@dataclass
class Location:
    geographic_area: str
    station: str
    event_number: int
    latitude: float
    longitude: float

@dataclass
class Instrument:
    type: str
    model: str

@dataclass
class Program:
    name: str
    version: str
    date: datetime.date
    time: datetime.time
    records_in: int
    records_out: int

@dataclass
class History:
    programs: list[Program]
    remarks: str


