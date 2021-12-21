"""Contains high-level object representing the whole of an IOS Shell file."""
import datetime
from typing import Dict, List, Union

from . import parsing, sections


class ShellFile:
    def __init__(
        self,
        filename: str,
        modified_date: datetime.datetime,
        header_version: sections.Version,
        file: sections.FileInfo,
        administration: sections.Administration,
        location: sections.Location,
        instrument: sections.Instrument,
        history: sections.History,
        calibration: sections.Calibration,
        comments: str,
        data: Union[List[List[object]], str],
    ):
        self.filename = filename
        self.modified_date = modified_date
        self.header_version = header_version
        self.file = file
        self.administration = administration
        self.location = location
        self.instrument = instrument
        self.history = history
        self.calibration = calibration
        self.comments = comments
        self.data = data

    @classmethod
    def fromfile(cls, filename, process_data=True):
        with open(filename, "r", encoding="ASCII", errors="ignore") as f:
            contents = f.read()
        return ShellFile.fromcontents(contents, process_data, filename=filename)

    @classmethod
    def fromcontents(cls, contents, process_data=True, filename="bare string"):
        modified_date, rest = parsing.get_modified_date(contents)
        header_version, rest = parsing.get_header_version(rest)
        # begin named sections
        # sections that may appear out of order
        (
            file,
            administration,
            location,
            instrument,
            history,
            calibration,
            comments,
            raw,
        ) = (
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )
        while not rest.lstrip().startswith("*END OF HEADER"):
            first = rest.lstrip().split("\n", 1)[0]
            if first.startswith("*FILE"):
                if file is not None:
                    raise ValueError("There should only be one file section")
                file, rest = parsing.get_file(rest)
            elif first.startswith("*ADMINISTRATION"):
                if administration is not None:
                    raise ValueError("There should only be one administration section")
                administration, rest = parsing.get_administration(rest)
            elif first.startswith("*LOCATION"):
                if location is not None:
                    raise ValueError("There should only be one location section")
                location, rest = parsing.get_location(rest)
            elif first.startswith("*INSTRUMENT"):
                if instrument is not None:
                    raise ValueError("There should only be one instrument section")
                instrument, rest = parsing.get_instrument(rest)
            elif first.startswith("*HISTORY"):
                if history is not None:
                    raise ValueError("There should only be one history section")
                history, rest = parsing.get_history(rest)
            elif first.startswith("*COMMENTS"):
                if comments is not None:
                    raise ValueError("There should only be one comments section")
                comments, rest = parsing.get_comments(rest)
            elif first.startswith("*CALIBRATION"):
                if calibration is not None:
                    raise ValueError("There should only be one calibration section")
                calibration, rest = parsing.get_calibration(rest)
            elif first.startswith("*RAW"):
                if raw is not None:
                    raise ValueError("There should only be one raw section")
                raw, rest = parsing.get_raw(rest)
            else:
                raise ValueError(f"Unknown section: {first}")
        # end named sections
        if process_data:
            data, rest = parsing.get_data(rest, file.format, file.number_of_records)
        else:
            data = rest
        return ShellFile(
            filename=filename,
            modified_date=modified_date,
            header_version=header_version,
            file=file,
            administration=administration,
            location=location,
            instrument=instrument,
            history=history,
            calibration=calibration,
            comments=comments,
            data=data,
        )

    def get_location(self) -> Dict[str, float]:
        return {
            "longitude": self.location.longitude,
            "latitude": self.location.latitude,
        }

    def get_time(self) -> datetime.datetime:
        if self.file.start_time != datetime.datetime.fromtimestamp(0):
            return self.file.start_time
        elif self.file.end_time != datetime.datetime.fromtimestamp(0):
            return self.file.end_time
        else:
            raise ValueError("No valid time found")

    def data_is_processed(self) -> bool:
        return not isinstance(self.data, str)

    def process_data(self):
        if self.data_is_processed():
            return
        self.data = parsing.get_data(
            self.data, self.file.format, self.file.number_of_records
        )
