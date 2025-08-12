from enum import IntEnum
import logging
import typing


class DiagnosticType(IntEnum):
    """Enumeration type that holds the diagnostic types supported by default.

    The included levels map to the levels provided by the logging library.

    Note:
        This enumeration type can be extended or replaced with any other integer type.
    """

    Debug = logging.DEBUG
    Info = logging.INFO
    Warning = logging.WARNING
    Error = logging.ERROR
    Critical = logging.CRITICAL
    Notset = logging.NOTSET

    @classmethod
    def names(cls) -> typing.List[str]:
        """Get the diagnostic names, sorted by level value.

        Returns:
            List[str]: The diagnostic names, sorted by level value.
        """
        names = [name for name in dir(DiagnosticType) if not name.startswith("_") and name[0].isupper()]
        return sorted(names, key=lambda name: int(getattr(DiagnosticType, name)))

    @classmethod
    def all(cls):
        """Get all type enumerations.

        Returns:
            List[int]: All type enumerations.
        """
        return [getattr(DiagnosticType, name) for name in cls.names()]

    @classmethod
    def count(cls) -> int:
        """Get the number of diagnostic types.

        Returns:
            int: The number of types.
        """
        return len(cls.names())


_levelToName = {
    logging.CRITICAL: "[red bold]CRITICAL[/red bold]",
    logging.ERROR: "[red]ERROR[/red]",
    logging.WARNING: "[yellow]WARNING[/yellow]",
    logging.INFO: "INFO",
    logging.DEBUG: "DEBUG",
    logging.NOTSET: "NOTSET",
}


def _getLevelName(level):
    """Get the display name for a logging level.

    Args:
        level (int): The logging level.

    Returns:
        str: The display name for the level, or empty string if not found.
    """
    if level in _levelToName:
        return _levelToName[level]
    return ""


class Diagnostic:
    """Diagnostic is a class that holds all relevant diagnostical information.

    Note:
        The type parameter can be any integer type. For convenience sake, DiagnosticType
        is used by default, but you can provide your own typing scheme.
    """

    @staticmethod
    def from_json(json: dict):
        """Create a Diagnostic instance from a JSON dictionary.

        Args:
            json (dict): JSON dictionary containing diagnostic data.

        Returns:
            Diagnostic: A new Diagnostic instance.
        """
        return Diagnostic(
            id=json.get("id"),
            message=json["message"],
            type=json["type"],
            line=json["line"] if "line" in json else None,
            offset=json["offset"] if "offset" in json else None,
        )

    def __init__(
        self,
        id: str | None,
        message: str,
        type: int,
        line: typing.Union[int, None] = None,
        offset: typing.Union[int, None] = None,
    ):
        """Initialize a Diagnostic instance.

        Args:
            id (str|None): Unique identifier.
            message (str): Message.
            type (int): Diagnostic type.
            line (int|None): Line number. Defaults to None.
            offset (int|None): Offset. Defaults to None.
        """
        super(Diagnostic, self).__init__()
        self.id = id
        self.message = message
        self.type = type
        self.line = line
        self.offset = offset

    def to_json(self):
        """Convert the diagnostic to a JSON dictionary.

        Returns:
            dict: A dictionary representing a JSON object of the diagnostic.
        """
        obj = dict(id=self.id, message=self.message, type=self.type)
        if self.line is not None:
            obj["line"] = self.line
        if self.offset is not None:
            obj["offset"] = self.offset
        return obj

    def to_exception(self):
        """Convert the diagnostic to a DiagnosticException.

        Returns:
            DiagnosticException: A DiagnosticException instance containing this diagnostic.
        """
        return DiagnosticException(self)

    def rich(self):
        """Get the rich string representation of the diagnostic.

        Returns:
            str: The rich string representation of the diagnostic.
        """
        if self.line:
            return f"<default>{self.id}</default>:{self.line}:{_getLevelName(self.type)}:{self.message}"
        else:
            return f"<default>{self.id}</default>:{_getLevelName(self.type)}:{self.message}"

    def __eq__(self, other):
        """Check equality with another Diagnostic instance.

        Args:
            other (Diagnostic): The other diagnostic to compare with.

        Returns:
            bool: True if diagnostics are equal, False otherwise.
        """
        return self.to_json() == other.to_json()

    def __str__(self):
        """Get string representation of the diagnostic.

        Returns:
            str: String representation of the diagnostic.
        """
        return f"<Diagnostic: id={self.id}, type={self.type}, message={self.message}>"


class DiagnosticException(Exception):
    """Exception that wraps a Diagnostic instance."""

    def __init__(self, diagnostic: Diagnostic):
        """Initialize a DiagnosticException.

        Args:
            diagnostic (Diagnostic): The diagnostic to wrap.
        """
        super(DiagnosticException, self).__init__(self, diagnostic.message)
        self.diagnostic = diagnostic

    def __str__(self):
        """Get string representation of the exception.

        Returns:
            str: The diagnostic message.
        """
        return self.diagnostic.message


class Diagnostics:
    """Diagnostics is a convenience class that provides commonly used functionality and acts as a facade."""

    @staticmethod
    def from_json(json: list):
        """Create a Diagnostics instance from a JSON list.

        Args:
            json (list): JSON list containing diagnostic data.

        Returns:
            Diagnostics: A new Diagnostics instance.
        """
        items = [Diagnostic.from_json(item) for item in json]
        return Diagnostics(items=items)

    def __init__(self, items: typing.List[Diagnostic] | None = None):
        """Initialize a Diagnostics instance.

        Args:
            items (List[Diagnostic]|None): Diagnostics. Defaults to an empty list.
        """
        super(Diagnostics, self).__init__()
        self.items = items if items else []

    def add(self, diagnostic: Diagnostic):
        """Add a diagnostic.

        Args:
            diagnostic (Diagnostic): Diagnostic to add.
        """
        self.items.append(diagnostic)

    def extend(self, diagnostics):
        """Extend with given diagnostics.

        Args:
            diagnostics (Diagnostics): Diagnostics to extend with.
        """
        for diagnostic in diagnostics:
            self.add(diagnostic)

    def filter(self, type: typing.SupportsInt):
        """Filter on a given diagnostic type.

        Args:
            type (typing.SupportsInt): Diagnostic type (DiagnosticType or int).

        Returns:
            filter: A filter object yielding diagnostics of the matching type.
        """
        if type == DiagnosticType.Notset:
            return self.items
        return filter(lambda item: type == item.type, self.items)

    def has(self, type: typing.SupportsInt) -> bool:
        """Check whether a diagnostic with the given type is present.

        Args:
            type (typing.SupportsInt): Diagnostic type to check for.

        Returns:
            bool: True if a diagnostic with the given type is present, False otherwise.
        """
        for _ in self.filter(type):
            return True
        return False

    def __len__(self) -> int:
        """Get the number of diagnostics.

        Returns:
            int: The number of diagnostics.
        """
        return len(self.items)

    def __iter__(self):
        """Iterate over the diagnostics.

        Returns:
            iterator: Iterator over the diagnostic items.
        """
        return iter(self.items)

    def raise_when(self, type: typing.SupportsInt):
        """Raise an exception when a diagnostic exceeds the level of the given type.

        Args:
            type (typing.SupportsInt): Diagnostic type threshold.

        Raises:
            DiagnosticException: Only in presence of a diagnostic level that exceeds the given type.
        """
        for diagnostic in self.items:
            if int(diagnostic.type) >= int(type):
                exception = diagnostic.to_exception()
                assert isinstance(exception, DiagnosticException), "Diagnostic did not return an exception"
                raise exception

    def is_greater_or_equal_than(self, type: typing.SupportsInt):
        """Check whether a diagnostic is greater or equal than the given diagnostic type.

        Args:
            type (typing.SupportsInt): Diagnostic type to compare against.

        Returns:
            bool: True if a diagnostic is greater or equal than the given diagnostic type, False otherwise.
        """
        for diagnostic in self.items:
            if int(diagnostic.type) >= int(type):
                return True

    def to_json(self):
        """Convert the diagnostics to a JSON list.

        Returns:
            list: A list of diagnostic JSON dictionaries.
        """
        return [diagnostic.to_json() for diagnostic in self.items]

    def __eq__(self, other):
        return self.to_json() == other.to_json()

    def __str__(self):
        return f"<Diagnostics: {len(self)} items>"

    def __getitem__(self, index):
        """Get diagnostic at the specified index.

        Args:
            index (int): Index of the diagnostic to retrieve.

        Returns:
            Diagnostic: The diagnostic at the specified index.
        """
        return self.items[index]
