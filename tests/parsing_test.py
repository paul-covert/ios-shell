import datetime
import math
import pytest

import ios_shell.parsing as parsing
from ios_shell.keys import *


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
    modified, rest = parsing.get_modified_date([contents])
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
    version, rest = parsing.get_header_version([contents])
    assert version.version_no == expected
    assert len(rest) == 0


def test_header_version_fails_with_no_version():
    try:
        parsing.get_header_version([])
        assert False
    except:
        pass


def test_get_file():
    file, rest = parsing.get_file(
        """*FILE
    START TIME          : PST 1933/07/25 15:35:00.000
    END TIME            : PST 1933/07/25 15:36:00.000
    TIME Zero           : PST 1933/07/25 15:35:00.000
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

    $REMARKS
        words words words
    $END

*END OF HEADER""".splitlines()
    )
    assert len(file.channels) == len(file.channel_details)
    tz = datetime.timezone(datetime.timedelta(hours=-8))
    assert file.start_time == datetime.datetime(
        1933, 7, 25, hour=15, minute=35, tzinfo=tz
    )
    assert file.end_time == datetime.datetime(
        1933, 7, 25, hour=15, minute=36, tzinfo=tz
    )
    assert file.time_zero == datetime.datetime(
        1933, 7, 25, hour=15, minute=35, tzinfo=tz
    )
    assert file.number_of_records == 10
    assert file.number_of_channels == 6
    assert file.data_description == "Bottle:Wire"
    assert file.format == "(F6.0,F7.2,F7.2,F7.2,F6.1,F7.2)"
    assert file.remarks.strip() == "words words words"
    assert START_TIME in file.raw

    assert rest == ["*END OF HEADER"]

    # minimal file section
    file, _ = parsing.get_file(
        """*FILE
    NUMBER OF RECORDS   : 10
    NUMBER OF CHANNELS  : 6
    FORMAT              : (F6.0,F7.2,F7.2,
        CONTINUED       : F7.2,F6.1,F7.2)

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
       1  -99.9   ' '    ' '    ' '     ' '   ' '
       2  -99.99  ' '    ' '    ' '     ' '   ' '
       3  -99.99  ' '    ' '    ' '     ' '   ' '
       4  -99.99  ' '    ' '    ' '     ' '   ' '
       5  -99.99  ' '    ' '    ' '     ' '   ' '
       6  -99.99  ' '    ' '    ' '     ' '   ' '
    $END

*END OF HEADER""".splitlines()
    )
    assert file.start_time == datetime.datetime.min
    assert file.end_time == datetime.datetime.min
    assert file.time_zero == datetime.datetime.min
    assert file.file_type == ""
    assert file.data_description == ""
    assert file.data_type == ""
    assert file.remarks == ""
    assert file.format == "(F6.0,F7.2,F7.2,F7.2,F6.1,F7.2)"


def test_get_administration():
    admin, rest = parsing.get_administration(
        """*ADMINISTRATION
    MISSION   : 1930-01
    AGENCY    : UBC
    COUNTRY   : Canada
    PROJECT   : Kitimat
    SCIENTIST : C. Hannah
    PLATFORM  : Tully
    $REMARKS
        words words words
    $END

*END OF HEADER""".splitlines()
    )
    assert admin.mission == "1930-01"
    assert admin.agency == "UBC"
    assert admin.country == "Canada"
    assert admin.scientist == "C. Hannah"
    assert admin.project == "Kitimat"
    assert admin.platform == "Tully"
    assert admin.remarks.strip() == "words words words"
    assert rest == ["*END OF HEADER"]
    assert MISSION in admin.raw

    admin, _ = parsing.get_administration(
        """*ADMINISTRATION

*END OF HEADER""".splitlines()
    )
    assert admin.mission == ""
    assert admin.agency == ""
    assert admin.country == ""
    assert admin.project == ""
    assert admin.scientist == ""
    assert admin.platform == ""
    assert admin.remarks == ""


def test_get_location():
    loc, rest = parsing.get_location(
        """*LOCATION
    GEOGRAPHIC AREA : Strait of Georgia
    STATION         : SOGN
    EVENT NUMBER    : 13
    LATITUDE        :  49 39.00000 N
    LONGITUDE       : 126 27.20000 W
    WATER DEPTH     : 332
    $REMARKS
        words words words
    $END

*END OF HEADER""".splitlines()
    )
    assert loc.longitude < 0
    assert loc.latitude > 0
    assert loc.geographic_area == "Strait of Georgia"
    assert loc.station == "SOGN"
    assert loc.event_number == 13
    assert loc.water_depth == 332.0
    assert loc.remarks.strip() == "words words words"
    assert LONGITUDE in loc.raw
    assert rest == ["*END OF HEADER"]

    loc, _ = parsing.get_location(
        """*LOCATION
    LATITUDE        :  49 39.00000 N
    LONGITUDE       : 126 27.20000 W

*END OF HEADER""".splitlines()
    )
    assert loc.geographic_area == ""
    assert loc.station == ""
    assert loc.event_number == -1
    assert loc.water_depth == -1
    assert loc.remarks == ""

    loc, _ = parsing.get_location(
        """*LOCATION
    LATITUDE        :  49 39.00000 N
    LONGITUDE       : 126 27.20000 W
    WATER DEPTH     : Unknown

*END OF HEADER""".splitlines()
    )
    assert loc.geographic_area == ""
    assert loc.station == ""
    assert loc.event_number == -1
    assert loc.water_depth == -1
    assert loc.remarks == ""


def test_get_instrument():
    instrument, rest = parsing.get_instrument(
        """*INSTRUMENT
    TYPE          : bottle
    MODEL         : abcd
    SERIAL NUMBER : 123456
    DEPTH         : 456
    $REMARKS
        words words words
    $END

*END OF HEADER""".splitlines()
    )
    assert instrument.type == "bottle"
    assert instrument.model == "abcd"
    assert instrument.serial_number == "123456"
    assert instrument.depth == 456
    assert instrument.remarks.strip() == "words words words"
    assert rest == ["*END OF HEADER"]

    instrument, _ = parsing.get_instrument(
        """*INSTRUMENT

*END OF HEADER""".splitlines()
    )
    assert instrument.type == ""
    assert instrument.model == ""
    assert instrument.serial_number == ""
    assert math.isnan(instrument.depth)
    assert instrument.remarks.strip() == ""


def test_get_raw():
    raw, rest = parsing.get_raw(
        """*RAW
    NUMBER OF RECORDS   : 99999
    $TABLE: CHANNELS
    !                                Averaging (day hr min sec ms)
    !Name                 Raw Units  Interval   Time Lag
    !-------------------- ---------  ---------  -----------
     PRESSURE             ' DBAR'
     TEMPERATURE          '    C'
     'CONDUCTIVITY RATIO' RATIO
    $END
    $REMARKS
        words words words
    $END

*END OF HEADER""".splitlines()
    )
    assert raw.remarks.strip() == "words words words"
    assert NUMBER_OF_RECORDS in raw.raw
    assert rest == ["*END OF HEADER"]

    raw, _ = parsing.get_raw(
        """*RAW

*END OF HEADER""".splitlines()
    )
    assert raw.remarks == ""
    assert NUMBER_OF_RECORDS not in raw.raw


def test_get_history():
    history, rest = parsing.get_history(
        """*HISTORY
    $TABLE: PROGRAMS
    !   Name     Vers   Date       Time     Recs In   Recs Out
    !   -------- ------ ---------- -------- --------- ---------
        RCM_CNVT 1.1    2019/07/18 10:36:44         0      2001
    $END
    $REMARKS
        words words words
    $END

*END OF HEADER""".splitlines()
    )
    assert len(history.programs) > 0
    assert history.remarks.strip() == "words words words"
    assert rest == ["*END OF HEADER"]

    history, _ = parsing.get_history(
        """*HISTORY

*END OF HEADER""".splitlines()
    )
    assert len(history.programs) == 0
    assert history.remarks == ""


def test_get_calibration():
    calibration, rest = parsing.get_calibration(
        """*CALIBRATION
    $TABLE: CORRECTED CHANNELS
    !   Name     Units  Fmla Pad    Coefficients
    !   -------- ------ ---- ------ ------------
        Oxygen   mg/l     10 -99.99 () (0 0.223916E-01)
    $END
    $REMARKS
        words words words
    $END
*END OF HEADER""".splitlines()
    )
    assert len(calibration.corrected_channels) > 0
    assert calibration.remarks.strip() == "words words words"
    assert rest == ["*END OF HEADER"]

    calibration, _ = parsing.get_calibration(
        """*CALIBRATION

*END OF HEADER""".splitlines()
    )
    assert len(calibration.corrected_channels) == 0
    assert calibration.remarks == ""


def test_get_deployment():
    deployment, rest = parsing.get_deployment(
        """*DEPLOYMENT
    MISSION             : 1930-01
    TYPE                : some type
    TIME ANCHOR DROPPED : UTC 1930/01/01 00:00:00
    $REMARKS
        words words words
    $END

*END OF HEADER""".splitlines()
    )
    assert deployment.mission == "1930-01"
    assert deployment.type == "some type"
    assert deployment.anchor_dropped == datetime.datetime(
        1930, 1, 1, tzinfo=datetime.timezone.utc
    )
    assert deployment.remarks.strip() == "words words words"
    assert rest == ["*END OF HEADER"]

    deployment, _ = parsing.get_deployment(
        """*DEPLOYMENT

*END OF HEADER""".splitlines()
    )
    assert deployment.mission == ""
    assert deployment.type == ""
    assert deployment.anchor_dropped == datetime.datetime.min
    assert deployment.remarks == ""


def test_get_recovery():
    recovery, rest = parsing.get_recovery(
        """*RECOVERY
    MISSION              : 1930-01
    TIME ANCHOR RELEASED : UTC 1930/01/01 00:00:00
    $REMARKS
        words words words
    $END

*END OF HEADER""".splitlines()
    )
    assert recovery.mission == "1930-01"
    assert recovery.anchor_released == datetime.datetime(
        1930, 1, 1, tzinfo=datetime.timezone.utc
    )
    assert recovery.remarks.strip() == "words words words"
    assert rest == ["*END OF HEADER"]

    recovery, _ = parsing.get_recovery(
        """*RECOVERY

*END OF HEADER""".splitlines()
    )
    assert recovery.mission == ""
    assert recovery.anchor_released == datetime.datetime.min
    assert recovery.remarks == ""


def test_get_comments():
    comments, rest = parsing.get_comments(
        """*COMMENTS
    words words words
    even more words
*END OF HEADER""".splitlines()
    )
    assert comments == "    words words words\n    even more words"
    assert rest == ["*END OF HEADER"]


def test_get_data():
    data, rest = parsing.get_data(
        """
200. 2000/01/01 00:00:00 100.000 other

300. 2000/01/01 00:00:01 100.001 other
        """,
        "(F4.0,A11,A10,F8.3,A6)",
        2,
    )
    assert len(rest.strip()) == 0
    assert len(data) == 2

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


def test_get_section_error_message():
    try:
        parsing.get_section(["*END OF HEADER"], "location")
        assert False
    except Exception as e:
        assert "LOCATION" in "".join(e.args)
        assert "*END OF HEADER" in "".join(e.args)


def test_get_section_array():
    section, _ = parsing.get_section(
        """*RAW
    $ARRAY: BIN DEPTHS (M)
        287.1
        289.1
    $END
*END OF HEADER""".splitlines(),
        "raw",
    )

    arr = section["bin depths (m)"]
    assert arr[0].strip() == "287.1"
    assert arr[1].strip() == "289.1"
