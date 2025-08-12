import json
from functools import wraps
from io import StringIO
from wowool.annotation.sentence import Sentence
from wowool.annotation.entity import Entity
from typing import Iterator, Union, cast
from wowool.document.document_interface import DocumentInterface, MT_ANALYSIS_JSON

APP_ID = "wowool_analysis"


def _filter_pass_thru(concept: Entity) -> bool:
    return True


def _filter_pass_thru_concept(concept: Entity) -> bool:
    return concept.uri != "Sentence"


def _content_access(fnc):
    @wraps(fnc)
    def wrapper(self, *args, **kwargs):
        if self._sentences is None and self._json_data is None:
            self._json_data = self._cpp.to_json()
            current_cpp = self._cpp
            self.__dict__.update(TextAnalysis.parse(self._json_data, self.id).__dict__)
            self._cpp = current_cpp
        return fnc(self, *args, **kwargs)

    wrapper.__doc__ = fnc.__doc__
    return wrapper


class TextAnalysis:
    """
    :class:`Analysis` is a class that holds the results of an NLP analysis. Instances of this class can parse the NLP result
    and yield objects such as :class:`Sentence <wowool.annotation.sentence.Sentence>`, :class:`Token <wowool.annotation.token.Token>`
    and :class:`Entity <wowool.annotation.entity.Entity>` to conveniently access the data behind those annotations. Furthermore,
    the class also provides a static method to parse raw JSON data as returned by, for example, the Portal API.
    """

    # required buy some common decorators.
    ID = APP_ID

    @staticmethod
    def parse(json_data: Union[dict, str], id: str | None = None) -> "TextAnalysis":
        """
        Create an :class:`Analysis` instance from JSON (``dict``) data such as that returned from the Portal API.

        .. code-block:: python

            analysis = Analysis.parse(json_raw)

        :param json_data: Raw JSON representation of the NLP analysis results
        :type json_data: ``dict``

        :rtype: :class:`Analysis`
        """
        from wowool.document.analysis.analysis_parser import parse_document

        return parse_document(json_data, id)

    def __init__(
        self,
        cpp_document,
        document_id=None,
        language=None,
        sentences: list[Sentence] | None = None,
        json_data=None,
        metadata=None,
    ):
        super(TextAnalysis, self).__init__()
        self._cpp = cpp_document
        self._language = language
        self._sentences = sentences
        self._json_data = json_data
        self._metadata = metadata
        self._text = None

        if document_id is not None:
            self.id = document_id
        elif self._cpp:
            self.id = self._cpp.id()
        else:
            self.id = "none"

    @_content_access
    def __iter__(self) -> Iterator[Sentence]:
        """
        An :class:`Analysis` instance is iterable, yielding :class:`Sentence <wowool.annotation.sentence.Sentence>` objects. For example:

        .. code-block:: python

            document = analyzer("some text")
            for sentence in document: print(annotation)

        Refer to the :class:`Sentence <wowool.annotation.sentence.Sentence>` documentation for more information on further iteration.

        :rtype: :class:`Sentence <wowool.annotation.sentence.Sentence>`
        """
        assert self._sentences is not None
        return iter(self._sentences)

    @_content_access
    def __getitem__(self, index: int) -> Sentence:
        """
        :param index: Sentence index
        :type index: ``int``

        :return: The sentence at the given index or ``None`` if the index is out of range
        :rtype: :class:`Sentence <wowool.annotation.sentence.Sentence>`

        .. code-block:: python

            document = analyzer("This is the first sentence.")
            first_sentence = document.analysis[0]
        """
        assert self._sentences
        if index < len(self._sentences) and index >= 0:
            return self._sentences[index]
        else:
            raise IndexError("Sentence index out of range")

    @_content_access
    def __len__(self) -> int:
        """
        :return: The number of sentences in the processed document
        :rtype: ``int``
        """
        assert self._sentences is not None
        return len(self._sentences)

    @_content_access
    def __repr__(self):
        assert self._sentences is not None
        with StringIO() as output:
            for sentence in self._sentences:
                output.write(repr(sentence))
            return output.getvalue()

    @property
    def language(self):
        """
        :return: The identified language of the processed document
        :rtype: ``str``
        """
        if self._cpp:
            return self._cpp.language()
        else:
            return self._language

    @property
    @_content_access
    def sentences(self) -> list[Sentence]:
        """
        :return: The sentences present in the analysis
        :rtype: A ``list`` of :class:`Sentence <wowool.annotation.sentence.Sentence>` objects
        """
        return self._sentences

    @_content_access
    def rich(self):
        """
        :return: A rich string representation of the processed document object
        :rtype: ``str``
        """
        assert self._sentences
        with StringIO() as output:
            for sentence in self._sentences:
                output.write(sentence.rich())
            return output.getvalue()

    @_content_access
    def to_json(self):
        """
        :return: A dictionary representing a JSON object of the processed document
        :rtype: ``dict``
        """
        if isinstance(self._json_data, str):
            return json.loads(self._json_data)
        elif isinstance(self._json_data, dict):
            return self._json_data

    @_content_access
    def to_json_data(self) -> str:
        """
        :return: A dictionary representing a JSON object of the processed document
        :rtype: ``dict``
        """
        if isinstance(self._json_data, str):
            return self._json_data
        elif isinstance(self._json_data, dict):
            return json.dumps(self._json_data)

        return ""

    @property
    @_content_access
    def entities(self):
        from wowool.annotation import Entity

        yield from Entity.iter(self)

    @_content_access
    def concepts(self, filter=_filter_pass_thru_concept):
        """
        Access the concepts in the analysis

        :param filter: Optional filter to select or discard concepts
        :type filter: Functor accepting a :class:`Entity <wowool.annotation.Entity>` and returning a ``bool``

        :return: A generator expression yielding the concepts in the processed document
        :rtype: :class:`Concepts <wowool.annotation.Entity>`
        """
        from wowool.annotation import Entity

        for concept in Entity.iter(self, filter):
            yield concept

    @property
    @_content_access
    def tokens(self):
        """
        Access the tokens in the analysis

        :return: A generator expression yielding the concepts in the processed document
        :rtype: :class:`Concepts <wowool.annotation.token.Token>`
        """
        from wowool.annotation import Token

        yield from Token.iter(self)

    @property
    @_content_access
    def annotations(self):
        """
        Access the annotations in the analysis

        :return: A generator expression yielding the annotations in the processed document
        :rtype: :class:`Concepts <wowool.annotation.annotation.Annotation>`
        """
        from wowool.annotation import Annotation

        yield from Annotation.iter(self)

    @property
    @_content_access
    def text(self):
        """
        :return: A string representation
        :rtype: ``str``
        """
        if self._text is None:
            assert self._sentences
            with StringIO() as output:
                for sentence in self._sentences:
                    output.write(sentence.text)
                self._text = output.getvalue()
        return self._text

    def reset(self):
        """
        Reset the object, clearing all underlying data

        :rtype: :class:`Analysis`
        """
        self._sentences = None
        self._json_data = None
        return self

    @_content_access
    def internal_annotations(self):
        """
        :return: A dictionary representing a JSON object of the processed document
        :rtype: ``dict``
        """
        assert self._cpp
        return json.loads(self._cpp.internal_annotations())

    @property
    def metadata(self):
        return json.loads(self._cpp.metadata())


class AnalysisInputProvider(DocumentInterface):
    MIME_TYPE = MT_ANALYSIS_JSON
    ENCODING = "utf-8"

    def __init__(self, data: dict, id: str, metadata: dict | None = None) -> None:
        self._id = id
        self.analysis_json = data
        self._metadata = metadata if metadata is not None else {}

    @property
    def id(self) -> str:
        return self._id

    @property
    def mime_type(self) -> str:
        return MT_ANALYSIS_JSON

    @property
    def encoding(self) -> str:
        return self.ENCODING

    @property
    def data(self) -> dict:
        return self.analysis_json

    @property
    def metadata(self) -> dict:
        return self._metadata
