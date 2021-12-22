import pytest
import os
import ios_shell as shell


@pytest.mark.optional
def test_all_subdirs():
    subdirs = [entry.path for entry in os.scandir(os.path.join(os.path.dirname(__file__), "data")) if entry.is_dir()]
    for subdir in subdirs:
        for file in os.listdir(subdir):
            file_name = os.path.join(subdir, file)
            info = shell.ShellFile.fromfile(file_name, process_data=True)
            assert info.file.number_of_records == len(info.data)
