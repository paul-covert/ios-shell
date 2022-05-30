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
    "format,kind,width,decimals,expected",
    [
        ("F", "R4", 8, 3, "F8.3"),
        ("I", "I", 8, 0, "I8"),
        ("YYYY/MM/DD", "D", 0, 0, "A11"),
        ("YYYY-MM-DD", "D", 0, 0, "A11"),
        ("HH:MM", "T", 0, 0, "A6"),
        ("HH:MM:SS", "T", 0, 0, "A9"),
        ("HH:MM:SS.SS", "T", 0, 0, "A12"),
        ("NQ", "C", 8, 0, "A8"),
        ("' '", "C", 8, 0, "A8"),
        ("F8.3", "R4", 0, 0, "F8.3"),
        ("I8", "I", 0, 0, "I8"),
        ("HH:MM", "DT", 0, 0, "A17"),
    ],
)
def test_utils_format_string(format, kind, width, decimals, expected):
    assert utils.format_string(format, kind, width, decimals) == expected


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


@pytest.mark.parametrize(
    "line",
    [
        "    ! --- ------ ---- --",
    ],
)
def test_utils_is_table_mask(line):
    assert utils.is_table_mask(line)


@pytest.mark.parametrize(
    "line",
    [
        "! not a table mask",
        "! --- ------ ---- --",  # this is a formatting mask for data
    ],
)
def test_utils_is_table_mask_fails(line):
    assert not utils.is_table_mask(line)


@pytest.mark.parametrize(
    "data,mask,expected",
    [
        ("words words words", "----- ----- -----", ["words", "words", "words"]),
        ("words words", "----- ----- -----", ["words", "words", "     "]),
        ("wordswordswords", "----- ----- -----", ["words", "ordsw", "rds  "]),
        ("words words words", "----- -----", ["words", "words words"]),
    ],
)
def test_utils_apply_column_mask(data, mask, expected):
    actual = utils.apply_column_mask(data, mask)
    assert actual == expected


@pytest.mark.parametrize(
    "description,expected",
    [
        ("30 0 0 0 0", datetime.timedelta(days=30)),
        ("0 30 0 0 0", datetime.timedelta(hours=30)),
        ("0 0 30 0 0", datetime.timedelta(minutes=30)),
        ("0 0 0 30 0", datetime.timedelta(seconds=30)),
        ("0 0 0 0 30", datetime.timedelta(milliseconds=30)),
        ("n/a", datetime.timedelta(minutes=0)),
    ],
)
def test_utils_to_increment(description, expected):
    actual = utils.to_increment(description)
    assert actual == expected


@pytest.mark.parametrize(
    "list,expected",
    [
        ([], False),
        ([1], False),
        ([1, 2], True),
        ([1, 2, 3], True),
    ],
)
def test_has_many_values(list, expected):
    assert utils.has_many_values(list) == expected


@pytest.mark.parametrize(
    "list,expected",
    [
        ([], False),
        ([1], True),
        ([1, 1], True),
        ([1, 2], False),
        ([1, 1, 1], True),
        ([1, 1, 2], False),
        ([1, 2, 3], False),
    ],
)
def test_all_same(list, expected):
    assert utils.all_same(list) == expected


@pytest.mark.pandas
@pytest.mark.parametrize(
    "list,names",
    [
        ([[1, 2, 3], [4, 5, 6]], ["id", "T", "oxy"]),
    ],
)
def test_list_to_pandas(list, names):
    import pandas

    df = utils.list_to_pandas(list, names)
    assert all(df.columns == pandas.Index(names))
    for i, row in df.iterrows():
        assert all(o == d for o, d in zip(list[i], row))
