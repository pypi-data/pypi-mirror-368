from wowool.document.document_interface import DocumentInterface
from wowool.document.factory import Factory
from wowool.document.defines import WJ_ID, WJ_DATA, WJ_MIME_TYPE, WJ_METADATA, WJ_ENCODING
import base64


def needs_base64_encoding(encoding: str) -> bool:
    """
    Check if the encoding requires base64 encoding.

    :param encoding: The encoding type.
    :return: True if base64 encoding is needed, False otherwise.
    """
    return encoding not in ["utf-8"]


def serialize_dict(document: dict) -> dict:
    if needs_base64_encoding(document["encoding"]):
        data = base64.b64encode(document["data"]).decode("ascii")
        return {
            WJ_ID: document["id"],
            WJ_DATA: data,
            WJ_MIME_TYPE: document["mime_type"],
            WJ_ENCODING: document["encoding"],
            WJ_METADATA: document.get("metadata", {}),
        }
    else:
        return {
            WJ_ID: document["id"],
            WJ_DATA: document["data"],
            WJ_MIME_TYPE: document["mime_type"],
            WJ_ENCODING: document["encoding"],
            WJ_METADATA: document.get("metadata", {}),
        }


def serialize_document_interface(document: DocumentInterface) -> dict:

    if needs_base64_encoding(document.encoding):
        data = base64.b64encode(document.data).decode("ascii")
        return {
            WJ_ID: document.id,
            WJ_DATA: data,
            WJ_MIME_TYPE: document.mime_type,
            WJ_ENCODING: document.encoding,
            WJ_METADATA: document.metadata,
        }
    else:
        return {
            WJ_ID: document.id,
            WJ_DATA: document.data,
            WJ_MIME_TYPE: document.mime_type,
            WJ_ENCODING: document.encoding,
            WJ_METADATA: document.metadata,
        }


def serialize(document: DocumentInterface | dict) -> dict:
    if isinstance(document, dict):
        return serialize_dict(document)
    return serialize_document_interface(document)


def deserialize(document: dict) -> DocumentInterface:
    encoding = document[WJ_ENCODING]
    if needs_base64_encoding(encoding):
        data = base64.b64decode(document[WJ_DATA])
        return Factory.create(
            id=document[WJ_ID],
            data=data,
            mime_type=document[WJ_MIME_TYPE],
            encoding=encoding,
            metadata=document.get(WJ_METADATA, {}),
        )
    else:
        return Factory.create(
            id=document[WJ_ID],
            data=document[WJ_DATA],
            mime_type=document[WJ_MIME_TYPE],
            metadata=document.get(WJ_METADATA, {}),
            encoding=encoding,
        )
