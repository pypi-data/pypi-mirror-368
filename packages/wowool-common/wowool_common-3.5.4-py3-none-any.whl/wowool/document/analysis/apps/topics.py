"""Topic API classes"""

from dataclasses import dataclass


@dataclass
class Topic:
    """Represents a topic identified in a document.

    Contains information about a specific topic found during document analysis,
    including its name and relevancy score indicating how prominent the topic is.

    Attributes:
        name (str): The name or identifier of the topic.
        relevancy (float): A score indicating the relevancy or prominence of the topic
            in the document, typically ranging from 0.0 to 1.0.
    """

    name: str
    relevancy: float


def convert_topics(jo_topics: list) -> list[Topic]:

    return [Topic(**t) for t in jo_topics] if jo_topics else []
