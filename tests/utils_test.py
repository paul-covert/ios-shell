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
def test_utils_to_datetime_produces_usable_datetime(time):
    time_info = utils.to_datetime(time)
    assert time_info.year == 2015
    assert time_info.month == 3
    assert time_info.day == 16
    assert time_info.tzinfo is not None


@pytest.mark.parametrize(
    "tzname,expected_offset",
    [
        ("UTC", 0),
        ("GMT", 0),
        ("ADT", -3),
        ("CST", -6),
        ("MDT", -6),
        ("MST", -7),
        ("PDT", -7),
        ("PST", -8),
    ],
)
def test_utils_from_iso_converts_time_zones_correctly(tzname, expected_offset):
    for tz in [tzname, tzname.lower(), tzname.capitalize()]:
        time_info = utils.to_datetime(tz + " 2015/03/16 00:00:00")
        assert time_info.tzinfo is not None
        assert time_info.tzinfo.utcoffset(time_info) == datetime.timedelta(
            hours=expected_offset
        )


def test_utils_to_date():
    assert utils.to_date("2000/01/01") == datetime.date(2000, 1, 1)


def test_utils_to_time():
    assert utils.to_time("01:01:01") == datetime.time(
        hour=1, minute=1, second=1, tzinfo=datetime.timezone.utc
    )
    # drop sub-second information
    assert utils.to_time("01:01:01.1") == datetime.time(
        hour=1, minute=1, second=1, tzinfo=datetime.timezone.utc
    )
    # refuse to handle invalid times
    try:
        utils.to_time("25:65:62")
        assert False
    except:
        pass


def test_utils_to_datetime():
    assert utils.to_datetime("2000/01/01 00:00") == datetime.datetime(
        2000, 1, 1, tzinfo=datetime.timezone.utc
    )
    # test for comments present
    assert utils.to_datetime("2000/01/01 00:00 ! comment") == datetime.datetime(
        2000, 1, 1, tzinfo=datetime.timezone.utc
    )


@pytest.mark.parametrize(
    "kind,width,decimals,expected",
    [
        ("F", 8, 3, "F8.3"),
        ("I", 8, 0, "I8"),
        ("YYYY/MM/DD", 0, 0, "A11"),
        ("HH:MM", 0, 0, "A6"),
        ("HH:MM:SS", 0, 0, "A9"),
        ("HH:MM:SS.SS", 0, 0, "A12"),
        ("NQ", 8, 0, "A8"),
        ("' '", 8, 0, "A8"),
        ("F8.3", 0, 0, "F8.3"),
        ("I8", 0, 0, "I8"),
    ],
)
def test_utils_format_string(kind, width, decimals, expected):
    assert utils.format_string(kind, width, decimals) == expected


@pytest.mark.parametrize(
    "contents,expected",
    [
        (
            "UTC 2000/01/01 12:00:00",
            datetime.datetime(2000, 1, 1, hour=12, tzinfo=datetime.timezone.utc),
        ),
        (
            "UTC 2000/01/01",
            datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc),
        ),
        (
            "UTC 2000/01/01 ! comment",
            datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc),
        ),
        (
            "2000-01-01 12:00:00 UTC",
            datetime.datetime(2000, 1, 1, hour=12, tzinfo=datetime.timezone.utc),
        ),
        (
            "2000-01-01 UTC",
            datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc),
        ),
        (
            "GMT 2000/01/01 12:00:00",
            datetime.datetime(2000, 1, 1, hour=12, tzinfo=datetime.timezone.utc),
        ),
        (
            "GMT 2000/01/01",
            datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc),
        ),
        (
            "ADT 2000/01/01 12:00:00",
            datetime.datetime(
                2000,
                1,
                1,
                hour=12,
                tzinfo=datetime.timezone(datetime.timedelta(hours=-3)),
            ),
        ),
        (
            "ADT 2000/01/01",
            datetime.datetime(
                2000,
                1,
                1,
                tzinfo=datetime.timezone(datetime.timedelta(hours=-3)),
            ),
        ),
        (
            "CST 2000/01/01 12:00:00",
            datetime.datetime(
                2000,
                1,
                1,
                hour=12,
                tzinfo=datetime.timezone(datetime.timedelta(hours=-6)),
            ),
        ),
        (
            "CST 2000/01/01",
            datetime.datetime(
                2000,
                1,
                1,
                tzinfo=datetime.timezone(datetime.timedelta(hours=-6)),
            ),
        ),
        (
            "MDT 2000/01/01 12:00:00",
            datetime.datetime(
                2000,
                1,
                1,
                hour=12,
                tzinfo=datetime.timezone(datetime.timedelta(hours=-6)),
            ),
        ),
        (
            "MDT 2000/01/01",
            datetime.datetime(
                2000,
                1,
                1,
                tzinfo=datetime.timezone(datetime.timedelta(hours=-6)),
            ),
        ),
        (
            "MST 2000/01/01 12:00:00",
            datetime.datetime(
                2000,
                1,
                1,
                hour=12,
                tzinfo=datetime.timezone(datetime.timedelta(hours=-7)),
            ),
        ),
        (
            "MST 2000/01/01",
            datetime.datetime(
                2000,
                1,
                1,
                tzinfo=datetime.timezone(datetime.timedelta(hours=-7)),
            ),
        ),
        (
            "PDT 2000/01/01 12:00:00",
            datetime.datetime(
                2000,
                1,
                1,
                hour=12,
                tzinfo=datetime.timezone(datetime.timedelta(hours=-7)),
            ),
        ),
        (
            "PDT 2000/01/01",
            datetime.datetime(
                2000,
                1,
                1,
                tzinfo=datetime.timezone(datetime.timedelta(hours=-7)),
            ),
        ),
        (
            "PST 2000/01/01 12:00:00",
            datetime.datetime(
                2000,
                1,
                1,
                hour=12,
                tzinfo=datetime.timezone(datetime.timedelta(hours=-8)),
            ),
        ),
        (
            "PST 2000/01/01",
            datetime.datetime(
                2000,
                1,
                1,
                tzinfo=datetime.timezone(datetime.timedelta(hours=-8)),
            ),
        ),
    ],
)
def test_utils_from_iso_timezones(contents, expected):
    assert utils.to_datetime(contents) == expected


@pytest.mark.parametrize(
    "lat_str,expected",
    [
        ("50 6.00000 N ! (deg min)", 50.1),
        ("50 6.00000 N", 50.1),
        ("50 6.00000 S ! (deg min)", -50.1),
        ("50 6.00000 S", -50.1),
    ],
)
def test_utils_get_latitude(lat_str, expected):
    assert utils.get_latitude(lat_str) == expected


@pytest.mark.parametrize(
    "lon_str,expected",
    [
        ("124 54.00000 E ! (deg min)", 124.9),
        ("124 54.00000 E", 124.9),
        ("124 54.00000 W ! (deg min)", -124.9),
        ("124 54.00000 W", -124.9),
    ],
)
def test_utils_get_longitude(lon_str, expected):
    assert utils.get_longitude(lon_str) == expected


@pytest.mark.parametrize(
    "contents",
    [
        "",
        "Unknown",
        "Unk.000",
        "?",
    ],
)
def test_utils_to_datetime_rejects_unknown_values(contents):
    assert utils.to_datetime(contents) == datetime.datetime.min
