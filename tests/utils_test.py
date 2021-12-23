import pytest

import ios_shell.utils as utils


@pytest.mark.parametrize(
    "time",
    [
        "UTC 2015/03/16 10:36:00.000",
        "UTC 2015/03/16",
    ]
)
def test_utils_to_iso(time):
    time_info = utils.to_iso(time)
    assert time_info.tzinfo is not None
