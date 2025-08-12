from pathlib import Path
from typing import Union, Optional
from wowool.document.document_interface import DocumentInterface
from wowool.utility.path import expand_path
from wowool.io.provider.encoding import get_data_encoding
from wowool.document.document_interface import MT_STRING
from wowool.document.analysis.text_analysis import AnalysisInputProvider

DEFAULT_TEXT_MIME_TYPE = "plain/text"
DEFAULT_ANALYSIS_DATA_TYPE = AnalysisInputProvider.MIME_TYPE


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
        raise RuntimeError(f"Data only supports str|bytes but was passed {type(data)}")


def _make_str(uid, data, encoding, **kwargs) -> DocumentInterface:
    from wowool.io.provider.str import StrInputProvider

    _txt = data2str(data, encoding)
    return StrInputProvider(_txt, id=str(uid), **kwargs)


def _make_text_file(uid, data, encoding, **kwargs) -> DocumentInterface:
    try:
        from wowool.io.provider.file import FileInputProvider

        return FileInputProvider(uid, encoding=encoding, **kwargs)
    except Exception as ex:
        raise ex


def _make_rtf(uid, data, encoding, **kwargs) -> DocumentInterface:
    from wowool.io.provider.rtf import RTFFileInputProvider

    _uid = str(uid) if isinstance(uid, Path) else uid
    return RTFFileInputProvider(_uid, encoding=encoding, **kwargs)


def _make_html(uid, data, encoding, **kwargs) -> DocumentInterface:
    try:
        from wowool.io.provider.html_v2 import HTMLFileInputProvider

        return HTMLFileInputProvider(uid, data, **kwargs)
    except Exception as ex:
        raise RuntimeError(f"install the BeautifulSoup(beautifulsoup4) library, 'pip install beautifulsoup4' {ex}")


def _make_docx(uid, data, **kwargs) -> DocumentInterface:
    assert data is None, "The docx reader does not support data, only files"
    try:
        from wowool.io.provider.docx import DocxFileInputProvider

        if "encoding" in kwargs:
            del kwargs["encoding"]
        return DocxFileInputProvider(uid, **kwargs)
    except ModuleNotFoundError as ex:
        raise ModuleNotFoundError(f"install the python-docx library, 'pip install python-docx' {ex}")


def _make_file(uid, data, encoding: str | None = None, metadata: dict | None = None, **kwargs) -> DocumentInterface:
    from wowool.io.provider.file import FileInputProvider

    options = {}
    if "cleanup" in kwargs:
        options["cleanup"] = kwargs["cleanup"]
    return FileInputProvider(fid=uid, encoding=encoding, metadata=metadata, **options)


def _make_pdf(uid, data, **kwargs) -> DocumentInterface:
    assert data is None, "The pdf reader does not support data, only files"
    try:
        from wowool.io.pdf.provider import PDFFileInputProvider

        return PDFFileInputProvider(uid, **kwargs)

    except ModuleNotFoundError as ex:
        raise ModuleNotFoundError(f"install the pdfminer.six library, 'pip install pdfminer.six' {ex}")


def _invalid_type(uid, data, **kwargs):
    raise RuntimeError("Invalid type")


creators = {
    DEFAULT_TEXT_MIME_TYPE: _make_str,
    "txt": _make_file,
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
    "md": _make_file,
    "md/utf8": _make_file,
    "html/utf8": _make_html,
    "pdf/utf8": _make_pdf,
    "docx/utf8": _make_docx,
    "_invalid_type": _invalid_type,
}


class Factory:
    @staticmethod
    def create(
        data: Optional[Union[str, bytes]] = None,
        id: Optional[str] = None,
        provider_type: str = "",
        encoding="utf8",
        **kwargs,
    ) -> DocumentInterface:
        """
        Class to create a document from input data or from file.

        .. code-block :: python

            fn = "test.html"
            doc = Factory.create(fn)

        .. code-block :: python

            fn = "test.html"
            with open(fn) as fh:
                html_data = fh.read()
                doc = Factory.create(id = fn, data = html_data, provider_type = "html")
        """
        _data = data
        if id is not None and _data is None:
            try:
                fn = Path(id)
            except Exception:
                fn = None
            #  this should be done in the provider itself
            # if fn.exists():
            #     with open(fn, "rb") as fh:
            #         bdata = fh.read()
            #         _data = bdata.decode(encoding)
            if fn is None:
                provider_type = "text"
            if not provider_type:
                if fn.exists():
                    provider_type = fn.suffix[1:] if fn.suffix.startswith(".") else "txt"
                else:
                    provider_type = "text"
        else:
            if data is not None:
                if id is not None:

                    fn = Path(id)
                    if not provider_type:
                        if fn.exists():
                            provider_type = fn.suffix[1:] if fn.suffix.startswith(".") else "txt"

        if not provider_type:
            provider_type = "txt" if _data is None else "text"
        if provider := creators.get(provider_type):
            return provider(id, _data, encoding=encoding, **kwargs)
        else:
            raise RuntimeError(f"Unknown provider type: {provider_type}")

    @staticmethod
    def split_path_on_wildcards(path_description: Path, pattern: str = "*.txt"):
        """
        Split a path description into a folder and a wildcard pattern.
        """
        parts = path_description.parts

        for index, part in enumerate(parts):
            if "*" in part or "?" in part:
                return Path(*parts[:index]), str(Path(*parts[index:]))

        return path_description, pattern

    @staticmethod
    def glob(folder: Path | str, pattern: str = "*.txt", provider_type: str = "", **kwargs):
        folder = expand_path(folder)
        if Path(folder).is_file():
            fn = Path(folder)
            if fn.exists():
                yield Factory.create(id=folder, provider_type=provider_type, **kwargs)
            else:
                raise RuntimeError(f"File {folder} does not exist")
        else:
            folder, pattern_ = Factory.split_path_on_wildcards(folder, pattern=pattern)
            for fn in folder.glob(pattern_):
                yield Factory.create(id=fn, provider_type=provider_type, **kwargs)
