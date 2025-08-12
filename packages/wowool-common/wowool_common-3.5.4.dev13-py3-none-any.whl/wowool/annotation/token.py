from __future__ import annotations
from wowool.annotation.annotation import Annotation
from wowool.annotation.annotation_list import AnnotationList
from typing import List, MutableSet, cast, Generator
import warnings
from typing import NewType

Entity = NewType("Entity", Annotation)
TokenType = NewType("TokenType", Annotation)


class Token(Annotation):
    """Token is a class that contains all the information about a token.

    This class represents a token with its position, literal text, morphological
    data, and properties within a document.
    """

    __slots__ = ["literal", "_morphology", "_properties"]

    def __init__(self, begin_offset: int, end_offset: int, literal: str):
        """Initialize a Token instance.

        Args:
            begin_offset (int): Begin offset of the token.
            end_offset (int): End offset of the token.
            literal (str): Literal string from the input document.
        """
        super(Token, self).__init__(begin_offset, end_offset)
        self.literal: str = literal
        self._morphology: list["MorphData"] = []
        self._properties: MutableSet[str] = set()

    @property
    def morphology(self) -> list["MorphData"]:
        """Get the morphological data of the token.

        Returns:
            List[MorphData]: A list of MorphData objects containing morphological information.
        """
        return self._morphology

    @property
    def properties(self) -> MutableSet[str]:
        """Get the properties of the token.

        Returns:
            MutableSet[str]: A set of properties associated with the token.
        """
        return self._properties

    def _set_morphology(self, morphology: list[MorphData]):
        """Set the morphological data of the token.

        Args:
            morphology (list[MorphData]): A list of MorphData objects to set.
        """
        self._morphology = morphology

    def _set_properties(self, properties: MutableSet[str]):
        """Set the properties of the token.

        Args:
            properties (MutableSet[str]): A set of properties to set.
        """
        self._properties = properties

    def rich(self):
        """Get the rich string representation of the token.

        Returns:
            str: The rich string representation of the token with XML-like formatting.
        """
        retval = "<token>T</token>:" + Annotation.__repr__(self) + ": <literal>" + self.literal + "</literal>"
        if self.properties:
            retval += ",{"
            for idx, prop in enumerate(sorted(self.properties)):
                if idx != 0:
                    retval += ", "
                retval += "+" + prop
            retval += "}"

        if self._morphology:
            retval += ","
            for morph_info in self._morphology:
                retval += morph_info.rich()

        return retval

    def __repr__(self):
        retval = "T:" + Annotation.__repr__(self) + ": " + self.literal
        if self.properties:
            retval += ",{"
            for idx, prop in enumerate(sorted(self.properties)):
                if idx != 0:
                    retval += ", "
                retval += "+" + prop
            retval += "}"

        if self._morphology:
            retval += ","
            for morph_info in self._morphology:
                retval += str(morph_info)

        return retval

    @property
    def lemma(self) -> str:
        """Get the first lemma of the token.

        Returns:
            str: The first lemma of the token or an empty string if absent.
        """
        for morph_info in self._morphology:
            return morph_info.lemma
        return ""

    @property
    def stem(self) -> str:
        """Get the first lemma of the token (alias for lemma).

        Returns:
            str: The first lemma of the token or an empty string if absent.
        """
        for morph_info in self._morphology:
            return morph_info.lemma
        return ""

    @property
    def pos(self) -> str:
        """Get the first part-of-speech of the token.

        Returns:
            str: The first part-of-speech of the token or an empty string if absent.
        """
        for morph_info in self._morphology:
            return morph_info.pos
        return ""

    def has_property(self, prop: str) -> bool:
        """Check whether a given property is set on the token.

        Args:
            prop (str): Property name. For example "nf".

        Returns:
            bool: Whether a given property is set on the token.
        """
        return prop in self.properties

    def has_pos(self, pos: str) -> bool:
        """Check whether a given part-of-speech is set on the token.

        Args:
            pos (str): Part-of-speech. For example "Nn".

        Returns:
            bool: Whether a given part-of-speech is set on the token.
        """
        for morph_info in self._morphology:
            if morph_info.pos.startswith(pos):
                return True
        return False

    def get_morphology(self, pos: str):
        """Get morphological data for a given part-of-speech.

        Args:
            pos (str): Part-of-speech. For example "Nn".

        Returns:
            MorphData|None: The morphological data if found, None otherwise.
        """
        for morph_info in self._morphology:
            if morph_info.pos.startswith(pos):
                return morph_info

    def __len__(self) -> int:
        """Get the length of the token in the input document in bytes.

        This takes Unicode characters into account.

        Returns:
            int: The length of the token in the input document in bytes.
        """
        return self.end_offset - self.begin_offset

    def __bool__(self) -> bool:
        return self._begin_offset != -1

    @staticmethod
    def _document_iter(doc) -> Generator[Token, None, None]:
        for sentence in doc:
            for annotation in sentence:
                if annotation.is_token:
                    yield cast(Token, annotation)

    @staticmethod
    def _concept_iter(concept) -> Generator[Token, None, None]:
        for annotation in concept.annotations:
            if annotation.is_token:
                yield cast(Token, annotation)

    @staticmethod
    def iter(object) -> Generator[Token, None, None]:
        """Iterate over the tokens in a document, analysis, sentence or concept.

        Example:
            ```python
            document = analyzer("Hello from Antwerp, said John Smith.")
            for token in Token.iter(document):
                print(token)
            ```

        Args:
            object (AnalysisDocument|TextAnalysis|Sentence|Entity): Object to iterate. Can be AnalysisDocument, TextAnalysis,
                Sentence or Entity.

        Returns:
            Generator[Token, None, None]: A generator expression yielding tokens.

        Raises:
            TypeError: If the object type is not supported.
        """
        from wowool.document.analysis.document import AnalysisDocument
        from wowool.document.analysis.text_analysis import TextAnalysis
        from wowool.annotation import Sentence, Entity

        if isinstance(object, AnalysisDocument) and object.analysis:
            yield from Token._document_iter(object.analysis)
        elif isinstance(object, TextAnalysis):
            yield from Token._document_iter(object)
        elif isinstance(object, Sentence):
            for annotation in object:
                if isinstance(annotation, Token):
                    yield cast(Token, annotation)
        elif isinstance(object, Entity):
            yield from Token._concept_iter(object)
        else:
            raise TypeError(f"Expected Document, TextAnalysis, Sentence, or Entity but got '{type(object)}'")

    @staticmethod
    def next(sentence: AnnotationList | list[Annotation], object: Token) -> "Token|None":
        """Return the next Token.

        Args:
            sentence (Sentence): The sentence containing the tokens.
            object (Token): The current object to find the next token from.

        Returns:
            Token|None: The next token in the sentence or None if not found.

        """
        index = object.index + 1
        sentence_length = len(sentence)
        while index < sentence_length:
            if sentence[index].is_token:
                return cast(Token, sentence[index])
            else:
                index += 1

        return None

    @staticmethod
    def prev(sentence: AnnotationList | list[Annotation], object: Entity | Token) -> Token | None:
        """Return the previous Token.

        Args:
            sentence (Sentence|list[Annotation]): The sentence containing the tokens.
            object (Entity|Token): The current object to find the previous token from.

        Returns:
            Token|None: The previous token in the sentence or None if not found.

        """
        index = object.index - 1
        while index >= 0:
            if sentence[index].is_token:
                return cast(Token, sentence[index])
            else:
                index -= 1
        return None


class MorphData:
    """MorphData is a class that contains the morphological data.

    Example:
        ```python
        for md in token.morphology:
            print(md.pos, md.lemma)
        ```

    Attributes:
        pos (str): Part-of-speech.
        lemma (str): Lemma.
    """

    __slots__ = ["_pos", "_lemma", "_morphology"]

    def __init__(self):
        self._pos: str = "None"
        self._lemma: str = ""
        self._morphology = None

    @property
    def pos(self) -> str:
        """Get the part-of-speech of the morphological data.

        Returns:
            str: The part-of-speech of the morphological data.
        """
        return self._pos

    @property
    def lemma(self) -> str:
        """Get the lemma of the morphological data.

        Returns:
            str: The lemma of the morphological data.
        """
        return self._lemma

    @property
    def morphology(self) -> List[MorphData] | None:
        """Get the morphology of the morphological data.

        Returns:
            List[MorphData]: An empty list as MorphData does not have morphology.
        """
        return self._morphology

    def set_morphology(self, morphology: List[MorphData]):
        """Set the morphology of the morphological data.

        Args:
            morphology (List[MorphData]): A list of MorphData objects to set.
        """
        self._morphology = morphology

    def rich(self) -> str:
        """Get the rich string representation of the morphological data.

        Returns:
            str: The rich string representation of the morphological data.
        """
        retval = "['<lemma>" + self.lemma + "</lemma>':" + self.pos + "]"
        if self._morphology is not None:
            self._morphology: List[MorphData]
            for md in self._morphology:
                retval += md.rich()
        return retval

    def __repr__(self) -> str:
        retval = f"[{self.lemma}:{self.pos}"
        if self._morphology is not None:
            retval += ",["
            self._morphology: List[MorphData]
            for md in self._morphology:
                retval += str(md)
            retval += "]"
        retval += "]"
        return retval

    @property
    def stem(self) -> str:
        """The lemma of the morphological data (deprecated, use lemma instead).

        Returns:
            str: The lemma of the morphological data.
        """
        warnings.warn("The 'stem' property is deprecated, use 'lemma' instead.", DeprecationWarning)
        return self.lemma

    def __setstate__(self, d):
        self.__dict__.update(d)

    def __getstate__(self):
        return self.__dict__


TokenNone = Token(-1, -1, "")
