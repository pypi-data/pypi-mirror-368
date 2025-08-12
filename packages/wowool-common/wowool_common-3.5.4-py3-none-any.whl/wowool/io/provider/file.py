from pathlib import Path
from wowool.document.document_interface import DocumentInterface, MT_PLAINTEXT
import errno
from wowool.io.provider.encoding import get_file_encoding


def _strip_upper_ascii(s):
    assert isinstance(s, bytes)
    return bytes([i for i in s if 31 < i < 127 or i == 0xD or i == 0xA]).decode("utf8")


class FileInputProvider(DocumentInterface):
    MIME_TYPE = MT_PLAINTEXT

    def __init__(self, fid, encoding: str | None = "utf-8", cleanup=None, metadata: dict | None = None):
        self._id = str(fid)
        self.encoding_ = encoding
        self.cleanup = cleanup
        self._metadata = metadata if metadata is not None else {}
        self.encoding_ = encoding

    def cache_it(self, s):
        if self.cache_fn and self.encoding_ != "utf-8":
            with open(self.cache_fn, "w") as fh:
                fh.write(s)
        return s

    @property
    def id(self) -> str:
        """
        :return: Unique document identifier
        :rtype: ``str``
        """
        return self._id

    @property
    def mime_type(self) -> str:
        return MT_PLAINTEXT

    @property
    def encoding(self) -> str:
        return "utf-8"

    @property
    def input_encoding(self):
        if self.encoding_ == "auto" or self.encoding_ == "binary":
            self.encoding_ = get_file_encoding(self.id)
        else:
            return self.encoding_

    @property
    def data(self, **kwargs):
        fn = Path(self.id)
        self.cache_fn = Path(fn.parent, ".utf8_cache_" + fn.name)

        try:
            Path(self.cache_fn).exists()
        except OSError as exc:

            if exc.errno == errno.ENAMETOOLONG:
                self.cache_fn = None

        if self.cache_fn and self.cache_fn.exists():
            with open(self.cache_fn, mode="r", encoding="utf8") as f:
                return f.read()

        self.encoding_ = kwargs.get("encoding", self.encoding_)
        if self.encoding_ == "auto" or self.encoding_ == "binary":
            self.encoding_ = get_file_encoding(str(fn))
            if self.encoding_ == "binary":
                if self.cleanup is None:
                    raise RuntimeError(f"Warning: Cannot process binary file: {self.id}")
        try:
            if self.encoding_ == "unknown-8bit":
                print(f"Warning: unknown encoding using ascii : {self.id}")
                with open(self.id, "rb") as f:
                    r = f.read()
                    if self.cleanup:
                        return self.cache_it(self.cleanup(r))
                    else:
                        return self.cache_it(_strip_upper_ascii(r))

            assert isinstance(self.encoding_, str)
            with open(str(self.id), mode="r", encoding=self.encoding_) as f:
                r = f.read()
                if self.cleanup:
                    return self.cache_it(self.cleanup(r))
                else:
                    return r
        except Exception as ex:
            if self.cleanup:
                with open(self.id, "rb") as f:
                    r = f.read()
                    return self.cache_it(self.cleanup(r))
            else:
                raise ex

    @property
    def metadata(self) -> dict:
        return self._metadata
