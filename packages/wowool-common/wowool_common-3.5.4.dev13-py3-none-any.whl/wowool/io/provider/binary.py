from pathlib import Path
from wowool.document.document_interface import DocumentInterface


class BinaryFileInputProvider(DocumentInterface):

    def __init__(self, fid: str | Path, mime_type: str, data: bytes | None = None, metadata: dict | None = None):
        self._id = str(fid)
        self._mime_type = mime_type
        self._data = data
        self._metadata = metadata if metadata is not None else {}

    @property
    def id(self) -> str:
        """
        :return: Unique document identifier
        :rtype: ``str``
        """
        return self._id

    @property
    def mime_type(self) -> str:
        """
        :return: Document type
        :rtype: ``str``
        """
        return self._mime_type

    @property
    def encoding(self) -> str:
        """
        :return: Document encoding
        :rtype: ``str``
        """
        return "binary"

    @property
    def data(self, **kwargs) -> bytes:
        if self._data is not None:
            return self._data
        # Check if the file exists
        fn = Path(self.id)
        return fn.read_bytes()

    @property
    def metadata(self) -> dict:
        return self._metadata
