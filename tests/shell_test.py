import datetime
import pytest
import os

import ios_shell as shell
import ios_shell.sections as sections


def test_shell_read_data():
    contents = """*2018/06/22 09:04:04.94
*IOS HEADER VERSION 2.0      2016/04/28 2016/06/13 IVF16

*FILE
    START TIME          : UTC 2015/03/16 10:36:00.000
    NUMBER OF RECORDS   : 1
    DATA DESCRIPTION    : Bottle:Wire
    FILE TYPE           : ASCII
    NUMBER OF CHANNELS  : 4

    $TABLE: CHANNELS
    ! No Name                         Units    Minimum        Maximum
    !--- ---------------------------- -------- -------------- --------------
       1 Depth:Nominal                metres   0              0
       2 Sample_Number                n/a      5              5
       3 Chlorophyll:Extracted        mg/m^3   30.69          30.69
       4 Flag:Chlorophyll:Extracted   ' '
    $END

    $TABLE: CHANNEL DETAIL
    ! No  Pad   Start  Width  Format  Type  Decimal_Places
    !---  ----  -----  -----  ------  ----  --------------
       1  -99   ' '        6  F       R4      0
       2  -99   ' '        5  I       I       0
       3  -99   ' '        7  F       R4      2
       4  ' '   ' '        3  NQ      C     ' '
    $END

*ADMINISTRATION
    MISSION             : 1993-001

*LOCATION
    LATITUDE            :  50   6.00000 N  ! (deg min)
    LONGITUDE           : 124  54.00000 W  ! (deg min)

*COMMENTS
words words words

*END OF HEADER
    0.    5  30.69 6"""
    info = shell.ShellFile.fromcontents(contents)
    assert info.filename == "bare string"
    assert len(info.data) == info.file.number_of_records
    assert isinstance(info.data[0][0], float)
    assert (
        info.file.channels[0].minimum
        <= info.data[0][0]
        <= info.file.channels[0].maximum
    )
    loc = info.get_location()
    assert loc["latitude"] == 50.1
    assert loc["longitude"] == -124.9
    assert info.get_time() != datetime.datetime.min
    assert info.comments.strip() == "words words words"

    # test for end time
    contents = (
        contents.replace("START", "END")
        .replace("*COMMENTS", "")
        .replace("words words words", "")
    )
    info = shell.ShellFile.fromcontents(contents)
    assert info.get_time() != datetime.datetime.min
    assert info.comments.strip() == ""


@pytest.mark.parametrize(
    "file_name",
    [
        "00200001.med",
        "1930-031-0001.bot",
        "1930-031-0010.bot",
        "1930-099-0001.bot",
        "1930-003-0058.bot",
        "1933-001-0001.bot",
        "1933-001-0004.bot",
        "1938-019-0001.bot",
        "1950-001-0033.bot",
        "1950-046-0002.bot",
        "1952-002-0018.bot",
        "1954-010-0001.bot",
        "1954-010-0002.bot",
        "1956-001-9001.bot",
        "1958-004-0001.bot",
        "1959-040-0013.bot",
        "1985-041-0004.bot",
        "1986-033-0003.bot",
        "1987-070-0001.bot",
        "1991-017-0003.bot",
        "1991-017-0010.bot",
        "1992-016-0001.bot",
        "1994-031-0512.ctd",
        "1996-036-0005.che",
        "1996-038-0077.che",
        "1997-033-0003.ctd",
        "1998-015-8001.bot",
        "2002-008-0026.ctd",
        "2002-030-8008.bot",
        "2002-043-Cape-Beale-Lighthouse.bot",
        "2004-016-0013.ctd",
        "2005-010-0016.che",
        "2008-010-0001.che",
        "2008-026-0089.che",
        "2015-022-0031.bot",
        "51010002.ubc",
        "74010003.ubc",
    ],
)
def test_shell_fromfile(file_name):
    full_file_name = os.path.join(os.path.dirname(__file__), "data", file_name)
    info = shell.ShellFile.fromfile(full_file_name, process_data=False)
    assert not info.data_is_processed()
    info.process_data()
    assert isinstance(info.data, list)
    assert info.data_is_processed()

    info = shell.ShellFile.fromfile(full_file_name, process_data=True)
    assert info.data_is_processed()
    assert len(info.data) == info.file.number_of_records


# for test files with either no data or too much data to reasonably process
@pytest.mark.parametrize(
    "file_name",
    [
        "2008-007-0002.tob",
        "BP2_20130705_20130810_0114m.ctd",
        "B515_19750812_19750901a_0002m.cur",
        "cmp1_20160127_20160520_0193m.ctd",
        "dev1_20150727_20160517_0152m.ctd",
        "nep3_20061220_20070117_0093m.adcp",
        "prc1_20190809_20200514_0037m.adcp",
    ],
)
def test_shell_fromfile_just_header(file_name):
    full_file_name = os.path.join(os.path.dirname(__file__), "data", file_name)
    info = shell.ShellFile.fromfile(full_file_name, process_data=False)
    assert not info.data_is_processed()


def test_shell_init_does_the_right_thing():
    some_date = datetime.datetime(1970, 1, 1)
    some_delta = datetime.timedelta(minutes=30)
    some_units = "Minutes"
    filename = "thing.bot"
    modified = some_date
    version = sections.Version(
        version_no="some version", date1="some date", date2="some other date"
    )
    file = sections.FileInfo(
        start_time=some_date,
        end_time=some_date,
        time_zero=some_date,
        time_increment=some_delta,
        time_units=some_units,
        number_of_records=0,
        data_description="",
        file_type="",
        format="",
        data_type="",
        pad=-99,
        number_of_channels=0,
        channels=[],
        channel_details=[],
        remarks="",
        raw={},
    )
    administration = sections.Administration(
        mission="",
        agency="",
        country="",
        project="",
        scientist="",
        platform="",
        remarks="",
        raw={},
    )
    location = sections.Location(
        geographic_area="",
        station="",
        event_number=0,
        latitude=0.0,
        longitude=0.0,
        water_depth=0.0,
        remarks="",
        raw={},
    )
    instrument = sections.Instrument(
        type="",
        model="",
        serial_number="",
        depth=-1,
        remarks="",
        raw={},
    )
    history = sections.History(
        programs=[],
        remarks="",
        raw={},
    )
    calibration = sections.Calibration(
        corrected_channels=[],
        remarks="",
        raw={},
    )
    deployment = sections.Deployment(
        mission="",
        type="",
        anchor_dropped=some_date,
        remarks="",
        raw={},
    )
    recovery = sections.Recovery(
        mission="",
        anchor_released=some_date,
        remarks="",
        raw={},
    )
    raw = sections.Raw(
        remarks="",
        raw={},
    )
    comments = ""
    data = [[]]

    info = shell.ShellFile(
        filename=filename,
        modified_date=modified,
        header_version=version,
        file=file,
        administration=administration,
        location=location,
        instrument=instrument,
        history=history,
        calibration=calibration,
        deployment=deployment,
        recovery=recovery,
        raw=raw,
        comments=comments,
        data=data,
    )

    assert info.filename == filename
    assert info.modified_date == modified
    assert info.header_version == version
    assert info.file == file
    assert info.administration == administration
    assert info.location == location
    assert info.instrument == instrument
    assert info.history == history
    assert info.calibration == calibration
    assert info.deployment == deployment
    assert info.recovery == recovery
    assert info.raw == raw
    assert info.comments == comments
    assert info.data == data


def test_process_data_fails_on_invalid_data():
    contents = """*2018/06/22 09:04:04.94
*IOS HEADER VERSION 2.0      2016/04/28 2016/06/13 IVF16

*FILE
    START TIME          : UTC 2015/03/16 10:36:00.000
    NUMBER OF RECORDS   : 2
    DATA DESCRIPTION    : Bottle:Wire
    FILE TYPE           : ASCII
    NUMBER OF CHANNELS  : 4

    $TABLE: CHANNELS
    ! No Name                         Units    Minimum        Maximum
    !--- ---------------------------- -------- -------------- --------------
       1 Depth:Nominal                metres   0              0
       2 Sample_Number                n/a      5              5
       3 Chlorophyll:Extracted        mg/m^3   30.69          30.69
       4 Flag:Chlorophyll:Extracted   ' '
    $END

    $TABLE: CHANNEL DETAIL
    ! No  Pad   Start  Width  Format  Type  Decimal_Places
    !---  ----  -----  -----  ------  ----  --------------
       1  -99   ' '        6  F       R4      0
       2  -99   ' '        5  I       I       0
       3  -99   ' '        7  F       R4      2
       4  ' '   ' '        3  NQ      C     ' '
    $END

*ADMINISTRATION
    MISSION             : 1993-001

*LOCATION
    LATITUDE            :  50   6.00000 N  ! (deg min)
    LONGITUDE           : 124  54.00000 W  ! (deg min)

*COMMENTS
words words words

*END OF HEADER
To see the real data, go to this link:..."""

    info = shell.ShellFile.fromcontents(contents, process_data=False)
    try:
        info.process_data()
        assert False
    except:
        assert not info.data_is_processed()


def test_get_complete_header_non_optional_sections():
    contents = """*2018/06/22 09:04:04.94
*IOS HEADER VERSION 2.0      2016/04/28 2016/06/13 IVF16

*FILE
    START TIME          : UTC 2015/03/16 10:36:00.000
    NUMBER OF RECORDS   : 1
    DATA DESCRIPTION    : Bottle:Wire
    FILE TYPE           : ASCII
    NUMBER OF CHANNELS  : 4

    $TABLE: CHANNELS
    ! No Name                         Units    Minimum        Maximum
    !--- ---------------------------- -------- -------------- --------------
       1 Depth:Nominal                metres   0              0
       2 Sample_Number                n/a      5              5
       3 Chlorophyll:Extracted        mg/m^3   30.69          30.69
       4 Flag:Chlorophyll:Extracted   ' '
    $END

    $TABLE: CHANNEL DETAIL
    ! No  Pad   Start  Width  Format  Type  Decimal_Places
    !---  ----  -----  -----  ------  ----  --------------
       1  -99   ' '        6  F       R4      0
       2  -99   ' '        5  I       I       0
       3  -99   ' '        7  F       R4      2
       4  ' '   ' '        3  NQ      C     ' '
    $END

*ADMINISTRATION
    MISSION             : 1993-001

*LOCATION
    LATITUDE            :  50   6.00000 N  ! (deg min)
    LONGITUDE           : 124  54.00000 W  ! (deg min)

*COMMENTS
words words words

*END OF HEADER
    0.    5  30.69 6"""

    info = shell.ShellFile.fromcontents(contents, process_data=False)
    assert info.get_complete_header() == {
        "file": {
            "start time": "UTC 2015/03/16 10:36:00.000",
            "number of records": "1",
            "data description": "Bottle:Wire",
            "file type": "ASCII",
            "number of channels": "4",
            "channels": [
                {
                    "no": "  1",
                    "name": "Depth:Nominal               ",
                    "units": "metres  ",
                    "minimum": "0             ",
                    "maximum": "0             ",
                },
                {
                    "no": "  2",
                    "name": "Sample_Number               ",
                    "units": "n/a     ",
                    "minimum": "5             ",
                    "maximum": "5             ",
                },
                {
                    "no": "  3",
                    "name": "Chlorophyll:Extracted       ",
                    "units": "mg/m^3  ",
                    "minimum": "30.69         ",
                    "maximum": "30.69         ",
                },
                {
                    "no": "  4",
                    "name": "Flag:Chlorophyll:Extracted  ",
                    "units": "' '     ",
                    "minimum": "              ",
                    "maximum": "              ",
                },
            ],
            "channel detail": [
                {
                    "no": "  1",
                    "pad": "-99 ",
                    "start": "' '  ",
                    "width": "    6",
                    "format": "F     ",
                    "type": "R4  ",
                    "decimal_places": "  0           ",
                },
                {
                    "no": "  2",
                    "pad": "-99 ",
                    "start": "' '  ",
                    "width": "    5",
                    "format": "I     ",
                    "type": "I   ",
                    "decimal_places": "  0           ",
                },
                {
                    "no": "  3",
                    "pad": "-99 ",
                    "start": "' '  ",
                    "width": "    7",
                    "format": "F     ",
                    "type": "R4  ",
                    "decimal_places": "  2           ",
                },
                {
                    "no": "  4",
                    "pad": "' ' ",
                    "start": "' '  ",
                    "width": "    3",
                    "format": "NQ    ",
                    "type": "C   ",
                    "decimal_places": "' '           ",
                },
            ],
        },
        "administration": {
            "mission": "1993-001",
        },
        "location": {
            "latitude": "50   6.00000 N  ! (deg min)",
            "longitude": "124  54.00000 W  ! (deg min)",
        },
        "comments": "words words words",
    }


def test_get_complete_header_optional_sections():
    contents = """*2018/06/22 09:04:04.94
*IOS HEADER VERSION 2.0      2016/04/28 2016/06/13 IVF16

*FILE
    START TIME          : UTC 2015/03/16 10:36:00.000
    NUMBER OF RECORDS   : 1
    DATA DESCRIPTION    : Bottle:Wire
    FILE TYPE           : ASCII
    NUMBER OF CHANNELS  : 1

    $TABLE: CHANNELS
    ! No Name                         Units    Minimum        Maximum
    !--- ---------------------------- -------- -------------- --------------
       1 Depth:Nominal                metres   0              0
    $END

    $TABLE: CHANNEL DETAIL
    ! No  Pad   Start  Width  Format  Type  Decimal_Places
    !---  ----  -----  -----  ------  ----  --------------
       1  -99   ' '        6  F       R4      0
    $END

*ADMINISTRATION
    MISSION   : 1993-001
    AGENCY    : UBC
    COUNTRY   : Canada
    PROJECT   : Kitimat
    SCIENTIST : C. Hannah
    PLATFORM  : Tully
    $REMARKS
        words words words
    $END

*LOCATION
    GEOGRAPHIC AREA : Strait of Georgia
    STATION         : SOGN
    EVENT NUMBER    : 13
    LATITUDE        :  49 39.00000 N
    LONGITUDE       : 126 27.20000 W
    WATER DEPTH     : 332
    $REMARKS
        words words words
    $END

*INSTRUMENT
    TYPE          : bottle
    MODEL         : abcd
    SERIAL NUMBER : 123456
    DEPTH         : 456
    $REMARKS
        words words words
    $END

*RAW
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

*HISTORY
    $TABLE: PROGRAMS
    !   Name     Vers   Date       Time     Recs In   Recs Out
    !   -------- ------ ---------- -------- --------- ---------
        RCM_CNVT 1.1    2019/07/18 10:36:44         0      2001
    $END
    $REMARKS
        words words words
    $END

*CALIBRATION
    $TABLE: CORRECTED CHANNELS
    !   Name     Units  Fmla Pad    Coefficients
    !   -------- ------ ---- ------ ------------
        Oxygen   mg/l     10 -99.99 () (0 0.223916E-01)
    $END
    $REMARKS
        words words words
    $END

*DEPLOYMENT
    MISSION             : 1930-01
    TYPE                : some type
    TIME ANCHOR DROPPED : UTC 1930/01/01 00:00:00
    $REMARKS
        words words words
    $END

*RECOVERY
    MISSION              : 1930-01
    TIME ANCHOR RELEASED : UTC 1930/01/01 00:00:00
    $REMARKS
        words words words
    $END

*COMMENTS
words words words

*END OF HEADER
    0.    5  30.69 6"""

    info = shell.ShellFile.fromcontents(contents, process_data=False)
    assert info.get_complete_header() == {
        "file": {
            "start time": "UTC 2015/03/16 10:36:00.000",
            "number of records": "1",
            "data description": "Bottle:Wire",
            "file type": "ASCII",
            "number of channels": "1",
            "channels": [
                {
                    "no": "  1",
                    "name": "Depth:Nominal               ",
                    "units": "metres  ",
                    "minimum": "0             ",
                    "maximum": "0             ",
                },
            ],
            "channel detail": [
                {
                    "no": "  1",
                    "pad": "-99 ",
                    "start": "' '  ",
                    "width": "    6",
                    "format": "F     ",
                    "type": "R4  ",
                    "decimal_places": "  0           ",
                },
            ],
        },
        "administration": {
            "mission": "1993-001",
            "agency": "UBC",
            "country": "Canada",
            "project": "Kitimat",
            "scientist": "C. Hannah",
            "platform": "Tully",
            "remarks": "        words words words",
        },
        "location": {
            "geographic area": "Strait of Georgia",
            "station": "SOGN",
            "event number": "13",
            "latitude": "49 39.00000 N",
            "longitude": "126 27.20000 W",
            "water depth": "332",
            "remarks": "        words words words",
        },
        "instrument": {
            "type": "bottle",
            "model": "abcd",
            "serial number": "123456",
            "depth": "456",
            "remarks": "        words words words",
        },
        "raw": {
            "number of records": "99999",
            "channels": [
                {
                    "name": "PRESSURE            ",
                    "raw_units": "' DBAR'  ",
                    "averaging_interval": "         ",
                    "day_hr_min_sec_ms)_time_lag": "           ",
                },
                {
                    "name": "TEMPERATURE         ",
                    "raw_units": "'    C'  ",
                    "averaging_interval": "         ",
                    "day_hr_min_sec_ms)_time_lag": "           ",
                },
                {
                    "name": "'CONDUCTIVITY RATIO'",
                    "raw_units": "RATIO    ",
                    "averaging_interval": "         ",
                    "day_hr_min_sec_ms)_time_lag": "           ",
                },
            ],
            "remarks": "        words words words",
        },
        "history": {
            "programs": [
                {
                    "name": "RCM_CNVT",
                    "vers": "1.1   ",
                    "date": "2019/07/18",
                    "time": "10:36:44",
                    "recs_in": "        0",
                    "recs_out": "     2001",
                },
            ],
            "remarks": "        words words words",
        },
        "calibration": {
            "corrected channels": [
                {
                    "name": "Oxygen  ",
                    "units": "mg/l  ",
                    "fmla": "  10",
                    "pad": "-99.99",
                    "coefficients": "() (0 0.223916E-01)",
                },
            ],
            "remarks": "        words words words",
        },
        "deployment": {
            "mission": "1930-01",
            "type": "some type",
            "time anchor dropped": "UTC 1930/01/01 00:00:00",
            "remarks": "        words words words",
        },
        "recovery": {
            "mission": "1930-01",
            "time anchor released": "UTC 1930/01/01 00:00:00",
            "remarks": "        words words words",
        },
        "comments": "words words words",
    }


def test_get_obs_time_date_and_time_columns():
    contents = """*2018/06/22 09:04:04.94
*IOS HEADER VERSION 2.0      2016/04/28 2016/06/13 IVF16

*FILE
    START TIME          : UTC 2015/03/28 10:36:00.000
    NUMBER OF RECORDS   : 4
    DATA DESCRIPTION    : Bottle:Wire
    FILE TYPE           : ASCII
    NUMBER OF CHANNELS  : 3

    $TABLE: CHANNELS
    ! No Name                         Units    Minimum        Maximum
    !--- ---------------------------- -------- -------------- --------------
       1 Date                         n/a      0              0
       2 Time                         n/a      5              5
       3 Chlorophyll:Extracted        mg/m^3   30.69          30.69
    $END

    $TABLE: CHANNEL DETAIL
    ! No  Pad   Start  Width  Format       Type  Decimal_Places
    !---  ----  -----  -----  -----------  ----  --------------
       1  -99   ' '      ' '  YYYY/MM/DD   D     ' '
       2  -99   ' '      ' '  hh:mm:ss.ss  T     ' '
       3  -99   ' '        7  F            R4      2
    $END

*ADMINISTRATION
    MISSION             : 1993-001

*LOCATION
    LATITUDE            :  50   6.00000 N  ! (deg min)
    LONGITUDE           : 124  54.00000 W  ! (deg min)

*COMMENTS
words words words

*END OF HEADER
 2015/03/28 10:36:00.00  14.00
 2015/03/28 10:46:00.00  15.00
 2015/03/28 10:56:00.00  16.00
 2015/03/28 11:06:00.00  17.00"""
    info = shell.ShellFile.fromcontents(contents, process_data=True)
    obs_time = info.get_obs_time()
    assert len(obs_time) == 4


def test_get_obs_time_combined_date_time_column():
    contents = """*2018/06/22 09:04:04.94
*IOS HEADER VERSION 2.0      2016/04/28 2016/06/13 IVF16

*FILE
    START TIME          : UTC 2015/03/28 10:36:00.000
    NUMBER OF RECORDS   : 4
    DATA DESCRIPTION    : Bottle:Wire
    FILE TYPE           : ASCII
    NUMBER OF CHANNELS  : 3

    $TABLE: CHANNELS
    ! No Name                         Units    Minimum        Maximum
    !--- ---------------------------- -------- -------------- --------------
       1 Date_Time                    n/a      0              0
       2 Chlorophyll:Extracted        mg/m^3   30.69          30.69
    $END

    $TABLE: CHANNEL DETAIL
    ! No  Pad   Start  Width  Format  Type  Decimal_Places
    !---  ----  -----  -----  ------  ----  --------------
       1  -99   ' '      ' '  HH:MM   DT     ' '
       2  -99   ' '        7  F       R4      2
    $END

*ADMINISTRATION
    MISSION             : 1993-001

*LOCATION
    LATITUDE            :  50   6.00000 N  ! (deg min)
    LONGITUDE           : 124  54.00000 W  ! (deg min)

*COMMENTS
words words words

*END OF HEADER
 2015/03/28 10:36  14.00
 2015/03/28 10:46  15.00
 2015/03/28 10:56  16.00
 2015/03/28 11:06  17.00"""
    info = shell.ShellFile.fromcontents(contents, process_data=True)
    obs_time = info.get_obs_time()
    assert len(obs_time) == 4


def test_get_obs_time_from_increment_value():
    contents = """*2018/06/22 09:04:04.94
*IOS HEADER VERSION 2.0      2016/04/28 2016/06/13 IVF16

*FILE
    START TIME          : UTC 2015/03/28 10:36:00.000
    NUMBER OF RECORDS   : 4
    DATA DESCRIPTION    : Bottle:Wire
    FILE TYPE           : ASCII
    TIME INCREMENT      : 0 0 10 0 0 ! (day hr min sec msec)
    NUMBER OF CHANNELS  : 3

    $TABLE: CHANNELS
    ! No Name                         Units    Minimum        Maximum
    !--- ---------------------------- -------- -------------- --------------
       1 Chlorophyll:Extracted        mg/m^3   30.69          30.69
    $END

    $TABLE: CHANNEL DETAIL
    ! No  Pad   Start  Width  Format Type  Decimal_Places
    !---  ----  -----  -----  ------ ----  --------------
       1  -99   ' '        7  F      R4      2
    $END

*ADMINISTRATION
    MISSION             : 1993-001

*LOCATION
    LATITUDE            :  50   6.00000 N  ! (deg min)
    LONGITUDE           : 124  54.00000 W  ! (deg min)

*COMMENTS
words words words

*END OF HEADER
 14.00
 15.00
 16.00
 17.00"""
    info = shell.ShellFile.fromcontents(contents, process_data=True)
    obs_time = info.get_obs_time()
    assert len(obs_time) == 4


def test_get_obs_time_fails_without_increment_value():
    contents = """*2018/06/22 09:04:04.94
*IOS HEADER VERSION 2.0      2016/04/28 2016/06/13 IVF16

*FILE
    START TIME          : UTC 2015/03/28 10:36:00.000
    NUMBER OF RECORDS   : 4
    DATA DESCRIPTION    : Bottle:Wire
    FILE TYPE           : ASCII
    NUMBER OF CHANNELS  : 3

    $TABLE: CHANNELS
    ! No Name                         Units    Minimum        Maximum
    !--- ---------------------------- -------- -------------- --------------
       1 Chlorophyll:Extracted        mg/m^3   30.69          30.69
    $END

    $TABLE: CHANNEL DETAIL
    ! No  Pad   Start  Width  Format  Type  Decimal_Places
    !---  ----  -----  -----  ------  ----  --------------
       1  -99   ' '        7  F       R4      2
    $END

*ADMINISTRATION
    MISSION             : 1993-001

*LOCATION
    LATITUDE            :  50   6.00000 N  ! (deg min)
    LONGITUDE           : 124  54.00000 W  ! (deg min)

*COMMENTS
words words words

*END OF HEADER
 14.00
 15.00
 16.00
 17.00"""
    info = shell.ShellFile.fromcontents(contents, process_data=True)
    try:
        obs_time = info.get_obs_time()
        assert False
    except:
        pass


def test_get_obs_time_fails_when_start_times_mismatch():
    contents = """*2018/06/22 09:04:04.94
*IOS HEADER VERSION 2.0      2016/04/28 2016/06/13 IVF16

*FILE
    START TIME          : UTC 2015/03/28 10:36:00.000
    NUMBER OF RECORDS   : 4
    DATA DESCRIPTION    : Bottle:Wire
    FILE TYPE           : ASCII
    NUMBER OF CHANNELS  : 3

    $TABLE: CHANNELS
    ! No Name                         Units    Minimum        Maximum
    !--- ---------------------------- -------- -------------- --------------
       1 Date                         n/a      0              0
       2 Time                         n/a      5              5
       3 Chlorophyll:Extracted        mg/m^3   30.69          30.69
    $END

    $TABLE: CHANNEL DETAIL
    ! No  Pad   Start  Width  Format       Type  Decimal_Places
    !---  ----  -----  -----  -----------  ----  --------------
       1  -99   ' '      ' '  YYYY/MM/DD   D     ' '
       2  -99   ' '      ' '  hh:mm:ss.ss  T     ' '
       3  -99   ' '        7  F            R4      2
    $END

*ADMINISTRATION
    MISSION             : 1993-001

*LOCATION
    LATITUDE            :  50   6.00000 N  ! (deg min)
    LONGITUDE           : 124  54.00000 W  ! (deg min)

*COMMENTS
words words words

*END OF HEADER
 2016/03/28 10:36:00.00  14.00
 2016/03/28 10:46:00.00  15.00
 2016/03/28 10:56:00.00  16.00
 2016/03/28 11:06:00.00  17.00"""
    info = shell.ShellFile.fromcontents(contents, process_data=True)
    try:
        obs_time = info.get_obs_time()
        assert False
    except:
        pass
