from io import StringIO
from typing import Union, Any, Generator
from wowool.annotation import Entity, Annotation, Token, Sentence, Paragraph
import json
from wowool.diagnostic import Diagnostics
from wowool.document.analysis.text_analysis import (
    _filter_pass_thru_concept,
    TextAnalysis,
    AnalysisInputProvider,
)
from wowool.document.analysis.text_analysis import APP_ID as APP_ID_ANALYSIS
from typing import cast
from wowool.document.analysis.apps.topics import convert_topics, Topic
from wowool.document.analysis.apps.themes import convert_themes, Theme
from wowool.document.analysis.apps.chunks import convert_chunks, Chunk
from wowool.document.analysis.apps.sentiments import convert_sentiments, SentimentResults
from wowool.document.analysis.apps.anonymizer import convert_anonymizer, AnonymizerResults
from wowool.document.analysis.apps.lid import convert_lid, LanguageIdentifierResults
from wowool.document.analysis.apps.entity_graph import convert_entity_graph, Link
from wowool.document.document_interface import DocumentInterface, MT_PLAINTEXT, MT_ANALYSIS_JSON
from wowool.document.document import Document
from wowool.document.defines import WJ_ID, WJ_DATA, WJ_MIME_TYPE, WJ_METADATA, WJ_ENCODING
from json import JSONEncoder
from wowool.document.analysis.document_format_exception import InvalidDocumentFormatException


RESULTS = "results"
DIAGNOSTICS = "diagnostics"


class AnalysisJsonEncoder(JSONEncoder):
    """Custom JSON encoder for analysis data that handles sets and objects with to_json methods."""

    def default(self, obj):
        """Handle encoding of custom objects.

        Args:
            obj (Any): The object to encode.

        Returns:
            Any: The encoded object.
        """
        if isinstance(obj, set):
            return list(obj)
        else:
            return getattr(obj, "to_json")() if hasattr(obj, "to_json") else super().default(obj)


def to_json_convert(obj):
    """Convert objects to JSON-compatible format.

    Args:
        obj (Any): The object to convert.

    Returns:
        Any: The converted object.
    """
    if isinstance(obj, set):
        return str(list(obj))
    return obj


STR_MISSING_ANALYSIS = "Document has not been processed by a Language"


class AnalysisDocument(DocumentInterface):
    """AnalysisDocument is a class that stores the data related to a document.

    Instances of this class are returned from a Pipeline, Language or Domain object.
    """

    MIME_TYPE = MT_ANALYSIS_JSON

    def __init__(self, document: DocumentInterface, metadata: dict | None = None):
        """Initialize an AnalysisDocument instance.

        Args:
            document (DocumentInterface): The input document to analyze.
            metadata (dict|None): Document metadata. Defaults to None.
        """
        super().__init__()

        self.input_document = document
        self._metadata = metadata if metadata is not None else {**self.input_document.metadata}
        self._apps = {}
        self._text = document.data if document.mime_type == MT_PLAINTEXT else None
        self.pipeline_concepts = cast(set[str], set())

    @property
    def text(self) -> str | None:
        """Get the text data of the document.

        Returns:
            str|None: The text data of the document.
        """
        return self._text

    @property
    def id(self) -> str:
        """Get the unique identifier of the document.

        Returns:
            str: The unique identifier of the document.
        """
        return self.input_document.id

    @property
    def mime_type(self) -> str:
        """Get the data type of the document.

        Returns:
            str: The data type of the document.
        """
        return AnalysisDocument.MIME_TYPE

    @property
    def encoding(self) -> str:
        """Get the encoding of the document.

        Returns:
            str: The encoding of the document.
        """
        return "utf-8"

    @property
    def data(self) -> str:
        """Get the text data of the document.

        Returns:
            str: The text data of the document.
        """

        analysis_data = self._apps
        return json.loads(json.dumps(analysis_data, cls=AnalysisJsonEncoder))

    @property
    def metadata(self) -> dict:
        """Get the metadata of the document.

        Returns:
            dict: The metadata of the document.
        """
        return self._metadata

    @property
    def analysis(self) -> TextAnalysis:
        """Get the Analysis of the document.

        Contains the Sentences, Tokens and Concepts, or None if the document
        has not been processed by a Language.

        Returns:
            TextAnalysis | None: The Analysis of the document containing the
                Sentences, Tokens and Concepts.
        """
        return cast(TextAnalysis, self.results(APP_ID_ANALYSIS))

    def app_ids(self):
        """Iterate over the application identifiers.

        Yields:
            str: Application identifiers.
        """
        for app_id in self._apps:
            yield app_id

    def has(self, app_id: str) -> bool:
        """Check if the application has results.

        Args:
            app_id (str): Application identifier.

        Returns:
            bool: True if the application has results, False otherwise.
        """
        return self.has_results(app_id)

    def has_results(self, app_id: str) -> bool:
        """Check if the application has results.

        Args:
            app_id (str): Application identifier.

        Returns:
            bool: True if the application is in the document, False otherwise.
        """
        return app_id in self._apps

    def add_results(self, app_id: str, results):
        """Add the given application results to the document.

        Args:
            app_id (str): Application identifier.
            results (Any): Application results (a JSON serializable object type).

        Returns:
            Any: The results that were added.
        """
        if app_id in self._apps:
            self._apps[app_id][RESULTS] = results
        else:
            self._apps[app_id] = {RESULTS: results}
        return results

    def results(self, app_id: str) -> Union[Any, None]:
        """Get the results of the given application.

        Args:
            app_id (str): Application identifier.

        Returns:
            Any|None: The results of the given application. See the different types
                of application results in the documentation.
        """
        if app_id in self._apps and RESULTS in self._apps[app_id]:
            return self._apps[app_id][RESULTS]

    def add_diagnostics(self, app_id: str, diagnostics: Diagnostics):
        """Add the given application diagnostics to the document.

        Args:
            app_id (str): Application identifier.
            diagnostics (Diagnostics): Application diagnostics.
        """
        if app_id in self._apps:
            self._apps[app_id][DIAGNOSTICS] = diagnostics
        else:
            self._apps[app_id] = {DIAGNOSTICS: diagnostics}

    def has_diagnostics(self, app_id: str | None = None) -> bool:
        """Check if the document contains diagnostics.

        Args:
            app_id (str|None): Application identifier. If None, checks
                for any diagnostics. Defaults to None.

        Returns:
            bool: True if the document contains diagnostics for the given application
                or any diagnostics if no application identifier is provided.
        """
        if app_id is None:
            for app_id in self._apps:
                if DIAGNOSTICS in self._apps[app_id]:
                    return True
            return False
        else:
            if app_id in self._apps and DIAGNOSTICS in self._apps[app_id]:
                return True
            else:
                return False

    def diagnostics(self, app_id: str | None = None) -> Diagnostics:
        """Get the diagnostics of the given application.

        Args:
            app_id (str|None): Application identifier. If None, returns
                all diagnostics. Defaults to None.

        Returns:
            Diagnostics: The diagnostics of the given application.

        Raises:
            ValueError: If the app has no diagnostics.
        """
        if app_id is None:
            diagnostics = Diagnostics()
            for _, app_data in self._apps.items():
                if DIAGNOSTICS in app_data:
                    diagnostics.extend(app_data[DIAGNOSTICS])
            return diagnostics
        else:
            if app_id in self._apps and DIAGNOSTICS in self._apps[app_id]:
                return self._apps[app_id][DIAGNOSTICS]
            else:
                raise ValueError(f"App '{app_id}' has no diagnostics")

    def to_json(self) -> dict:
        """Convert the document to a JSON dictionary.

        Returns:
            dict: A dictionary representing a JSON object of the document.
        """
        from json import JSONEncoder

        class Encoder(JSONEncoder):
            def default(self, obj):
                """Handle encoding of custom objects.

                Args:
                    obj (Any): The object to encode.

                Returns:
                    Any: The encoded object.
                """
                if isinstance(obj, set):
                    return list(obj)
                else:
                    return getattr(obj, "to_json")() if hasattr(obj, "to_json") else super().default(obj)

        document = {
            WJ_ID: self.id,
            WJ_MIME_TYPE: AnalysisInputProvider.MIME_TYPE,
            WJ_DATA: self.data,
            WJ_ENCODING: AnalysisInputProvider.ENCODING,
            WJ_METADATA: self.metadata,
        }
        return json.loads(json.dumps(document, cls=Encoder))

    @staticmethod
    def from_dict(document_json: dict) -> "AnalysisDocument":
        """Create an AnalysisDocument from a dictionary.

        Args:
            document_json (dict): JSON dictionary containing document data.

        Returns:
            AnalysisDocument: A new AnalysisDocument instance.

        Raises:
            AssertionError: If the document JSON format is invalid.
            InvalidDocumentFormatException: If app data format is invalid.
        """
        assert WJ_ID in document_json, "Invalid Document json format"
        assert WJ_MIME_TYPE in document_json, "Invalid Document json format"
        json_doc = document_json
        assert WJ_DATA in json_doc, "Invalid Document json format"

        input_document = Document.create(**json_doc)
        doc = AnalysisDocument(input_document)
        assert AnalysisInputProvider.MIME_TYPE == doc.mime_type
        doc._apps = input_document.data

        if APP_ID_ANALYSIS in doc._apps:
            analysis_ = doc._apps[APP_ID_ANALYSIS]
            assert isinstance(analysis_, dict), f"Expected dict, not '{type(analysis_)}'"
            # phforest : this should no be a assert, in case we have errors there will be no results.
            # assert RESULTS in analysis_, f"Missing {RESULTS} in {APP_ID_ANALYSIS}"
            if RESULTS in analysis_:
                analysis = TextAnalysis.parse(analysis_[RESULTS])
                # doc.input_document = AnalysisInputProvider(json.dumps(analysis_[RESULTS]), doc.id)
                doc.add_results(APP_ID_ANALYSIS, analysis)

        for _, app_data in doc._apps.items():
            if isinstance(app_data, dict):
                if diagnostics := app_data.get(DIAGNOSTICS):
                    app_data[DIAGNOSTICS] = Diagnostics.from_json(diagnostics)
            else:
                raise InvalidDocumentFormatException(f"App data for '{_}' is not a dict: {type(app_data)}")

        return doc

    @staticmethod
    def from_document(doc: "AnalysisDocument") -> "AnalysisDocument":
        """Create an AnalysisDocument from another AnalysisDocument.

        Args:
            doc (AnalysisDocument): The document to copy from.

        Returns:
            AnalysisDocument: A new AnalysisDocument instance.
        """

        assert AnalysisInputProvider.MIME_TYPE == doc.mime_type
        doc._apps = doc.data

        if APP_ID_ANALYSIS in doc._apps:
            analysis_ = doc._apps[APP_ID_ANALYSIS]
            assert isinstance(analysis_, dict), f"Expected dict, not '{type(analysis_)}'"
            # phforest : this should no be a assert, in case we have errors there will be no results.
            # assert RESULTS in analysis_, f"Missing {RESULTS} in {APP_ID_ANALYSIS}"
            if RESULTS in analysis_:
                analysis = TextAnalysis.parse(analysis_[RESULTS])
                # doc.input_document = AnalysisInputProvider(json.dumps(analysis_[RESULTS]), doc.id)
                doc.add_results(APP_ID_ANALYSIS, analysis)

        for _, app_data in doc._apps.items():
            if diagnostics := app_data.get(DIAGNOSTICS):
                app_data[DIAGNOSTICS] = Diagnostics.from_json(diagnostics)

        return doc

    def concepts(self, filter=_filter_pass_thru_concept):
        """Access the concepts in the analysis of the document.

        Args:
            filter (callable, optional): Optional filter to select or discard concepts.
                Should accept an Entity and return a bool. Defaults to pass-through filter.

        Yields:
            Entity: The concepts in the processed document.
        """
        return self.analysis.concepts(filter) if self.analysis else iter([])

    def __repr__(self):
        if self.text:
            sz = len(self.text) if self.text else 0
            text = '"' + self.text[:50].strip().replace("\n", " ") + '"' if self.text else None
            return f"<AnalysisDocument id={self.id} mime_type={self.mime_type} size={sz} text={text} >"
        else:
            return f"<AnalysisDocument id={self.id} mime_type={self.mime_type} >"

    def __str__(self):
        with StringIO() as output:
            if self.analysis:
                output.write(str(self.analysis))
            else:
                output.write(self.__repr__())
                output.write("\n")

            # print the rest of the applications.
            for app_id, app_data in self._apps.items():
                if app_id == APP_ID_ANALYSIS:
                    # we already have printed the self.analysis
                    continue

                if RESULTS in app_data:
                    output.write(f"{app_id}, {json.dumps(app_data[RESULTS], indent=2)}\n")
                elif DIAGNOSTICS in app_data:
                    output.write(f"{app_id}, {app_data[DIAGNOSTICS].to_json()}\n")

            return output.getvalue()

    @property
    def entities(self) -> Generator[Entity, Any, None]:
        """Get the entities of the document.

        Returns:
            Generator[Entity, Any, None]: The entities of the document.

        Raises:
            ValueError: If the document has not been processed by a Language.
        """
        if self.analysis is not None:
            yield from self.analysis.entities
        else:
            raise ValueError(STR_MISSING_ANALYSIS)

    @property
    def tokens(self) -> Generator[Token, Any, None]:
        """Get the tokens of the document.

        Returns:
            Generator[Token, Any, None]: The tokens of the document.

        Raises:
            ValueError: If the document has not been processed by a Language.
        """
        if self.analysis is not None:
            yield from self.analysis.tokens
        else:
            raise ValueError(STR_MISSING_ANALYSIS)

    @property
    def annotations(self) -> Generator[Annotation, Any, None]:
        """Get the annotations of the document.

        Returns:
            Generator[Annotation, Any, None]: The annotations of the document.

        Raises:
            ValueError: If the document has not been processed by a Language.
        """
        if self.analysis is not None:
            yield from self.analysis.annotations
        else:
            raise ValueError(STR_MISSING_ANALYSIS)

    @property
    def sentences(self) -> Generator[Sentence, Any, None]:
        """Get the sentences of the document.

        Returns:
            Generator[Sentence, Any, None]: The sentences of the document.

        Raises:
            ValueError: If the document has not been processed by a Language.
        """

        if self.analysis is not None:
            yield from self.analysis.sentences
        else:
            raise ValueError(STR_MISSING_ANALYSIS)

    @property
    def paragraphs(self) -> Generator[Paragraph, Any, None]:
        """Get the paragraphs of the document.

        Returns:
            Generator[Paragraph, Any, None]: The paragraphs of the document.

        Raises:
            ValueError: If the document has not been processed by a Language.
        """
        if self.analysis is not None and self.text is not None:
            yield from Paragraph.iter(self.analysis, self.text)
        else:
            raise ValueError(STR_MISSING_ANALYSIS)

    @property
    def topics(self) -> list[Topic]:
        """Get the topics of the document.

        Returns:
            `list[Topic]`: The topics of the document.
        """
        if topics_results := self.results("wowool_topics"):
            return convert_topics(topics_results)
        else:
            return []

    @property
    def categories(self) -> list[Theme]:
        """Get the categories of the document.

        Returns:
            list[Theme]: The categories of the document.
        """
        if themes_results := self.results("wowool_themes"):
            return convert_themes(themes_results)
        else:
            return []

    @property
    def chunks(self) -> list[Chunk]:
        """Get the chunks data of the document.

        Returns:
            list[Chunk]: The chunks data of the document.
        """
        if chuck_results := self.results("wowool_chunks"):
            return convert_chunks(chuck_results)
        else:
            return []

    @property
    def sentiments(self) -> SentimentResults | None:
        """Get the sentiments of the document.

        Returns:
            SentimentResults|None: The sentiments of the document.
        """
        if sentiments_results := self.results("wowool_sentiments"):
            return convert_sentiments(sentiments_results)
        else:
            return None

    @property
    def anonymizer(self) -> AnonymizerResults | None:
        """Get the anonymizer results of the document.

        Returns:
            AnonymizerResults|None: The anonymizer results of the document.
        """
        if anonymizer_results := self.results("wowool_anonymizer"):
            return convert_anonymizer(anonymizer_results)
        else:
            return None

    @property
    def lid(self) -> LanguageIdentifierResults | None:
        """Get the language identifier results of the document.

        Returns:
            LanguageIdentifierResults|None: The language identifier results.
        """
        if not hasattr(self, "_lid_results"):
            if lid_results := self.results("wowool_language_identifier"):
                self._lid_results = convert_lid(lid_results)
            else:
                self._lid_results = None

        return self._lid_results

    @property
    def themes(self) -> list[Theme] | list:
        """Get the themes/categories of the document.

        Returns:
            list[Theme]: The themes/categories of the document.
        """
        return self.categories

    @property
    def language(self):
        """Get the language of the document.

        Returns:
            str|None: The language of the document.
        """
        if lid_results := self.lid:
            return lid_results.language
        else:
            if analysis_results := self.results(APP_ID_ANALYSIS):
                language = analysis_results.language
                if "@" in language:
                    return language.split("@")[0]
                return analysis_results.language
            else:
                return None

    @staticmethod
    def deserialize(document: dict):
        """Deserialize a document from JSON format.

        Args:
            document (dict): JSON representation of the document.

        Returns:
            AnalysisDocument: Document object.
        """

        return AnalysisDocument.from_dict(document)

    @property
    def entity_graph(self) -> list[Link]:
        """Get the entity graph of the document.

        Returns:
            list[Link]: The entity graph of the document.
        """
        if app_results := self.results("wowool_entity_graph"):
            return convert_entity_graph(app_results)
        else:
            return []
