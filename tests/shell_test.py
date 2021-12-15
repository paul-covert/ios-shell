import pytest
import os
import ios_shell.shell as shell
import ios_shell.parsing as parsing

@pytest.mark.parametrize(
    "contents,expected",
    [
        ("*IOS HEADER VERSION 1.10 2011/10/26 2011/10/26", "1.10"),
        ("*IOS HEADER VERSION 2.0      2016/04/28 2016/06/13 IVF16", "2.0"),
    ])
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
    ])
def test_get_location(contents):
    _, rest = parsing.get_location(contents)
    assert rest.strip() == "*END OF HEADER"

def test_shell_get_section():
    section, rest = parsing.get_section("""
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
    """, "file")
    assert rest.strip() == "*END OF HEADER"
    assert "channels" in section

@pytest.mark.parametrize(
    "file_name",
    [
        "1930-031-0001.bot",
        "1930-031-0010.bot",
        "1930-099-0001.bot",
        "1930-003-0058.bot",
        "1933-001-0001.bot",
        "1933-001-0004.bot",
        "1938-019-0001.bot",
        "1950-001-0033.bot",
    ])
def test_shell_read_file(file_name):
    full_file_name = os.path.join(os.path.dirname(__file__), "data", file_name)
    info = shell.ShellFile.fromfile(full_file_name)
    assert len(info.data) == info.file.number_of_records
