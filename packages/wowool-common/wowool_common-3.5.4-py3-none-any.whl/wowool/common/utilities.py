import re


def strip_version(component_name: str) -> str:
    return re.sub("""(.*)@(?:dev\\d*|[0-9\\.]+[\\d]+)(\\.(?:language|dom))?""", "\\1\\2", component_name)


def split_component(component_name: str) -> dict | None:
    """
    Splits a component name into its name, version, and type.
    """
    m = re.match("""(.*)@(dev\\d*|[0-9\\.]+[\\d]+)\\.(language|dom)""", component_name)
    if m:
        return {"name": m.group(1), "version": m.group(2), "type": m.group(3)}


def get_lxware_version():
    from os import environ

    if "WOWOOL_LXWARE_VERSION" in environ:
        return environ["WOWOOL_LXWARE_VERSION"]
    return ""
