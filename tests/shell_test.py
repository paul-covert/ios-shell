import pytest
import os
import ios_shell as shell
import ios_shell.parsing as parsing

TEST_FILES = [
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
    "1987-070-0001.bot",
    "1991-017-0003.bot",
    "1991-017-0010.bot",
    "1992-016-0001.bot",
    "1996-036-0005.che",
    "1996-038-0077.che",
    "1998-015-8001.bot",
    "2002-030-8008.bot",
    "2002-043-Cape-Beale-Lighthouse.bot",
    "2005-010-0016.che",
    "2008-007-0002.tob",
    "2008-010-0001.che",
    "2008-026-0089.che",
    "2015-022-0031.bot",
    "51010002.ubc",
    "74010003.ubc",
]


@pytest.mark.parametrize(
    "file_name",
    TEST_FILES,
)
def test_shell_read_file(file_name):
    full_file_name = os.path.join(os.path.dirname(__file__), "data", file_name)
    info = shell.ShellFile.fromfile(full_file_name, process_data=True)
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
    ],
)
def test_shell_read_data(contents):
    info = shell.ShellFile.fromcontents(contents)
    assert len(info.data) == info.file.number_of_records
    assert (
        info.file.channels[0].minimum
        <= info.data[0][0]
        <= info.file.channels[0].maximum
    )


@pytest.mark.parametrize(
    "file_name",
    TEST_FILES,
)
def test_shell_process_data(file_name):
    full_file_name = os.path.join(os.path.dirname(__file__), "data", file_name)
    info = shell.ShellFile.fromfile(full_file_name, process_data=False)
    assert not info.data_is_processed()
    info.process_data()
    assert isinstance(info.data, list)
    assert info.data_is_processed()

    info = shell.ShellFile.fromfile(full_file_name, process_data=True)
    assert info.data_is_processed()
