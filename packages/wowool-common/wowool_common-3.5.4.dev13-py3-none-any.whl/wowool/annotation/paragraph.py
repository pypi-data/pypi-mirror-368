from __future__ import annotations
from wowool.annotation.annotation import Annotation
from wowool.annotation.sentence import Sentence
from wowool.annotation.token import Token
from typing import Callable, List, cast, Iterator, Self


class Paragraph(Annotation):
    """Class that contains all the information about a paragraph."""

    FilterType = Callable[[Self], bool]

    def __init__(self, begin_offset: int, end_offset: int):
        """Initialize a Paragraph instance.

        Args:
            begin_offset (int): Begin offset of the paragraph.
            end_offset (int): End offset of the paragraph.
        """
        self._attributes = {}
        super(Paragraph, self).__init__(begin_offset, end_offset)
        self._sentence_annotations = None
        self._dict = None
        self._canonical = None
        self._text = None

    def _get_text(self) -> str:
        """Get a string representation of the paragraph.

        Returns:
            str: A string representation of the paragraph.
        """
        if not isinstance(self._sentence_annotations, list):
            return ""

        retval = ""
        prev_tk = None
        for tk in [a for a in self._sentence_annotations if a.is_token]:
            if prev_tk and prev_tk.end_offset != tk.begin_offset:
                retval += " "
            retval += tk.literal
            prev_tk = tk
        return retval.strip()

    @property
    def sentences(self) -> List[Sentence]:
        """Get a list of the sentence annotations in the paragraph

        Returns:
            list[Sentence]: A list of the sentence annotations in the paragraph.
        """
        if self._sentence_annotations is None:
            return []
        return self._sentence_annotations

    @property
    def text(self):
        """Get a string representation of the paragraph.

        Returns:
            str: A string representation of the paragraph.
        """
        if self._text is None:
            self._text = self._get_text()
        return self._text

    def __setstate__(self, d):
        self.__dict__.update(d)

    def __getstate__(self):
        return self.__dict__

    def keys(self):
        """Convert a paragraph object to a dictionary and return its keys.

        This function is used to convert a paragraph object to a dictionary.

        Example:
            ```python
            { **paragraph }
            ```

        Returns:
            List[str]: A list of the keys of the paragraph.
        """
        if not self._dict:
            self._dict = self.to_json()
        return self._dict.keys()

    def __repr__(self) -> str:
        retval = "P:" + Annotation.__repr__(self)
        return retval

    @staticmethod
    def same_paragraph(original_text: str, prev: Sentence, next: Sentence) -> bool:
        annotation = prev.annotations[-1]

        if prev.is_header and not next.is_header:
            return True

        prev_last_token = cast(Token, annotation) if annotation.is_token else None
        if prev_last_token and prev_last_token.has_pos("Punct-Line"):
            return True
        if (next.begin_offset - prev.end_offset) >= 2:
            doc_text = original_text[prev.end_offset : next.begin_offset]
            if "\r" in doc_text:
                doc_text = doc_text.replace("\r", "")
            pos = doc_text.find("\n")
            if pos == -1:
                return True
            elif (pos := doc_text.find("\n", pos + 1)) == -1:
                return True
            else:
                return False

        return True

    @staticmethod
    def _document_iter(doc, original_text: str) -> Iterator[Paragraph]:

        paragraph = Paragraph(0, 0)
        for sentence in doc:
            if paragraph._sentence_annotations is None:
                paragraph._sentence_annotations = [sentence]
                paragraph._begin_offset = sentence.begin_offset
            else:
                if Paragraph.same_paragraph(original_text, paragraph._sentence_annotations[-1], sentence):
                    paragraph._sentence_annotations.append(sentence)
                else:
                    paragraph._end_offset = paragraph._sentence_annotations[-1].end_offset
                    yield paragraph
                    paragraph = Paragraph(sentence.begin_offset, 0)
                    paragraph._sentence_annotations = [sentence]
        if paragraph._sentence_annotations:
            paragraph._end_offset = paragraph._sentence_annotations[-1].end_offset
            yield paragraph

    @staticmethod
    def iter(object, original_text: str) -> Iterator["Paragraph"]:
        """Iterate over the paragraphs in a document or analysis.

        Example:
            ```python
            document = analyzer("Hello from Antwerp, said John Smith.")
            for paragraph in Paragraph.iter(document):
                print(paragraph)
            ```

        Args:
            object(AnalysisDocument|TextAnalysis): Object to iterate the paragraphs.
            original_text (str, optional): The original text to use for paragraph detection.
            align (bool): Whether to align the iteration.

        Returns:
            Iterator[Paragraph]: A generator expression yielding paragraphs.

        Raises:
            TypeError: If object type is not supported.
        """
        from wowool.document.analysis.document import AnalysisDocument
        from wowool.document.analysis.text_analysis import TextAnalysis

        if original_text is None and isinstance(object, AnalysisDocument):
            original_text = object.text

        if isinstance(object, AnalysisDocument) and object.analysis:
            yield from Paragraph._document_iter(object.analysis, original_text)
        elif isinstance(object, TextAnalysis):
            yield from Paragraph._document_iter(object, original_text)
        else:
            raise TypeError(f"Expected Document, Analysis, but got '{type(object)}'")
