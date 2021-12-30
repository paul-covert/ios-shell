import datetime
import pytest
import os

import ios_shell as shell
import ios_shell.sections as sections


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
        "2005-010-0016.che",
        "2008-007-0002.tob",
        "2008-010-0001.che",
        "2008-026-0089.che",
        "2015-022-0031.bot",
        "51010002.ubc",
        "74010003.ubc",
        "BP2_20130705_20130810_0114m.ctd",
        "cmp1_20160127_20160520_0193m.ctd",
        "dev1_20150727_20160517_0152m.ctd",
    ],
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
    assert len(info.data) == info.file.number_of_records


def test_shell_init_does_the_right_thing():
    some_date = datetime.datetime(1970, 1, 1)
    filename = "thing.bot"
    modified = some_date
    version = sections.Version(version_no="some version", date1="some date", date2="some other date")
    file = sections.FileInfo(
        start_time=some_date,
        end_time=some_date,
        time_zero=some_date,
        number_of_records=0,
        data_description="",
        file_type="",
        format="",
        data_type="",
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
        channels=[],
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
    assert info.comments == comments
    assert info.data == data
