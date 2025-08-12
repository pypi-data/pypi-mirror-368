from wowool.document.document_interface import DocumentInterface
from wowool.document.factory import Factory, _resolve__pass_thru
from pathlib import Path
from wowool.document.defines import WJ_ID, WJ_DATA, WJ_MIME_TYPE, WJ_METADATA
from typing import Generator, Any, Callable


class Document(DocumentInterface):
    """DocumentInterface is an interface utility to handle data input.

    This class provides methods for creating, loading, and manipulating documents
    from various data sources including files, strings, and binary data.
    """

    def __init__(
        self,
        data: str | bytes,
        id: Path | str | None = None,
        mime_type: str = "",
        metadata: dict = {},
        encoding="utf8",
    ):
        """Initialize a Document instance.

        Args:
            data (str|bytes): The content of the document as string or bytes.
            id (Path|str| None): Unique document identifier or file path.
            mime_type (str): Document MIME type.
            metadata (dict): Additional metadata for the document.
            encoding (str): Character encoding of the given data.
        """
        self.input_provider = Factory.create(
            id=id,
            data=data,
            mime_type=mime_type,
            encoding=encoding,
            metadata=metadata,
        )
        self._metadata = metadata

    @property
    def id(self) -> str:
        """Get the unique document identifier.

        Returns:
            str: Unique document identifier.
        """
        return self.input_provider.id

    @property
    def mime_type(self) -> str:
        """Get the document MIME type.

        Returns:
            str: Document MIME type.
        """
        return self.input_provider.mime_type

    @property
    def encoding(self) -> str:
        """Get the document encoding.

        Returns:
            str: Document character encoding.
        """
        return self.input_provider.encoding

    @property
    def data(self) -> str | bytes:
        """Get the document content.

        Returns:
            str|bytes: Document content as string or bytes.
        """
        return self.input_provider.data

    @property
    def metadata(self) -> dict:
        """Get the document metadata.

        Returns:
            dict: Document metadata dictionary.
        """
        return self._metadata

    @staticmethod
    def deserialize(document: dict) -> DocumentInterface:
        """Deserialize a document from JSON format.

        Args:
            document (dict): JSON representation of the document.

        Returns:
            DocumentInterface: Document object.
        """
        from wowool.document.serialize import deserialize

        return deserialize(document)

    @staticmethod
    def from_json(
        document: dict,
    ) -> DocumentInterface:
        """Create a document from JSON representation.

        Args:
            document (dict): JSON dictionary containing document data.

        Returns:
            DocumentInterface: Document object created from JSON data.
        """
        return Factory.from_json(
            id=document[WJ_ID], data=document[WJ_DATA], provider_type=document[WJ_MIME_TYPE], metadata=document.get(WJ_METADATA, {})
        )

    @staticmethod
    def create(
        data: str | bytes | None = None,
        id: Path | str | None = None,
        mime_type: str = "",
        encoding="utf8",
        binary: bool = False,
        **kwargs,
    ) -> DocumentInterface:
        """Create a document from the given data.

        Args:
            data (str|bytes|None): Document content.
            id (Path|str|None): Unique document identifier.
            mime_type (str): Document MIME type.
            encoding (str): Document character encoding.
            binary (bool): If True, the data is treated as binary.
            kwargs: Additional keyword arguments.

        Returns:
            DocumentInterface: Document object.
        """
        return Factory.create(
            id=id,
            data=data,
            mime_type=mime_type,
            encoding=encoding,
            binary=binary,
            **kwargs,
        )

    @staticmethod
    def from_file(
        file: Path | str | None = None,
        data: str | bytes | None = None,
        mime_type: str = "",
        encoding="utf-8",
        **kwargs,
    ) -> DocumentInterface:
        """Create a document from the given file.

        Args:
            file (Path|str|None): Path to the file.
            data (str|bytes|None): Document content.
            mime_type (str): Document MIME type.
            encoding (str): Document character encoding.
            kwargs: Additional keyword arguments.

        Returns:
            DocumentInterface: Document object.

        Raises:
            ValueError: If the file is not found.
            TypeError: If the file is not a string or Path object.
            IOError: If there is an error reading the file.
        """
        return Factory.create(
            id=file,
            data=data,
            mime_type=mime_type,
            encoding=encoding,
            **kwargs,
        )

    @staticmethod
    def glob(
        folder: Path | str,
        pattern: str = "**/*.txt",
        mime_type: str = "",
        resolve: Callable[[str | Path], str] = _resolve__pass_thru,
        binary: bool = False,
        stop_on_error: bool = False,
        **kwargs,
    ) -> Generator[DocumentInterface, Any, None]:
        """Create documents from files matching a pattern in the given folder.

        This method will search for files matching the given pattern in the specified folder.

        Example:
            ```python
            from wowool.document import Document

            for doc in Document.glob("/path/to/folder/*.html"):
                print(doc.id, doc.text)
            ```
        Args:
            folder (Path|str): Path to the folder.
            pattern (str): Pattern to match files.
            mime_type (str): Document MIME type.
            resolve (Callable[[str|Path], str]): Function to resolve the data.
            binary (bool): If True, the data is treated as binary.
            stop_on_error (bool): If True, stop processing on first error.
            kwargs: Additional keyword arguments.

        Returns:
            Generator[DocumentInterface, Any, None]: Generator of Document objects.

        Raises:
            ValueError: If the folder is not found.
        """
        yield from Factory.glob(
            folder, pattern=pattern, mime_type=mime_type, resolve=resolve, binary=binary, stop_on_error=stop_on_error, **kwargs
        )
