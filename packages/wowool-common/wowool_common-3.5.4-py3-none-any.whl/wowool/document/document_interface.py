from typing import Protocol, runtime_checkable, Any

MT_PLAINTEXT = "text/plain"
MT_ANALYSIS_JSON = "application/vnd.wowool.document-analysis+json"
MT_STRING = "application/vnd.wowool.string"


@runtime_checkable
class DocumentInterface(Protocol):
    """Protocol interface for handling document data input.

    This protocol defines the standard interface that document implementations
    must follow to provide consistent access to document properties including
    identification, content type, encoding, data, and metadata.
    """

    @property
    def id(self) -> str:
        """Get the unique identifier for the document.

        Returns:
            str: A unique identifier string for the document.
        """
        ...

    @property
    def mime_type(self) -> str:
        """Get the MIME type of the document.

        Returns:
            str: The MIME type string indicating the document's content type
                (e.g., 'text/plain', 'application/json').
        """
        ...

    @property
    def encoding(self) -> str:
        """Get the character encoding of the document.

        Returns:
            str: The character encoding string (e.g., 'utf-8', 'ascii').
        """
        ...

    @property
    def data(self) -> Any:
        """Get the actual document data content.

        Returns:
            Any: The document data in its native format. The type depends
                on the specific document implementation and MIME type.
        """
        ...

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the document metadata.

        Returns:
            dict[str,Any]: A dictionary containing document metadata
                with string keys and values of any type.
        """
        ...
