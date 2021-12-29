import pytest
import datetime

import ios_shell.utils as utils


@pytest.mark.parametrize(
    "time",
    [
        "UTC 2015/03/16 10:36:00.000",
        "UTC 2015/03/16",
    ],
)
def test_utils_from_iso_produces_usable_datetime(time):
    time_info = utils.from_iso(time)
    assert time_info.year == 2015
    assert time_info.month == 3
    assert time_info.day == 16
    assert time_info.tzinfo is not None


def test_utils_from_iso_produces_none_for_empty_string():
    time_info = utils.from_iso("")
    assert time_info is None


@pytest.mark.parametrize(
    "tzname,expected_offset",
    [
        ("UTC", 0),
        ("GMT", 0),
        ("ADT", -3),
        ("MDT", -6),
        ("MST", -7),
        ("PDT", -7),
        ("PST", -8),
    ],
)
def test_utils_from_iso_converts_time_zones_correctly(tzname, expected_offset):
    time_info = utils.from_iso(tzname + " 2015/03/16 00:00:00")
    assert time_info.tzinfo is not None
    assert time_info.tzinfo.utcoffset(time_info) == datetime.timedelta(
        hours=expected_offset
    )


def test_utils_to_date():
    assert utils.to_date("2000/01/01") == datetime.date(2000, 1, 1)


def test_utils_to_time():
    assert utils.to_time("01:00:00") == datetime.time(
        hour=1, tzinfo=datetime.timezone.utc
    )
    # drop sub-second information
    assert utils.to_time("01:00:00.1") == datetime.time(
        hour=1, tzinfo=datetime.timezone.utc
    )


def test_utils_to_datetime():
    assert utils.to_datetime("2000/01/01 00:00") == datetime.datetime(
        2000, 1, 1, tzinfo=datetime.timezone.utc
    )
