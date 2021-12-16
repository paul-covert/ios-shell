import pytest
import os
import ios_shell.shell as shell
import ios_shell.parsing as parsing


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


def test_shell_get_section():
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


@pytest.mark.parametrize(
    "file_name",
    [
        "00200001.med",
        "01100124.bot",
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
        "1991-017-0003.bot",
        "1991-017-0010.bot",
        "1992-016-0001.bot",
        "1996-036-0005.che",
        "1996-038-0077.che",
        "2002-030-8008.bot",
        "2005-010-0016.che",
        "2008-010-0001.che",
        "2008-026-0089.che",
        "2015-022-0031.bot",
        "51010002.ubc",
        "74010003.ubc",
    ],
)
def test_shell_read_file(file_name):
    full_file_name = os.path.join(os.path.dirname(__file__), "data", file_name)
    info = shell.ShellFile.fromfile(full_file_name)
    assert len(info.data) == info.file.number_of_records


@pytest.mark.parametrize(
    "contents",
    [
        """
*2018/06/22 09:04:04.94
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

*END OF HEADER
    0.    5  30.69 6
        """,
    ]
)
def test_shell_read_data(contents):
    info = shell.ShellFile.fromcontents(contents)
    assert len(info.data) == info.file.number_of_records
    assert info.file.channels[0].minimum <= info.data[0][0] <= info.file.channels[0].maximum
