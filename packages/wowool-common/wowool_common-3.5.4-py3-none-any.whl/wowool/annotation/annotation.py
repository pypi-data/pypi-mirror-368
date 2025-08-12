from typing import Iterator


class BasicAnnotation:
    """Base class for all annotations."""

    __slott__ = ["begin_offset", "end_offset"]

    def __init__(self, begin_offset: int, end_offset: int):
        """Initialize a BasicAnnotation instance.

        Args:
            begin_offset (int): Begin offset of the annotation.
            end_offset (int): End offset of the annotation.
        """
        self._begin_offset: int = begin_offset
        self._end_offset: int = end_offset

    def __repr__(self):
        return "({:>3},{:>3})".format(self.begin_offset, self.end_offset)

    @property
    def begin_offset(self) -> int:
        """The begin offset of the annotation."""
        return self._begin_offset

    @property
    def end_offset(self) -> int:
        """The end offset of the annotation."""
        return self._end_offset

    @property
    def is_concept(self) -> bool:
        """Whether the annotation is an Entity (deprecated, use is_entity instead)."""
        return self.is_entity

    @property
    def is_entity(self) -> bool:
        """Whether the annotation is an Entity."""
        from wowool.annotation.entity import Entity

        return isinstance(self, Entity)

    @property
    def is_sentence(self) -> bool:
        """Whether the annotation is a Sentence."""
        from wowool.annotation.sentence import Sentence

        return isinstance(self, Sentence)

    @property
    def is_token(self) -> bool:
        """Whether the annotation is a Token."""
        from wowool.annotation.token import Token

        return isinstance(self, Token)

    @property
    def is_paragraph(self) -> bool:
        """Whether the annotation is a Paragraph."""
        from wowool.annotation.paragraph import Paragraph

        return isinstance(self, Paragraph)


class Annotation(BasicAnnotation):
    """Base class for all annotations."""

    __slott__ = ["begin_offset", "end_offset"]

    def __init__(self, begin_offset: int, end_offset: int):
        """Initialize an Annotation instance.

        Args:
            begin_offset (int): Begin offset of the annotation.
            end_offset (int): End offset of the annotation.
        """
        super(Annotation, self).__init__(begin_offset, end_offset)
        self._annotation_idx = None

    @property
    def index(self) -> int:
        assert self._annotation_idx is not None
        return self._annotation_idx

    @staticmethod
    def _document_iter(doc) -> Iterator["Annotation"]:
        for sentence in doc:
            yield sentence
            for annotation in sentence:
                yield annotation

    @staticmethod
    def _sentence_iter(sentence) -> Iterator["Annotation"]:
        for annotation in sentence:
            yield annotation

    @staticmethod
    def iter(object) -> Iterator["Annotation"]:
        """Iterate over the annotations in a document, analysis, or sentence.

        Example:
            ```python
            document = analyzer("Hello from Antwerp, said John Smith.")
            for concept in Entity.iter(document, lambda concept : concept.uri == "NP"):
                print(concept)
            ```

        Args:
            object (AnalysisDocument|TextAnalysis|Sentence): Object to iterate over (Analysis, Sentence, or Entity).

        Returns:
            Iterator: Generator yielding annotations.

        Raises:
            TypeError: If object type is not supported.
        """
        from wowool.document.analysis.document import AnalysisDocument
        from wowool.document.analysis.text_analysis import TextAnalysis
        from wowool.annotation import Sentence

        if isinstance(object, AnalysisDocument) and object.analysis:
            yield from Annotation._document_iter(object.analysis)
        elif isinstance(object, TextAnalysis):
            yield from Annotation._document_iter(object)
        elif isinstance(object, Sentence):
            yield from Annotation._sentence_iter(object)
        else:
            raise TypeError(f"Expected Document, TextAnalysis, Sentence, but got '{type(object)}'")
