import pytest
import ios_shell.shell as shell
import ios_shell.parsing as parsing

test_file = """
*2021/12/13 16:09:19.32
*IOS HEADER VERSION 1.10 2011/10/26 2011/10/26

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

*LOCATION
    GEOGRAPHIC AREA     : Nootka Sound
    STATION             : 2235-H
    EVENT NUMBER        : 16
    LATITUDE            :  49  39.00000 N  ! (deg min)
    LONGITUDE           : 126  27.20000 W  ! (deg min)

*END OF HEADER
    1.  16.00  18.64   6.70  12.6   0.55
    2.  15.60  19.76   6.82  12.6   0.63
    4.  13.20  27.09   7.83   7.2   0.63
    6.  11.15  31.26   7.92   6.8   0.75
   10.   9.20  32.21   5.00  27.6   1.45
   20.   8.70  32.25   3.95  33.8   1.94
   30.   8.30  32.52   3.53  34.8   1.94
   50.   8.05  32.61   3.03  38.2   2.19
  100.   7.90  32.79   3.02  38.2   2.25
  200.   7.80  32.83   1.93-100.0 -99.99
"""

@pytest.mark.parametrize(
    "contents",
    [
        "*IOS HEADER VERSION 1.10 2011/10/26 2011/10/26",
    ])
def test_header_version(contents):
    version, rest = parsing.get_header_version(contents)
    assert version == "1.10"
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

def test_struct_modified_date():
    _, rest = parsing.get_modified_date(test_file)
    assert len(rest) > 0

    try:
        parsing.get_modified_date("no modified date")
        assert False
    except:
        pass

def test_shell_struct_header_version():
    version, rest = parsing.get_header_version("*IOS HEADER VERSION 1.10 2011/10/26 2011/10/26")
    assert version == "1.10"
    assert len(rest) == 0

    version, rest = parsing.get_header_version("*IOS HEADER VERSION 1.10 2011/10/26 2011/10/26\nmore")
    assert version == "1.10"
    assert len(rest) > 0
    assert rest[0] == "\n"

    try:
        parsing.get_header_version("not a header version")
        assert False
    except:
        pass

def test_shell_struct_section():
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

def test_shell_struct_full_file():
    info = shell.ShellFile.fromcontents(test_file)
    assert info.file.number_of_records == 10
    assert len(info.data) == info.file.number_of_records
