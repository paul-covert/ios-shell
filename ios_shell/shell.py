import datetime

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
        self.calibration = calibration
        self.comments = comments
        self.data = data

    @classmethod
    def fromfile(cls, filename):
        with open(filename, "r", encoding="ASCII", errors="ignore") as f:
            contents = f.read()
        return ShellFile.fromcontents(contents, filename=filename)

    @classmethod
    def fromcontents(cls, contents, filename="bare string"):
        modified_date, rest = parsing.get_modified_date(contents)
        header_version, rest = parsing.get_header_version(rest)
        # begin named sections
        file_info, rest = parsing.get_file(rest)
        # sections that may appear out of order
        administration, location, instrument, history, calibration, comments = (
            None,
            None,
            None,
            None,
            None,
            None,
        )
        while not rest.lstrip().startswith("*END OF HEADER"):
            first = rest.lstrip().split("\n", 1)[0]
            if first.startswith("*ADMINISTRATION"):
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
            else:
                raise ValueError(f"Unknown section: {first}")
        # end named sections
        data, rest = parsing.get_data(
            rest, file_info.format, file_info.number_of_records
        )
        return ShellFile(
            filename=filename,
            modified_date=modified_date,
            header_version=header_version,
            file=file_info,
            administration=administration,
            location=location,
            instrument=instrument,
            history=history,
            calibration=calibration,
            comments=comments,
            data=data,
        )

    def get_location(self) -> dict[str, float]:
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

    def get_data_by_name(self, name: str) -> list[object]:
        names = [channel.name for channel in self.file.channels]
        if name not in names:
            raise ValueError(f"{name} not found in {self.file.channels}")
        return self.__get_data(names.index(name))

    def get_data_by_channel_no(self, channel_no: int) -> list[object]:
        numbers = [channel.no for channel in self.file.channels]
        if channel_no not in numbers:
            raise ValueError(f"{channel_no} not found in {self.file.channels}")
        return self.__get_data(numbers.index(channel_no))

    def __get_data(self, index, placeholder) -> list[object]:
        return ["NaN" if row[index] == placeholder else row[index] for row in self.data]
