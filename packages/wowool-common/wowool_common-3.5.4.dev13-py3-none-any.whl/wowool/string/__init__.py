import re
from wowool.document.analysis.document import AnalysisDocument
from typing import cast

_URI_WORDS = re.compile(r"\w+")


def normalize(text: str):
    """Remove accents from characters in a given string.

    Args:
        text (str): The string to normalize.

    Returns:
        str: The normalized string with accented characters removed.
    """
    try:
        import unidecode

        return unidecode.unidecode(text)
    except ModuleNotFoundError:
        return text


def to_text(annotations: list) -> str:
    """Convert a list of annotations into a string.

    This function will also normalize the whitespace between the tokens.

    Args:
        annotations (list): List of annotation objects to convert to text.

    Returns:
        str: The converted text string.
    """
    prev_end_offset = None
    text = ""
    for a in annotations:
        if a.is_token:
            if prev_end_offset:
                if prev_end_offset != a.begin_offset:
                    text += " "

            text += a.literal
            prev_end_offset = a.end_offset
        elif a.is_sentence:
            if len(text) > 0:
                text += " "
            text += to_text(a.annotations)
    return text


def _camelize(name, separator=""):
    """Capitalize the first letter of every part of a multiword.

    Remove spaces and replace with the separator.

    Args:
        name (str): The name to camelize.
        separator (str): The separator to use between words.

    Returns:
        str: The camelized string.
    """
    parts = _URI_WORDS.findall(name)
    for idx in range(len(parts)):
        parts[idx] = parts[idx].capitalize()
    return separator.join(parts).strip()


def camelize(name: str, separator: str = ""):
    """Camelize a string after removing accents if any.

    Args:
        name (str): The name to camelize.
        separator (str): The separator to use between words.

    Returns:
        str: The camelized string with accents removed.
    """
    return _camelize(normalize(name), separator)


def initial_caps(name):
    """Capitalize the first letter of every part of a multiword.

    Args:
        name (str): The name to capitalize.

    Returns:
        str: The string with initial capitals and spaces preserved.
    """
    return camelize(name, separator=" ")


def to_uri(name: str, separator="") -> str:
    """Convert a name to URI format by camelizing and removing spaces.

    Args:
        name (str): The name to convert to URI format.
        separator (str): The separator to use between words.

    Returns:
        str: The URI-formatted string.
    """
    return camelize(name, separator)


GUESSER_PROPERTIES = {"cleanup", "guess", "typo"}


def canonicalize(obj, lemmas: bool = False, dates=True, spelling=True) -> str:
    """Replace the literal or the lemmas by their canonical form. The obj can be a `Sentence` or an `Entity`.

    Args:
        obj (Sentence|Entity): The annotation to be converted (Sentence or Entity).
        lemmas (bool): Replace using the lemma or the literal.
        dates (bool): Whether to canonicalize dates.
        spelling (bool): Whether to use canonical spelling corrections.

    Returns:
        str: The canonicalized string.

    Raises:
        RuntimeError: If obj type cannot be canonicalized.
    """
    from io import StringIO
    from wowool.annotation import Sentence, Entity, Token

    if isinstance(obj, Sentence):
        annotations_range = obj.annotations
    elif isinstance(obj, Entity):
        concept = obj
        annotations_range = concept.annotations
    else:
        raise RuntimeError("obj type can not be wowool.utility.canonicalize")

    with StringIO() as output:
        skip_until_offset = 0
        annotation_count = len(annotations_range)
        prev_token = None
        annotation_idx = 0
        while annotation_idx < annotation_count:
            annotation = annotations_range[annotation_idx]
            if annotation.begin_offset < skip_until_offset:
                prev_token = annotation
                annotation_idx += 1
                continue
            else:
                skip_until_offset = 0

            if annotation.is_token:
                token = cast(Token, annotation)
                # print(f"T:[{annotation.begin_offset},{annotation.end_offset}]:{annotation.literal} prev:{prev_token}")
                if prev_token:
                    # print(f"  -- pe:{prev_token.end_offset} != ab:{annotation.begin_offset}")
                    if prev_token.end_offset != annotation.begin_offset:
                        output.write(" ")
                if lemmas:
                    output.write(token.lemma)
                    if "rewrite" in token.properties:
                        next_token = Token.next(annotations_range, token)
                        if next_token and next_token.literal == "-":
                            annotation_idx += 1
                elif spelling and bool(GUESSER_PROPERTIES.intersection(token.properties)):
                    output.write(token.lemma)
                elif "rewrite" in token.properties:
                    output.write(token.lemma)
                    next_token = Token.next(annotations_range, token)
                    if next_token and next_token.literal == "-":
                        annotation_idx += 1

                else:
                    output.write(token.literal)

                prev_token = token

            elif annotation.is_concept:
                concept = cast(Entity, annotation)
                if "canonical" in concept.attributes:
                    if prev_token:
                        if prev_token.end_offset != concept.begin_offset:
                            output.write(" ")
                    output.write((concept.attributes["canonical"][0]))
                    skip_until_offset = concept.end_offset
                elif dates and concept.uri == "Date" and "abs_date" in concept.attributes:
                    if prev_token:
                        if prev_token.end_offset != concept.begin_offset:
                            output.write(" ")
                    output.write((concept.attributes["abs_date"][0]))
                    skip_until_offset = concept.end_offset
            annotation_idx += 1

        return output.getvalue()


def search_and_replace(document: AnalysisDocument, expression: str, replacestring: str) -> str:
    """Search for entities with a given URI and replace them with a given string.

    Args:
        document (AnalysisDocument): The document to search in.
        expression (str): The URI pattern to search for.
        replacestring (str): The string to replace matching entities with.

    Returns:
        str: The document text with replacements made.
    """
    from io import StringIO
    from wowool.annotation import Entity

    with StringIO() as strm:
        assert isinstance(document.text, str), "document.text should be a string"
        dtext = document.text
        offset_ = 0
        for concept in Entity.iter(document, lambda c: c.uri == expression):
            strm.write(dtext[offset_ : concept.begin_offset])  # noqa: E203
            strm.write(replacestring)
            offset_ = concept.end_offset

        strm.write(dtext[offset_:])
        return strm.getvalue()
