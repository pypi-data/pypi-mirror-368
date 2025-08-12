from typing import Protocol
from wowool.annotation.annotation import Annotation


class AnnotationList(Protocol):
    def __getitem__(self, index: int) -> Annotation: ...
    def __len__(self) -> int: ...
