"""Theme API classes"""

from dataclasses import dataclass


@dataclass
class Theme:
    """Represents a theme identified in a document.

    Contains information about a specific theme found during document analysis,
    including its name and relevancy score indicating how prominent the theme is.

    Attributes:
        name (str): The name or identifier of the theme.
        relevancy (float): A score indicating the relevancy or prominence of the theme
            in the document, typically ranging from 0.0 to 1.0.
    """

    name: str
    relevancy: float


def convert_themes(jo_themes: list) -> list[Theme]:

    return [Theme(**t) for t in jo_themes] if jo_themes else []
