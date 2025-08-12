from wowool.document.document_interface import DocumentInterface, MT_PLAINTEXT
from striprtf.striprtf import rtf_to_text


class RTFFileInputProvider(DocumentInterface):

    MIME_TYPE = MT_PLAINTEXT

    def __init__(self, fid, metadata: dict | None = None, **kwargs):
        self._id = str(fid)
        self._data = None
        self._metadata = metadata if metadata is not None else {}

    @property
    def id(self) -> str:
        return self._id

    @property
    def mime_type(self) -> str:
        return MT_PLAINTEXT

    @property
    def encoding(self) -> str:
        return "utf-8"

    @property
    def data(self, **kwargs):
        if self._data is not None:
            return self._data

        with open(self.id, "r") as f:
            data = f.read()
            self._data = rtf_to_text(data, errors="ignore", encoding=self.encoding)
            return self._data

    @property
    def metadata(self) -> dict:
        return self._metadata
