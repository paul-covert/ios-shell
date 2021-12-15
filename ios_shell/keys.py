"""
This module holds constats for expected keys for each section in an IOS Shell file.

It exists because it is easier to ensure consistent string values by using constants instead of raw strings.
This also means typos are easier to correct.
"""

# *FILE keys
START_TIME = "start time"
END_TIME = "end time"
TIME_ZERO = "time zero"
NUMBER_OF_RECORDS = "number of records"
DATA_DESCRIPTION = "data description"
FILE_TYPE = "file type"
DATA_TYPE = "data type"
NUMBER_OF_CHANNELS = "number of channels"
CHANNELS = "channels"
CHANNEL_DETAIL = "channel detail"
REMARKS = "remarks"
FORMAT = "format"
CONTINUED = "continued"
FILE_KEYS = [
    START_TIME,
    END_TIME,
    TIME_ZERO,
    NUMBER_OF_RECORDS,
    DATA_DESCRIPTION,
    FILE_TYPE,
    DATA_TYPE,
    NUMBER_OF_CHANNELS,
    CHANNELS,
    CHANNEL_DETAIL,
    REMARKS,
    FORMAT,
    CONTINUED,
]

# *ADMINISTRATION keys
MISSION = "mission"
AGENCY = "agency"
COUNTRY = "country"
PROJECT = "project"
SCIENTIST = "scientist"
PLATFORM = "platform"
ADMINISTRATION_KEYS = [
    MISSION,
    AGENCY,
    COUNTRY,
    PROJECT,
    SCIENTIST,
    PLATFORM,
]

# *LOCATION keys
GEOGRAPHIC_AREA = "geographic area"
STATION = "station"
EVENT_NUMBER = "event number"
LATITUDE = "latitude"
LONGITUDE = "longitude"
LOCATION_KEYS = [
    GEOGRAPHIC_AREA,
    STATION,
    EVENT_NUMBER,
    LATITUDE,
    LONGITUDE,
]

# *INSTRUMENT keys
TYPE = "type"
MODEL = "model"
INSTRUMENT_KEYS = [
    TYPE,
    MODEL
]

# *HISTORY keys
PROGRAMS = "programs"
HISTORY_KEYS = [
    PROGRAMS,
    REMARKS,
]
