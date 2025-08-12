from typing import Optional, Union
from pathlib import Path
from wowool.utility.path import expand_path
from wowool.document import Document


def default_cleanup(text: str) -> str:
    """Default cleanup function for the CLI.

    Args:
        text: Text to be cleaned up.

    Returns:
        Cleaned text with only printable ASCII characters and line endings.
    """
    return "".join(i for i in text if 31 < ord(i) < 127 or ord(i) == 0xD or ord(i) == 0xA)


def return_generator(docs):  # -> Generator[Any, Any, None]:
    """Return a generator for the given documents."""
    if isinstance(docs, list):
        for doc in docs:
            yield doc
    else:
        yield docs


def make_document_collection(
    text: Optional[Union[list, str]] = None,
    file: Optional[Union[Path, str]] = None,
    cleanup: Optional[bool] = None,
    encoding: str = "utf-8",
    pattern: str = "**/*.txt",
    **kwargs,
):
    """Create a document collection from text or file input.

    Args:
        text: Text content as string or list of strings.
        file: File path to process.
        cleanup: Whether to apply text cleanup.
        encoding: Text encoding to use.
        pattern: File pattern for globbing.
        **kwargs: Additional keyword arguments.

    Returns:
        List of Document objects or None.
    """
    stripped = None
    if cleanup:
        stripped = default_cleanup

    if file:
        options = {}
        options["encoding"] = encoding
        if cleanup:
            options["cleanup"] = stripped
        fn = expand_path(file)

        return Document.glob(fn, stripped=stripped)
    if text:
        doc_collection = []
        if isinstance(text, str):
            doc_collection.append(Document.create(text))
        elif isinstance(text, list):
            for text_ in text:
                doc_collection.append(Document.create(text_))

        return return_generator(doc_collection)
    raise RuntimeError("You must provide either text or file input to create a document collection.")
    # return Document.glob(folder, pattern, stripped=stripped, **kwargs)
