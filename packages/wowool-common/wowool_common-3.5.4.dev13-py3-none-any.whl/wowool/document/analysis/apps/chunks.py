"""Chunk API classes"""

from dataclasses import dataclass
from wowool.document.analysis.apps.topics import convert_topics, Topic
from wowool.document.analysis.apps.themes import convert_themes, Theme


@dataclass
class Chunk:
    """Represents a chunk of text with associated metadata.

    A chunk is a segment of text that contains sentences along with their
    offsets, outline information, topics, and themes.

    Attributes:
        sentences (list): List of sentences contained in this chunk.
        begin_offset (int): Starting character position of the chunk in the document.
        end_offset (int): Ending character position of the chunk in the document.
        outline (list|None): Hierarchical outline structure for the chunk, if available.
        topics (list[Topic]|None): List of topics associated with the chunk, if any.
        themes (list[Theme]|None): List of themes associated with the chunk, if any.
    """

    sentences: list
    begin_offset: int
    end_offset: int
    outline: list | None
    topics: list[Topic] | None
    themes: list[Theme] | None


def convert_chunks(jo_chunks: dict):
    chunks = []
    for c in jo_chunks["chunks"]:
        chunk = Chunk(
            c["sentences"],
            c.get("begin_offset"),
            c.get("end_offset"),
            c.get("outline"),
            convert_topics(c.get("topics")),
            convert_themes(c.get("themes")),
        )
        chunks.append(chunk)

    return chunks
