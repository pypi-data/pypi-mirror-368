from wowool.document.document_interface import DocumentInterface, MT_PLAINTEXT


def generate_uuid(prefix: str = "") -> str:
    """
    Generate a unique identifier for the document.
    :return: A unique identifier.
    :rtype: ``str``
    """
    import uuid

    return f"{prefix}{uuid.uuid4().hex}"


class StrInputProvider(DocumentInterface):

    def __init__(self, text: str, id: str | None = None, metadata: dict | None = None):
        self._uid = id if id is not None else generate_uuid()
        self._text = text
        self._metadata = metadata if metadata is not None else {}

    @property
    def id(self) -> str:
        return self._uid

    @property
    def mime_type(self) -> str:
        return MT_PLAINTEXT

    @property
    def encoding(self) -> str:
        return "utf-8"

    @property
    def data(self) -> str:
        return self._text

    @property
    def metadata(self) -> dict:
        return self._metadata
