from pathlib import Path
from typing import Any, Generator, Union, Optional
from wowool.document.document_interface import DocumentInterface, MT_ANALYSIS_JSON, MT_STRING
from os import pathconf
from wowool.utility.path import expand_path
from wowool.document.analysis.text_analysis import AnalysisInputProvider
from wowool.utility.mime_type.mime_type import get_mime_type, get_mime_type_from_file_extension
from wowool.io.provider.encoding import get_data_encoding
from logging import getLogger

logger = getLogger(__name__)
PC_NAME_MAX = pathconf("/", "PC_NAME_MAX")
DEFAULT_TEXT_MIME_TYPE = "plain/text"
DEFAULT_ANALYSIS_DATA_TYPE = AnalysisInputProvider.MIME_TYPE


def _resolve__pass_thru(id: str | Path) -> str:
    return str(id)


def data2str(data: Union[str, bytes, None], encoding="utf-8") -> str:
    if isinstance(data, str):
        return data
    elif isinstance(data, bytes):
        if encoding and encoding == "auto" or encoding == "binary":
            encoding = get_data_encoding(data)

        return data.decode(encoding)
    elif data is None:
        return ""
    else:
        raise RuntimeError(f"data only supports str|bytes, not {type(data)} {data}")


def _make_str(uid, data, encoding, metadata: dict | None = None, **kwargs) -> DocumentInterface:
    from wowool.io.provider.str import StrInputProvider

    _txt: str = data2str(data, encoding)
    _uid = str(uid) if isinstance(uid, Path) else uid
    return StrInputProvider(_txt, id=_uid, metadata=metadata, **kwargs)


def _make_file(uid, data, encoding: str | None = None, metadata: dict | None = None, **kwargs) -> DocumentInterface:
    from wowool.io.provider.file import FileInputProvider

    options = {}
    if "cleanup" in kwargs:
        options["cleanup"] = kwargs["cleanup"]
    return FileInputProvider(fid=uid, encoding=encoding, metadata=metadata, **options)


def _make_html(uid, data, encoding, metadata: dict | None = None, **kwargs) -> DocumentInterface:
    try:
        from wowool.io.provider.html_v2 import HTMLFileInputProvider

        return HTMLFileInputProvider(uid, data, metadata=metadata, **kwargs)
    except Exception as ex:
        raise RuntimeError(f"install the BeautifulSoup(beautifulsoup4) library, 'pip install beautifulsoup4' {ex}")


def _make_docx(uid, data, metadata: dict | None = None, **kwargs) -> DocumentInterface:
    assert data is None, "The docx reader does not support data, only files"
    try:
        from wowool.io.provider.docx import DocxFileInputProvider

        return DocxFileInputProvider(uid, metadata=metadata, **kwargs)
    except ModuleNotFoundError as ex:
        raise ModuleNotFoundError(f"install the python-docx library, 'pip install python-docx' {ex}")


def _make_pdf(uid, data, metadata: dict | None = None, **kwargs) -> DocumentInterface:
    # assert data is None, "The pdf reader does not support data, only files"
    try:
        from wowool.io.pdf.provider import PDFFileInputProvider

        return PDFFileInputProvider(uid, metadata=metadata, input_bytes=data, **kwargs)

    except ModuleNotFoundError as ex:
        raise ModuleNotFoundError(f"install the pdfminer.six library, 'pip install pdfminer.six' {ex}")


def _make_rtf(uid, data, metadata: dict | None = None, **kwargs) -> DocumentInterface:
    assert data is None, "The pdf reader does not support data, only files"
    try:
        from wowool.io.provider.rtf import RTFFileInputProvider

        return RTFFileInputProvider(uid, metadata=metadata, **kwargs)

    except ModuleNotFoundError as ex:
        raise ModuleNotFoundError(f"install the striprtf library, 'pip install striprtf' {ex}")


def _make_analysis_document(uid, data, metadata: dict | None = None, **kwargs) -> DocumentInterface:
    return AnalysisInputProvider(data=data, id=uid, metadata=metadata)


def _invalid_type(uid, data, metadata: dict | None = None, **kwargs) -> DocumentInterface:
    raise RuntimeError("Invalid type")


creators = {
    DEFAULT_TEXT_MIME_TYPE: _make_str,
    "txt": _make_str,
    MT_STRING: _make_str,
    "utf8": _make_str,
    "text": _make_str,
    "file": _make_file,
    "text/plain": _make_file,
    "text/html": _make_html,
    "pdf": _make_pdf,
    "docx": _make_docx,
    "text/rtf": _make_rtf,
    "text/csv": _make_file,
    "application/pdf": _make_pdf,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": _make_docx,
    "file/utf8": _make_file,
    "md/utf8": _make_file,
    "html/utf8": _make_html,
    "pdf/utf8": _make_pdf,
    "docx/utf8": _make_docx,
    DEFAULT_ANALYSIS_DATA_TYPE: _make_analysis_document,
    "_invalid_type": _invalid_type,
}


binary_content_types = set(["pdf", "docx"])


def generate_uuid(prefix: str = "") -> str:
    """
    Generate a unique identifier for the document.
    :return: A unique identifier.
    :rtype: ``str``
    """
    import uuid

    return f"{prefix}{uuid.uuid4().hex}"


class Factory:

    @staticmethod
    def from_json(id: str, data: Any, provider_type: str, metadata: dict | None = None) -> DocumentInterface:
        """
        Deserialize a document from JSON format.
        :param document: JSON representation of the document.
        :return: Document object.
        :rtype: ``Document``
        """
        return creators.get(provider_type, _invalid_type)(id, data, metadata=metadata)

    @staticmethod
    def create_raw(
        file: str | Path, data: bytes | None, mime_type: str | None = None, metadata: dict | None = None, **kwargs
    ) -> DocumentInterface:
        """
        Create a raw file input provider.
        :param file: The file name or path.
        :param data: The data to be read from the file.
        :param mime_type: The type of the provider.
        """
        from wowool.io.provider.binary import BinaryFileInputProvider

        file = Path(file)
        if not mime_type:
            import magic

            if data is not None:
                mime_type_ = magic.from_buffer(data, mime=True)
            else:
                mime_type_ = magic.from_file(file, mime=True)
        else:
            mime_type_ = mime_type
        return BinaryFileInputProvider(file, mime_type=mime_type_, data=data, metadata=metadata, **kwargs)

    @staticmethod
    def create(
        id: Path | str | None = None,
        data: Optional[Union[str, bytes]] = None,
        mime_type: str = "",
        encoding="utf8",
        binary: bool = False,
        metadata: dict | None = None,
        **kwargs,
    ) -> DocumentInterface:
        """
        Create a document object based on the given parameters.
        :param id: The unique identifier for the document.
        :param data: The data to be read from the file.
        :param provider_type: The type of the provider.
        :param encoding: The encoding to be used for the data.
        :param binary: If True, create a binary file input provider.
        :param kwargs: Additional keyword arguments.
        :return: A document object.
        :rtype: ``Document``
        """

        mime_type_ = get_mime_type(mime_type=mime_type, data=data, file=id)

        if binary:
            assert id is not None, "binary=True requires an id"

            return Factory.create_raw(file=id, data=data, mime_type=mime_type_, metadata=metadata, **kwargs)

        _data = data
        if id is not None and _data is None and mime_type_ is None:
            if get_mime_type_from_file_extension(id) == None:
                raise ValueError(f"Could not determine mime type for {id}, please provide data or a valid file")
            fn = Path(id)
            try:
                if not fn.exists():
                    _data = None

            except Exception:
                _data = None
        else:
            if data is not None:
                # dispatch to the string input provider
                mime_type_ = MT_STRING if mime_type_ == "text/plain" else mime_type_
                if id is None:
                    id = generate_uuid()
                else:
                    # assume the id is a file name
                    fn = Path(id)
        return creators.get(mime_type_, _invalid_type)(id, _data, encoding=encoding, metadata=metadata, **kwargs)

    @staticmethod
    def split_path_on_wildcards(path_description: Path, pattern: str = "**/*.txt"):
        """
        Split a path description into a folder and a wildcard pattern.
        """
        parts = path_description.parts

        for index, part in enumerate(parts):
            if "*" in part or "?" in part:
                return Path(*parts[:index]), str(Path(*parts[index:]))

        if not path_description.exists():
            raise ValueError(f"Path {path_description} does not exist")
        return path_description, pattern

    @staticmethod
    def glob(
        folder: Path | str,
        pattern: str = "**/*.txt",
        mime_type: str = "",
        resolve=_resolve__pass_thru,
        binary: bool = False,
        metadata: dict | None = None,
        stop_on_error: bool = False,
        **kwargs,
    ) -> Generator[DocumentInterface, Any, None]:
        """
        Create a generator that yields document objects based on the files found in the specified folder and pattern.
        :param folder: The folder to search for files.
        :param pattern: The pattern to match files.
        :param mime_type: The type of the provider.
        :param resolve: A function to resolve the file name.
        :param binary: If True, create a binary file input provider.
        :param kwargs: Additional keyword arguments.
        :return: A generator that yields document objects.
        :rtype: ``Generator``
        """
        folder = expand_path(folder)
        if folder.is_file():
            try:
                fn = Path(folder)
                if fn.exists():
                    yield Factory.create(id=resolve(folder), mime_type=mime_type, binary=binary, metadata=metadata, **kwargs)
                    return
                else:
                    raise ValueError(f"File {folder} does not exist")
            except Exception as ex:
                if stop_on_error:
                    raise RuntimeError(f"Could not create document object, {ex}: {folder}")
                else:
                    logger.warning(f"{ex}: {folder}")
        folder, pattern_ = Factory.split_path_on_wildcards(folder, pattern=pattern)
        for fn in folder.glob(pattern_):
            try:
                if fn.is_file():
                    yield Factory.create(id=resolve(fn), mime_type=mime_type, binary=binary, metadata=metadata, **kwargs)
            except Exception as ex:
                if stop_on_error:
                    raise RuntimeError(f"Could not create document object, {ex}: {folder}")
                else:
                    logger.warning(f"{ex}: {folder}")
