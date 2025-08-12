"""Anonymizer API classes"""

from dataclasses import dataclass, field


@dataclass
class Location:
    """Represents a location of anonymized content in a document.

    A location contains information about where sensitive data was found
    and how it was anonymized, including character and byte offsets.

    Attributes:
        begin_offset (int): Starting character position of the sensitive content.
        end_offset (int): Ending character position of the sensitive content.
        uri (str): URI or identifier for the type of sensitive content detected.
        anonymized (str): The anonymized replacement text.
        text (str): The original sensitive text that was anonymized.
        byte_begin_offset (int|None): Starting byte position, if available.
        byte_end_offset (int|None): Ending byte position, if available.
    """

    begin_offset: int
    end_offset: int
    uri: str
    anonymized: str
    text: str
    byte_begin_offset: int | None = None
    byte_end_offset: int | None = None


@dataclass
class AnonymizerResults:
    """Results from an anonymization process on a document.

    Contains the anonymized text and a list of all locations where
    sensitive content was detected and anonymized.

    Attributes:
        text (str): The complete anonymized text with sensitive content replaced.
        locations (list[Location]): List of Location objects describing where
            and how sensitive content was anonymized. Defaults to empty list.
    """

    text: str
    locations: list[Location] = field(default_factory=list)


def convert_anonymizer(jo_data: dict) -> AnonymizerResults:
    results = AnonymizerResults(text=jo_data["text"])
    for location in jo_data["locations"]:
        location = Location(**location)
        results.locations.append(location)

    return results
