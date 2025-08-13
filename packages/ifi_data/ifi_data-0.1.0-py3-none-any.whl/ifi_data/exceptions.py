class InvalidDelimiterError(Exception):
    """Raised when delimiter auto-detection fails and no delimiter is provided."""

    pass


class DatetimeDetectionError(Exception):
    """Raised when automatic detection of datetime column fails or is ambiguous."""

    pass


class DatetimeParsingError(Exception):
    """Raised when parsing a datetime column fails due to incorrect format or timezone."""

    pass


class TableNameError(Exception):
    """Raised when a provided table name is invalid."""

    pass


class MetadataError(Exception):
    """Raised for problems reading or writing table metadata."""

    pass


class DatabaseUnavailableError(RuntimeError):
    """Raised when the Timescale / Postgres server cannot be reached."""

    pass