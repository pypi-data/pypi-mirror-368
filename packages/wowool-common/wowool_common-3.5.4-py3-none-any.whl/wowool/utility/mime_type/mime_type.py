from pathlib import Path

# note: we only import the magic library if we need it otherwise we force the user to install it

MIME_TYPES = {
    "html": "text/html",
    "htm": "text/html",
    "txt": "text/plain",
    "md": "text/plain",
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "doc": "application/msword",
    "rtf": "text/rtf",
    "csv": "text/csv",
}


def get_mime_type_from_file_extension(file: str | Path) -> str | None:
    # Ensure file is a string
    if not isinstance(file, str):
        file = str(file)

    parts = file.split(".")
    if len(parts) > 1:
        return MIME_TYPES.get(parts[-1], None)


def get_mime_type_from_file(file: str | Path) -> str | None:
    # Ensure file is a string
    if not isinstance(file, str):
        file = str(file)

    parts = file.split(".")
    if len(parts) > 1:
        return MIME_TYPES.get(parts[-1], None)
    return "text/plain"


def get_mime_type(file: Path, data=None, mime_type: str | None = None) -> str:
    """
    Get the mime type of a file
    :param file: File path
    :return: Mime type
    """

    mime_type_ = MIME_TYPES.get(mime_type, mime_type) if mime_type else None
    if not mime_type_:
        if file:
            mime_type_from_fn = get_mime_type_from_file(str(file))
            if mime_type_from_fn is not None:
                mime_type_ = mime_type_from_fn
            else:
                if data is not None:
                    import magic

                    mime_type_ = magic.from_buffer(data, mime=True)
                else:
                    if not Path(file).exists():
                        mime_type_from_fn = get_mime_type_from_file(str(file))
                        if mime_type_from_fn is not None:
                            mime_type_ = mime_type_from_fn
                        else:
                            mime_type_ = "text/plain"
                    else:
                        import magic

                        mime_type_ = magic.from_file(file, mime=True)

            # mime_type_ = magic.from_file(file, mime=True)
        else:
            mime_type_from_fn = get_mime_type_from_file(str(file))
            if mime_type_from_fn:
                mime_type_ = mime_type_from_fn
            else:
                mime_type_ = mime_type

    return mime_type_ if mime_type_ else "plain/text"
