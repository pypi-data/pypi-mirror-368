from io import StringIO
from wowool.annotation.annotation import BasicAnnotation
from wowool.annotation.annotation_list import AnnotationList
from wowool.annotation.token import Token, Annotation
from wowool.annotation.entity import Entity
from typing import Callable, Iterator, Self


def _filter_pass_thru_concept(concept: Entity) -> bool:
    return concept.uri != "Sentence"


def _filter_pass_thru(sentence) -> bool:
    return True


class Sentence(BasicAnnotation, AnnotationList):
    """Class that contains the tokens and entities of a sentence."""

    FilterType = Callable[[Self], bool]

    def __init__(self, begin_offset: int, end_offset: int) -> None:
        """Initialize a Sentence instance.

        Args:
            begin_offset (int): Begin offset of the sentence.
            end_offset (int): End offset of the sentence.
        """
        super(Sentence, self).__init__(begin_offset, end_offset)
        self.annotations = []
        self.text_ = None
        self.attributes = {}
        self.tokens_: list[Token] | None = None

    def rich(self) -> str:
        """The rich string representation of the sentence.

        Returns:
            str: The rich string representation of the sentence.
        """
        output = StringIO()
        output.write("S:" + BasicAnnotation.__repr__(self))
        if self.is_header:
            output.write(" @( header='true' )")
        output.write("\n")
        for annotation in self.annotations:
            output.write(" ")
            output.write(annotation.rich())
            output.write("\n")
        contents = output.getvalue()
        output.close()
        return contents

    def __repr__(self) -> str:
        output = StringIO()
        output.write("S:" + BasicAnnotation.__repr__(self))
        if self.is_header:
            output.write(" @( header='true' )")
        output.write("\n")
        for annotation in self.annotations:
            output.write(" ")
            output.write(str(annotation))
            output.write("\n")
        contents = output.getvalue()
        output.close()
        return contents

    def __iter__(self):
        """Iterate over annotations in the sentence.

        A Sentence instance is iterable, yielding Annotation objects.

        Example:
            ```python
            for annotation in sentence:
                print(annotation)
            ```

        Returns:
            Iterator[Annotation]: An iterator over the annotations.
        """
        return iter(self.annotations)

    def __len__(self) -> int:
        return len(self.annotations)

    @property
    def tokens(self) -> list[Token]:
        if self.tokens_ is None:
            self.tokens_ = [a for a in self.annotations if a.is_token]
        return self.tokens_

    @property
    def entities(self):
        yield from Entity.iter(self)

    def __getattr__(self, uri: str):
        """Find the first instance of the concept with the given URI in the sentence.

        Example:
            ```python
            # Find the first person in the current sentence
            person = sentence.Person
            ```

        Args:
            uri (str): URI, or name, of the concept.

        Returns:
            Entity: The first matching instance of the given concept.
        """
        return self.find_first(uri)

    def find_first(self, uri: str):
        """Find the first instance of the entity with the given URI in the sentence.

        Example:
            ```python
            # Find a child entity in the current sentence
            person = entity.find_first('Person'))
            ```

        Args:
            uri (str): URI, or name, of the entity (ex: "Person").

        Returns:
            Entity: The first matching instance of the given entity.
        """
        concept = Entity(self.begin_offset, self.end_offset, "Sentence")
        concept._sentence_annotations = self.annotations
        concept._annotation_idx = 0
        return concept.find_first(uri)

    def find(self, uri: str):
        """Find all instances of the given entity with the given URI in the sentence.

        Example:
            ```python
            # List all persons in the sentence
            for person in entity.find('Person')):
                print(person)
            ```

        Args:
            uri (str): URI, or name, of the concept.

        Returns:
            List[Entity]: The matching instances of the given concept.
        """
        concept = Entity(self.begin_offset, self.end_offset, "Sentence")
        concept._sentence_annotations = self.annotations
        concept._annotation_idx = 0
        return concept.find(uri)

    def __getitem__(self, value) -> Annotation | None:
        return self.annotations[value] if value < len(self.annotations) else None

    @property
    def text(self):
        """Get a string representation of the sentence.

        Returns:
            str: A string representation of the sentence.
        """
        retval = ""
        prev_tk = None
        for tk in [a for a in self.annotations if a.is_token]:
            if prev_tk:
                if prev_tk.end_offset != tk.begin_offset:
                    retval += " "
            retval += tk.literal
            prev_tk = tk
        return retval.strip()

    @property
    def lemma(self):
        """Get a string representation of the sentence with the lemmas.

        Returns:
            str: A string representation of the sentence with the lemmas.
        """
        if self.text_ is None:
            retval = ""
            prev_tk = None
            for tk in [a for a in self.annotations if a.is_token]:
                if prev_tk:
                    if prev_tk.end_offset != tk.begin_offset:
                        retval += " "
                retval += tk.lemma
                prev_tk = tk
            self.text_ = retval.strip()
        return self.text_

    @property
    def lemmas(self):
        """Get a list of lemmas for all tokens in the sentence.

        Returns:
            List[str]: A list of lemmas for all tokens in the sentence.
        """
        return [token.lemma for token in self.tokens]

    @property
    def stems(self):
        """Get a list of stems for all tokens in the sentence.

        Returns:
            List[str]: A list of stems for all tokens in the sentence.
        """
        return self.lemmas

    @property
    def is_header(self) -> bool:
        """Check if the sentence is a header.

        Returns:
            bool: True if the sentence is a header.
        """
        return self.attributes.get("header", []) == ["true"]

    def concepts(self, filter=_filter_pass_thru_concept):
        yield from Entity.iter(self, filter)

    @staticmethod
    def _document_iter(doc, filter: FilterType = _filter_pass_thru) -> Iterator["Sentence"]:
        """Iterate over sentences in a document."""
        for sentence in doc:
            if filter(sentence):
                yield sentence

    @staticmethod
    def _paragraph_iter(paragraph, filter: FilterType = _filter_pass_thru) -> Iterator["Sentence"]:
        """Iterate over sentences in a paragraph."""
        for sentence in paragraph.sentences:
            if filter(sentence):
                yield sentence

    @staticmethod
    def iter(object, filter: FilterType = _filter_pass_thru, align: bool = True) -> Iterator["Sentence"]:
        from wowool.document.analysis.document import AnalysisDocument
        from wowool.document.analysis.text_analysis import TextAnalysis
        from wowool.annotation.paragraph import Paragraph

        if isinstance(object, AnalysisDocument) and object.analysis:
            yield from Sentence._document_iter(object.analysis, filter)
        elif isinstance(object, TextAnalysis):
            yield from Sentence._document_iter(object, filter)
        elif isinstance(object, Paragraph):
            yield from Sentence._paragraph_iter(object, filter)
        else:
            raise TypeError(f"Expected Document, Analysis, Sentence, or Entity but got '{type(object)}'")
