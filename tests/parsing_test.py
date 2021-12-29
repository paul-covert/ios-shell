import datetime
import pytest

import ios_shell.parsing as parsing


@pytest.mark.parametrize(
    "contents,expected",
    [
        (
            "*2017/06/30 13:26:49.33",
            datetime.datetime(2017, 6, 30, hour=13, minute=26, second=49),
        ),
        (
            "*1998-10-16 14:17:54.54",
            datetime.datetime(1998, 10, 16, hour=14, minute=17, second=54),
        ),
    ],
)
def test_modified_date(contents, expected):
    expected = expected.replace(tzinfo=datetime.timezone.utc)
    modified, rest = parsing.get_modified_date(contents)
    assert modified == expected
    assert len(rest) == 0


@pytest.mark.parametrize(
    "contents,expected",
    [
        ("*IOS HEADER VERSION 1.10 2011/10/26 2011/10/26", "1.10"),
        ("*IOS HEADER VERSION 2.0      2016/04/28 2016/06/13 IVF16", "2.0"),
        ("*IOS HEADER VERSION 0.4  1992/11/17", "0.4"),
    ],
)
def test_header_version(contents, expected):
    version, rest = parsing.get_header_version(contents)
    assert version.version_no == expected
    assert len(rest) == 0


def test_header_version_fails_with_no_version():
    try:
        parsing.get_header_version("no version string")
        assert False
    except:
        pass


@pytest.mark.parametrize(
    "contents",
    [
        """
*LOCATION
    LATITUDE  :  49 39.00000 N
    LONGITUDE : 126 27.20000 W

*END OF HEADER
        """,
    ],
)
def test_get_location(contents):
    loc, rest = parsing.get_location(contents)
    assert loc.longitude < 0
    assert loc.latitude > 0
    assert rest.strip() == "*END OF HEADER"


def test_get_section():
    section, rest = parsing.get_section(
        """
*FILE
    START TIME          : PST 1933/07/25 15:35:00.000
    NUMBER OF RECORDS   : 10
    DATA DESCRIPTION    : Bottle:Wire
    NUMBER OF CHANNELS  : 6

    $TABLE: CHANNELS
    ! No Name                    Units    Minimum        Maximum
    !--- ----------------------- -------- -------------- --------------
       1 Depth                   metres   1              200
       2 Temperature:Reversing   'deg C'  7.8            16
       3 Salinity:Bottle         ppt      18.64          32.83
       4 Oxygen:Dissolved        mL/L     1.932          7.924
       5 Silicate                umol/L   6.8            38.2
       6 Phosphate               umol/L   0.55           2.25
    $END

    $TABLE: CHANNEL DETAIL
    ! No  Pad     Start  Width  Format  Type  Decimal_Places
    !---  ------  -----  -----  ------  ----  --------------
       1  -99.9   ' '        6  F       ' '     0
       2  -99.99  ' '        7  F       ' '     2
       3  -99.99  ' '        7  F       ' '     2
       4  -99.99  ' '        7  F       ' '     2
       5  -99.99  ' '        6  F       ' '     1
       6  -99.99  ' '        7  F       ' '     2
    $END

*END OF HEADER
        """,
        "file",
    )
    assert rest.strip() == "*END OF HEADER"
    assert "channels" in section


def test_get_data():
    data, rest = parsing.get_data(
        """
*END OF HEADER
200. 2000/01/01 00:00:00 100.000 other
        """,
        "(F4.0,A11,A10,F8.3,A6)",
        1,
    )
    assert len(rest.strip()) == 0

    date = data[0][1]
    time = data[0][2]
    value = data[0][3]
    extra = data[0][4]

    assert isinstance(date, datetime.date)
    assert date == datetime.date(2000, 1, 1)

    assert isinstance(time, datetime.time)
    assert time == datetime.time(hour=0, tzinfo=datetime.timezone.utc)

    assert isinstance(value, float)
    assert value == 100.000

    assert isinstance(extra, str)
    assert extra == "other"
