"""Language Identification API classes"""

from dataclasses import dataclass, field


@dataclass
class LanguageIdentifierSectionResult:
    """Language identification results for a specific section of text.

    Represents the detected language for a particular section or segment
    of a document, including the text boundaries and content.

    Attributes:
        language (str): The identified language code (e.g., 'en', 'fr', 'es').
        begin_offset (int): Starting character position of the section.
        end_offset (int): Ending character position of the section.
        text (str|None): The actual text content of the section, if available.
            Defaults to None.
    """

    language: str
    begin_offset: int
    end_offset: int
    text: str | None = None


@dataclass
class LanguageIdentifierResults:
    """Complete language identification results for a document.

    Contains the overall language identification results, including the primary
    language and detailed section-by-section analysis for multi-language documents.

    Attributes:
        language (str): The primary identified language code. If multiple languages
            are detected, this will be "multiple". Defaults to empty string.
        sections (list[LanguageIdentifierSectionResult]): List of section-specific
            language identification results. Defaults to empty list.
    """

    language: str = ""
    sections: list[LanguageIdentifierSectionResult] = field(default_factory=list)


def convert_lid(jo_data: dict) -> LanguageIdentifierResults:
    retval = LanguageIdentifierResults()
    if "sections" in jo_data:
        sections = []
        languages = set()
        for section in jo_data["sections"]:
            section_result = LanguageIdentifierSectionResult(
                language=section["language"],
                begin_offset=section["begin_offset"],
                end_offset=section["end_offset"],
                text=section.get("text"),
            )
            languages.add(section_result.language)
            sections.append(section_result)
        retval.sections = sections
        if len(languages) == 1:
            retval.language = languages.pop()
        else:
            retval.language = "multiple"
    elif "language" in jo_data:
        retval.language = jo_data["language"]
    else:
        raise ValueError("Invalid JSON data for language identification.")
    return retval
