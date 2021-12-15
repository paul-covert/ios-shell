import datetime

from .parsing import *
from .sections import *

class ShellFile:
    def __init__(
        self,
        filename: str,
        modified_date: datetime.datetime,
        header_version: str,
        file: FileInfo,
        administration: Administration,
        location: Location,
        instrument: Instrument,
        history: History,
        comments: str,
        data: list[list[object]],
    ):
        self.filename = filename
        self.modified_date = modified_date
        self.header_version = header_version
        self.file = file
        self.administration = administration
        self.location = location
        self.instrument = instrument
        self.history = history
        self.comments = comments
        self.data = data

    @classmethod
    def fromfile(cls, filename):
        with open(filename) as f:
            contents = f.read()
        return ShellFile.fromcontents(contents, filename=filename)

    @classmethod
    def fromcontents(cls, contents, filename="bare string"):
        modified_date, rest = get_modified_date(contents)
        header_version, rest = get_header_version(rest)
        # begin named sections
        # could spin searching through sections?
        file_info, rest = get_file(rest)
        administration, rest = get_administration(rest)
        location, rest = get_location(rest)
        instrument, rest = get_instrument(rest)
        history, rest = get_history(rest)
        comments, rest = get_comments(rest)
        # end named sections
        data, rest = get_data(rest, file_info.format, file_info.number_of_records)
        return ShellFile(
            filename,
            modified_date,
            header_version,
            file_info,
            administration,
            location,
            instrument,
            history,
            comments,
            data,
        )
