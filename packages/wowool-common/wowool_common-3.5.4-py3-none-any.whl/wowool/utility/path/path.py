from pathlib import Path
from os.path import expandvars


def expand_path(path: str | Path, resolve: bool = True) -> Path:
    if isinstance(path, str):
        path = path.strip('"')
    fn = Path(expandvars(path)).expanduser()
    if resolve:
        fn = fn.resolve()
    return fn
