import json
from wowool.annotation.entity import Entity
from wowool.annotation.sentence import Sentence
from wowool.annotation.token import Token, MorphData
from wowool.document.analysis.text_analysis import TextAnalysis
from wowool.error import Error
from enum import IntEnum


def _add_morphology(tkz, mdl, jo):
    for json_md in jo:
        md = MorphData()
        if len(json_md) > 0:
            md._lemma = json_md[0]
        if len(json_md) > 1:
            md._pos = json_md[1]
        pidx = 2
        while pidx < len(json_md):
            if isinstance(json_md[pidx], list):
                md.set_morphology([])
                _add_morphology(tkz, md.morphology, json_md[pidx])
            elif isinstance(json_md[pidx], str):
                tkz.properties.add(json_md[pidx])
            pidx += 1
        mdl.append(md)


class AnnotationType(IntEnum):
    SENTENCE = 1
    CONCEPT = 2
    TOKEN = 3


def _parse_sentence(json_sentence):
    sentence = Sentence(json_sentence[1], json_sentence[2])
    if len(json_sentence) > 4:
        sentence.attributes = json_sentence[4]

    sentence_annotation = None
    for annotation in json_sentence[3]:
        if annotation[0] == AnnotationType.TOKEN:  # Token
            token = Token(annotation[1], annotation[2], annotation[3])
            token._set_properties(set(annotation[4]))
            token._set_morphology([])
            _add_morphology(token, token.morphology, annotation[5])
            token._annotation_idx = len(sentence.annotations)
            sentence.annotations.append(token)
        elif annotation[0] == AnnotationType.CONCEPT:  # Entity
            if sentence_annotation is None and annotation[3] == "Sentence":
                # we do not want to create a new Entity for the sentence annotation in the API.
                sentence_annotation = annotation
                continue
            concept = Entity(annotation[1], annotation[2], annotation[3])
            concept.set_attributes(annotation[4] if len(annotation) > 4 else {})
            concept._set_sentence_annotations_index(sentence.annotations, len(sentence.annotations))
            sentence.annotations.append(concept)
        else:
            raise Error(f"Annotation type = {annotation} not supported.")
    return sentence


def parse_document(json_str_or_obj, doc_id=None, cpp_document=None):
    """
    Parse a json string into a TextAnalysis

    :param json_str: a json string returned from the server.
    :type json_str: string
    :returns: a TextAnalysis

    .. code-block:: python

        from wowool.document_parser import parse_document
        document = parse_document(json_str)
        for sentence in document:
            for annotation in sent.annotations:
                if annotation.is_token: pass
                if annotation.is_concept: pass

    :raises: ValueError, Exception
    """
    json_obj = json_str_or_obj if isinstance(json_str_or_obj, dict) else json.loads(json_str_or_obj)
    if "error" in json_obj:
        raise ValueError(json_obj["error"])
    if "exception" in json_obj:
        raise Exception(json_obj["exception"])
    jo_sentences = None

    wowool_out = json_obj
    if "document" in json_obj:
        if "sentences" in wowool_out["document"]:
            jo_sentences = wowool_out["document"]["sentences"]
        elif "sentences" in wowool_out:
            jo_sentences = wowool_out["sentences"]
    elif "sentences" in wowool_out:
        jo_sentences = wowool_out["sentences"]

    if jo_sentences is None:
        raise Exception("Invalid json format. Missing document object.")

    language = wowool_out["language"] if "language" in wowool_out else "english"
    if not doc_id:
        doc_id = wowool_out["id"] if "id" in wowool_out else id(json_str_or_obj)

    metadata = wowool_out["metadata"] if "metadata" in wowool_out else {}

    sentences = [_parse_sentence(json_sentence) for json_sentence in jo_sentences]
    return TextAnalysis(cpp_document, doc_id, language, sentences, json_str_or_obj, metadata)
