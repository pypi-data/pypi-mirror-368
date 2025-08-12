from dataclasses import dataclass, field
from typing import Any


@dataclass
class UUID:
    """A UUID object representing a component identifier with options.

    Attributes:
        name (str): The name of the component.
        options (dict[str,Any]): Configuration options for the component.
    """

    name: str
    options: dict[str, Any] = field(default_factory=dict)

    def to_json(self):
        """Convert the UUID to a JSON-serializable dictionary.

        Returns:
            dict[str,Any]: A dictionary containing the name and options.
        """
        return {"name": self.name, "options": self.options}


def createUUID(uid: str | UUID | dict) -> UUID:
    """Create a UUID object from various input types.

    Args:
        uid (str|UUID|dict): The input to create a UUID from. Can be a string name,
            an existing UUID object, or a dictionary with 'name' and optional 'options' keys.

    Returns:
        UUID: A UUID object created from the input.

    Raises:
        ValueError: If the input type is not supported.

    Examples:
        >>> createUUID("component_name")
        UUID(name='component_name', options={})

        >>> createUUID({"name": "component", "options": {"key": "value"}})
        UUID(name='component', options={'key': 'value'})
    """
    if isinstance(uid, str):
        return UUID(name=uid)
    elif isinstance(uid, UUID):
        return uid
    elif isinstance(uid, dict):
        if "options" not in uid:
            uid["options"] = {}
        return UUID(name=uid["name"], options=uid["options"])
    else:
        raise ValueError(f"Invalid UID: {uid}")


@dataclass
class ComponentInfo:
    """Component information for pipeline components.

    Contains metadata and configuration information for a component in the pipeline.

    Attributes:
        options (dict[str,Any]): Configuration options on how the component has been initialized.
        type (str): The type of component (e.g., 'language', 'domain', 'app').
        name (str): The name of the component. (e.g., 'english.language', 'english-entity.dom').
        uid (str): Unique identifier for the component.
        filename (str|None): Optional filename associated with the component (if applicable).
        app (dict[str,str]|None): Optional application-specific information.
        original (str|None): Optional original source information.
    """

    options: dict[str, Any]
    type: str
    name: str
    uid: str
    filename: str | None = None
    app: dict[str, str] | None = None
    original: str | None = None

    def to_json(self):
        """Convert the ComponentInfo to a JSON-serializable dictionary.

        Returns:
            dict[str, Any]: A dictionary containing the component information with
                type, uid, and optionally options, filename, and app information.
        """
        retval: dict[str, Any] = {"type": self.type, "uid": self.uid}
        if self.options:
            retval["options"] = self.options
        if self.filename:
            retval["filename"] = self.filename
        if self.app:
            retval["app"] = self.app
        return retval
