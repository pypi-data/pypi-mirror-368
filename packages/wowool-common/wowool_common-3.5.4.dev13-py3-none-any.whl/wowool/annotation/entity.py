from __future__ import annotations
from wowool.annotation.annotation import Annotation
from wowool.annotation.token import Token
from typing import Callable, Union, List, cast, Generator, Iterator, Self, Protocol
from wowool.annotation.annotation_list import AnnotationList


def _align(idx, collection) -> int:
    bo = collection[idx].begin_offset
    eo = collection[idx].end_offset
    rvidx = idx - 1
    while rvidx >= 0:
        if bo == collection[rvidx].begin_offset and eo == collection[rvidx].end_offset:
            rvidx -= 1
        else:
            return rvidx + 1
    return idx


def _filter_pass_thru(concept) -> bool:
    return True


class Entity(Annotation):
    """Class that contains all the information about a entity."""

    FilterType = Callable[[Self], bool]

    def __init__(self, begin_offset: int, end_offset: int, uri: str):
        """Initialize an Entity instance.

        Args:
            begin_offset (int): Begin offset of the concept.
            end_offset (int): End offset of the concept.
            uri (str): URI or name of the concept.
        """
        self._attributes = {}
        super(Entity, self).__init__(begin_offset, end_offset)
        self._uri = uri
        self._sentence_annotations = None
        self._annotations = None
        self._literals = None
        self._lemmas = None
        self._tokens = None
        self._dict = None
        self._canonical = None
        self._text = None

    @property
    def uri(self) -> str:
        """The URI or type of the entity.

        Returns:
            str: The URI or type of the entity (ex: Person or Company).
        """
        return self._uri

    @property
    def literal(self) -> str:
        """The literal or text representation of the entity. Same as the text property

        Returns:
            str: The text representation of the entity (ex: John Smith).
        """
        return self.text

    @property
    def literals(self) -> List[str]:
        """The token literals of the entity."""
        if not self._literals:
            self._literals = [token.literal for token in self.tokens]
        return self._literals

    @property
    def lemma(self) -> str:
        """Get the lemmatized form of the entity.

        Returns:
            str: The lemmatized form of the entity's text.
        """
        return " ".join(self.lemmas)

    @property
    def lemmas(self) -> List[str]:
        """The lemmas of the concept."""
        if not self._lemmas:
            self._lemmas = [token.lemma for token in self.tokens]
        return self._lemmas

    @property
    def stem(self) -> str:
        """Get the stem form of the entity.

        This property returns the same value as the lemma property, providing
        an alias for accessing the lemmatized form of the entity's text.

        Returns:
            str: The stem/lemma representation of the entity.
        """
        return self.lemma

    def has_canonical(self) -> bool:
        if "canonical" in self._attributes:
            return True
        elif "icanonical" in self._attributes:
            return True
        return False

    def _get_canonical(self) -> str:
        if "canonical" in self._attributes:
            return self._attributes["canonical"][0]
        elif "icanonical" in self._attributes:
            return self._attributes["icanonical"][0]
        elif self._has_guesses() or self._has_props():
            return self.literal
        return self.lemma if self.lemma else self.literal

    @property
    def canonical(self) -> str:
        """The canonical representation of the concept.

        Returns:
            str: The canonical representation of the concept.
        """
        if self._canonical is None:
            self._canonical = self._get_canonical()
        return self._canonical

    @property
    def attributes(self):
        return self._attributes

    @property
    def stems(self) -> list[str]:
        """The stems of the concept.

        Returns:
            List[str]: The stems of the concept.
        """
        return self.lemmas

    def _get_text(self) -> str:
        """Get a string representation of the concept.

        Returns:
            str: A string representation of the concept.
        """
        retval = ""
        prev_tk = None
        for tk in [cast(Token, a) for a in self.annotations if a.is_token]:
            if prev_tk and prev_tk.end_offset != tk.begin_offset:
                retval += " "
            retval += tk.literal
            prev_tk = tk
        return retval.strip()

    @property
    def text(self) -> str:
        """A string representation of the entity.

        Returns:
            str: A string representation of the entity.
        """
        if self._text is None:
            self._text = self._get_text()
        return self._text

    @property
    def tokens(self) -> list[Token]:
        """The tokens of the concept.

        Returns:
            List[Token]: The tokens of the concept.
        """
        if not self._tokens:
            assert self._sentence_annotations is not None
            self._tokens = [
                cast(Token, annotation)
                for annotation in self._sentence_annotations[self._annotation_idx :]
                if annotation.is_token and annotation.begin_offset < self.end_offset
            ]
        return self._tokens

    @property
    def annotations(self) -> list[Annotation]:
        """The annotations of the concept.

        Returns:
            List[Annotation]: The annotations of the concept.
        """
        if not self._annotations:
            assert self._sentence_annotations is not None
            self._annotations = [
                annotation for annotation in self._sentence_annotations[self._annotation_idx :] if annotation.begin_offset < self.end_offset
            ]
        return self._annotations

    def set_attributes(self, new_attributes: dict):
        """Set the attributes of the entity.

        Args:
            new_attributes (dict): The new attributes to set.
        """
        self._attributes = new_attributes

    def _has_guesses(self) -> bool:
        """Check if the entity has tokens with guess properties.

        Returns:
            bool: True if the entity has tokens with guess properties.
        """
        return len([tk for tk in self.tokens if "guess" in tk.properties]) > 0

    def _has_props(self) -> bool:
        """Check if the entity has tokens with 'Prop' part of speech.

        Returns:
            bool: True if the entity has tokens with 'Prop' part of speech.
        """
        for tk in self.tokens:
            if tk.has_pos("Prop"):
                return True
        return False

    def __setstate__(self, d):
        """Set the state of the entity during unpickling.

        Args:
            d (dict): The state dictionary.
        """
        self.__dict__.update(d)

    def __getstate__(self):
        """Get the state of the entity for pickling.

        Returns:
            dict: The state dictionary.
        """
        return self.__dict__

    def __getattr__(self, name: str) -> Union[None, str, Entity]:
        """Find an attribute or the first child instance of the entity with the given name.

        Some often used attributes are:
        - canonical: canonical representation (str) of the entity
        - attributes: attributes (dict) collected on the entity

        Example:
            ```python
            # Find a child entity in this entity
            person = entity.Person
            # Print the attribute 'gender'
            print(person.gender)
            ```

        Args:
            name (str): Attribute name.

        Returns:
            Union[None, str, Entity]: The first instance of the matching entity or
                the requested attribute value.
        """

        if name in self._attributes:
            return ",".join(self._attributes[name])
        entity = self.find_first(name)
        if entity:
            return cast(Entity, entity)

    def find_first(self, uri: str) -> Union[None, Entity]:
        """Find the first child instance of the entity with the given URI in this entity.

        Example:
            ```python
            # Find a child entity in the current entity
            person = entity.find_first('Person'))
            ```

        Args:
            uri (str): URI or name of the entity.

        Returns:
            Union[None, Entity]: The first matching child instance of the given entity.
        """
        try:
            return next(self._find(uri))
        except StopIteration:
            return None

    def find(self, uri: str) -> List[Entity]:
        """Find all the child entities in the current entity.

        Example:
            ```python
            # Find all the child entities in the current entity
            for person in entity.find('Person')):
                print(person)
            ```

        Args:
            uri (str): URI or name of the entity.

        Returns:
            List[Entity]: The matching child instances of the given entity.
        """
        return [entity for entity in self._find(uri)]

    def _find(self, uri: str) -> Generator[Entity, None, None]:
        assert self._sentence_annotations is not None
        idx = _align(self._annotation_idx, self._sentence_annotations)
        sent_len = len(self._sentence_annotations)
        while idx < sent_len:
            annotation = self._sentence_annotations[idx]
            if annotation.is_concept and uri == cast(Entity, annotation).uri:
                yield cast(Entity, annotation)
            elif annotation.is_token:
                if annotation.begin_offset < self.end_offset:
                    pass
                else:
                    return
            idx += 1

    def match(self, call_able: Callable[[str], bool]) -> List[Entity]:
        """Find all child concepts matching the callable predicate.

        Example:
            ```python
            # Find a child concept in the current concept
            for person in concept.match(lambda uri: uri.startswith('Person')):
                print(person)
            ```

        Args:
            call_able (Callable[[str], bool]): Predicate function that accepts a URI and returns True for matches.

        Returns:
            List[Entity]: The matching child instances of the given concept.
        """
        return [concept for concept in self._match(call_able)]

    def _match(self, call_able: Callable[[str], bool]) -> Generator[Entity, None, None]:
        assert self._sentence_annotations is not None
        idx = _align(self._annotation_idx, self._sentence_annotations)
        sent_len = len(self._sentence_annotations)
        while idx < sent_len:
            annotation = self._sentence_annotations[idx]
            if annotation.is_concept and call_able(cast(Self, annotation).uri):
                yield cast(Entity, annotation)
            elif annotation.is_token:
                if annotation.begin_offset < self.end_offset:
                    pass
                else:
                    return
            idx += 1

    def __getitem__(self, key: str) -> str:
        if self._dict and key in self._dict:
            return self._dict[key]
        return ""

    def rich(self) -> str:
        """Get a rich string representation of the entity.

        Returns:
            str: A rich string representation of the entity.
        """
        retval = "<uri>E</uri>:" + Annotation.__repr__(self) + ": <uri>" + self.uri + "</uri>"
        if self._attributes:
            retval += ",@(<default>"
            for k, vs in sorted(self._attributes.items()):
                for v in vs:
                    retval += f"{k}='{v}' "
            retval += "</default>)"
        return retval

    def keys(self) -> List[str]:
        """Convert an entity object to a dictionary and return its keys.

        This function is used to convert an entity object to a dictionary.

        Example:
            ```python
            { **entity }
            ```

        Returns:
            List[str]: A list of the keys of the entity.
        """
        if not self._dict:
            self._dict = self.to_json()
        return list(self._dict.keys())

    def __repr__(self) -> str:
        retval = "E:" + Annotation.__repr__(self) + ": " + self.uri
        if self._attributes:
            retval += ",@("
            for k, vs in sorted(self._attributes.items()):
                for v in vs:
                    retval += f"{k}='{v}' "
            retval += ")"
        return retval

    def to_json(self) -> dict:
        """Get a dictionary representing a JSON object of the concept.

        Returns:
            dict: A dictionary representing a JSON object of the concept.
        """
        dict_self = {"uri": self.uri, "literal": self.literal, "lemma": self.lemma}
        dict_attributes = {}
        for k, vl in self._attributes.items():
            dict_attributes[k] = ",".join([str(v) for v in vl])
        return {**dict_self, **dict_attributes}

    @staticmethod
    def _document_iter(doc, filter: FilterType = _filter_pass_thru) -> Iterator[Entity]:
        for sentence in doc:
            for annotation in sentence:
                if annotation.is_concept and filter(annotation):
                    yield annotation

    @staticmethod
    def _sentence_iter(sentence, filter: FilterType = _filter_pass_thru) -> Iterator[Entity]:
        for annotation in sentence:
            if annotation.is_concept and filter(annotation):
                yield annotation

    @staticmethod
    def _concept_iter(concept, filter: FilterType = _filter_pass_thru, align: bool = True) -> Iterator[Entity]:
        idx = _align(concept._annotation_idx, concept._sentence_annotations) if align else concept._annotation_idx + 1
        N = len(concept._sentence_annotations)
        while idx < N:
            if concept._annotation_idx != idx:
                annotation = concept._sentence_annotations[idx]
                if annotation.begin_offset >= concept.end_offset:
                    break
                if annotation.is_concept and filter(annotation) and annotation.end_offset <= concept.end_offset:
                    yield cast(Entity, annotation)
            idx += 1

    @staticmethod
    def iter(object, filter: FilterType = _filter_pass_thru, align: bool = True) -> Iterator[Entity]:
        """Iterate over the concepts in a document, analysis, sentence or concept.

        Example:
            ```python
            document = analyzer("Hello from Antwerp, said John Smith.")
            for entity in Entity.iter(document, lambda concept : concept.uri == "NP"):
                print(entity)
            ```

        Args:
            object (AnalysisDocument|TextAnalysis|Sentence|Entity): Object to iterate Sentence or Entity).
            filter (FilterType): Predicate function to filter the entities. A callable that accepts
                a concept and returns True if the concept is considered a match.
            align (bool): Whether to align the iteration.

        Returns:
            Iterator[Entity]: A generator expression yielding concepts.

        Raises:
            TypeError: If object type is not supported.
        """
        from wowool.document.analysis.document import AnalysisDocument
        from wowool.document.analysis.text_analysis import TextAnalysis
        from wowool.annotation import Sentence

        if isinstance(object, AnalysisDocument) and object.analysis:
            yield from Entity._document_iter(object.analysis, filter)
        elif isinstance(object, TextAnalysis):
            yield from Entity._document_iter(object, filter)
        elif isinstance(object, Sentence):
            yield from Entity._sentence_iter(object, filter)
        elif isinstance(object, Entity):
            yield from Entity._concept_iter(object, filter, align)
        else:
            raise TypeError(f"Expected Document, AnalysisDocument, TextAnalysis, Sentence, or Entity but got '{type(object)}'")

    @staticmethod
    def next(sentence: AnnotationList | list[Annotation], object: Annotation) -> Entity | None:
        """Get the next Entity in the sentence.

        Args:
            sentence (List[Annotation]): The list of annotations in the sentence.
            object (Annotation): The current object.

        Returns:
            Entity|None: The next Entity or None if no next entity is found.

        """
        index = object.index + 1
        sentence_length = len(sentence)
        while index < sentence_length:
            if sentence[index].is_concept:
                return cast(Entity, sentence[index])
            else:
                index += 1
        return None

    @staticmethod
    def prev(sentence: AnnotationList | list[Annotation], object: Annotation) -> Entity | None:
        """Get the previous Entity in the sentence.

        Args:
            sentence (List[Annotation]): The list of annotations in the sentence.
            object (Annotation): The current object.

        Returns:
            Entity: The previous Entity or None if no previous entity is found.

        """
        index = object.index - 1
        while index >= 0:
            if sentence[index].is_concept:
                return cast(Entity, sentence[index])
            else:
                index -= 1
        return None

    def _set_sentence_annotations_index(self, sentence_annotations: list[Annotation], annotation_idx: int):
        """Set the sentence annotations and annotation index.

        Args:
            sentence_annotations (list[Annotation]): The sentence annotations.
            annotation_idx (int): The annotation index.
        """
        self._sentence_annotations = sentence_annotations
        self._annotation_idx = annotation_idx

    def get_attribute(self, key: str):
        """Get the first value of an attribute.

        Args:
            key (str): The attribute key.

        Returns:
            str:The first value of the attribute.
        """
        return self._attributes[key][0]

    def get_attributes(self, key: str):
        """Get all values of an attribute.

        Args:
            key (str): The attribute key.

        Returns:
            list[str]: All values of the attribute.
        """
        return self._attributes[key]
