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
        instrument: Union[sections.Instrument, None],
        history: Union[sections.History, None],
        calibration: Union[sections.Calibration, None],
        deployment: Union[sections.Deployment, None],
        recovery: Union[sections.Recovery, None],
        raw: Union[sections.Raw, None],
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
        self.deployment = deployment
        self.recovery = recovery
        self.raw = raw
        self.comments = comments
        self.data = data

    @classmethod
    def fromfile(cls, filename, process_data=True):  # pragma: no mutate
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
            deployment,
            recovery,
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
            None,
            None,
        )
        while not rest.lstrip().startswith("*END OF HEADER"):
            rest = rest.lstrip()
            if rest.startswith("*FILE"):
                if file is not None:
                    raise ValueError("There should only be one file section")
                file, rest = parsing.get_file(rest)
            elif rest.startswith("*ADMINISTRATION"):
                if administration is not None:
                    raise ValueError("There should only be one administration section")
                administration, rest = parsing.get_administration(rest)
            elif rest.startswith("*LOCATION"):
                if location is not None:
                    raise ValueError("There should only be one location section")
                location, rest = parsing.get_location(rest)
            elif rest.startswith("*INSTRUMENT"):
                if instrument is not None:
                    raise ValueError("There should only be one instrument section")
                instrument, rest = parsing.get_instrument(rest)
            elif rest.startswith("*HISTORY"):
                if history is not None:
                    raise ValueError("There should only be one history section")
                history, rest = parsing.get_history(rest)
            elif rest.startswith("*COMMENTS"):
                if comments is not None:
                    raise ValueError("There should only be one comments section")
                comments, rest = parsing.get_comments(rest)
            elif rest.startswith("*CALIBRATION"):
                if calibration is not None:
                    raise ValueError("There should only be one calibration section")
                calibration, rest = parsing.get_calibration(rest)
            elif rest.startswith("*RAW"):
                if raw is not None:
                    raise ValueError("There should only be one raw section")
                raw, rest = parsing.get_raw(rest)
            elif rest.startswith("*DEPLOYMENT"):
                if deployment is not None:
                    raise ValueError("There should only be one deployment section")
                deployment, rest = parsing.get_deployment(rest)
            elif rest.startswith("*RECOVERY"):
                if recovery is not None:
                    raise ValueError("There should only be one recovery section")
                recovery, rest = parsing.get_recovery(rest)
            else:
                section_name = rest.lstrip().split("\n", 1)[0]  # pragma: no mutate
                raise ValueError(f"Unknown section: {section_name}")
        # end named sections
        if process_data:
            data, rest = parsing.get_data(rest, file.format, file.number_of_records)
        else:
            data = rest
        # check for required sections
        if file is None:
            raise ValueError("*FILE section must be present")
        if administration is None:
            raise ValueError("*ADMINISTRATION section must be present")
        if location is None:
            raise ValueError("*LOCATION section must be present")
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
            deployment=deployment,
            recovery=recovery,
            raw=raw,
            comments=comments if comments is not None else "",
            data=data,
        )

    def get_location(self) -> Dict[str, float]:
        return {
            "longitude": self.location.longitude,
            "latitude": self.location.latitude,
        }

    def get_time(self) -> datetime.datetime:
        if self.file.start_time != datetime.datetime.min:
            return self.file.start_time
        elif self.file.end_time != datetime.datetime.min:
            return self.file.end_time
        else:
            raise ValueError("No valid time found")

    def data_is_processed(self) -> bool:
        return not isinstance(self.data, str)

    def process_data(self):
        if self.data_is_processed():
            return
        # assertion to satisfy (optional) type checking
        assert isinstance(self.data, str)
        self.data, _ = parsing.get_data(
            self.data, self.file.format, self.file.number_of_records
        )
