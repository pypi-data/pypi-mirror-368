def _has_module(name) -> bool:
    try:
        import importlib.util

        module_spec = importlib.util.find_spec(name)
        return True if module_spec else False
    except ModuleNotFoundError:
        return False


class AppConsole:
    def __init__(self, console):
        self.console_ = console

    def log(self, obj, **kwargs):
        self.console_.log(obj, **kwargs)

    def print(self, obj, **kwargs):
        self.console_.print(obj, **kwargs)

    def print_json(self, obj, **kwargs):
        self.console_.print_json(obj, **kwargs)


_markers = {
    "default": "default",
    "error": "red bold",
    "literal": "green bold",
    "stem": "green",
    "lemma": "green",
    "token": "yellow",
    "uri": "blue",
    "warning": "yellow bold",
    "info": "blue bold",
    "note": "bold",
    "prog": "bold",
}


class RichConsole:
    def __init__(self, console, console_stderr):
        self.console_ = console
        self.console_stderr_ = console_stderr

    def log(self, obj, **kwargs):
        self.console_.log(obj, **kwargs)

    def print(self, obj, **kwargs):

        if isinstance(obj, str):
            for marker, color in _markers.items():
                obj = obj.replace(f"<{marker}>", f"[{color}]").replace(f"</{marker}>", f"[/{color}]")

        if "file" in kwargs:
            del kwargs["file"]
            self.console_stderr_.print(obj, **kwargs)
        else:
            self.console_.print(obj, **kwargs)

    def print_json(self, obj, **kwargs):
        if not isinstance(obj, str):
            import json

            obj = json.dumps(obj, ensure_ascii=False)
        self.console_.print_json(obj, ensure_ascii=False, **kwargs)


class PrintConsole:
    def log(self, obj, **kwargs):
        print(obj, **kwargs)

    def print(self, obj, **kwargs):
        if isinstance(obj, str):
            for marker in _markers.keys():
                obj = obj.replace(f"<{marker}>", "").replace(f"</{marker}>", "")
        print(obj, **kwargs)

    def print_json(self, obj, **kwargs):
        import json

        print(json.dumps(obj, indent=4, sort_keys=True, ensure_ascii=False), **kwargs)


console = None
if _has_module("rich"):
    try:
        from rich.console import Console
        from rich.theme import Theme

        custom_theme = Theme(
            {
                "info": "dim cyan",
                "warning": "magenta",
                "danger": "bold red",
                "h1": "bold blue",
            }
        )
        console = AppConsole(RichConsole(Console(theme=custom_theme), Console(stderr=True, theme=custom_theme)))

    except Exception as ex:
        # TODO: change this into a warning
        print("warning rich not installed: 'pip install rich' to have colorful messages.", ex)
        pass
if not console:
    console = AppConsole(PrintConsole())


def has_rich():
    """
    Check if the rich library is available.

    :return: True if rich is available, False otherwise.
    """
    return _has_module("rich")
