filemagic = None


def get_file_encoding(fn: str):
    global filemagic
    if filemagic is None:
        try:
            import magic

            filemagic = magic.Magic(mime_encoding=True)
        except ImportError:
            raise ImportError("Please install magic-mime_types to use auto encoding detection")

    return filemagic.from_file(fn)


def get_data_encoding(buffer: bytes):
    global filemagic
    if filemagic is None:
        try:
            import magic

            filemagic = magic.Magic(mime_encoding=True)
        except ImportError:
            raise ImportError("Please install magic-mime_types to use auto encoding detection")

    return filemagic.from_buffer(buffer)
