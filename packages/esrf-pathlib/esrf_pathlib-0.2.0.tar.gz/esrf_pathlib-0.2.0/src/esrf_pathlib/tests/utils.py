import os
import pathlib
import sys

_IS_WINDOWS = sys.platform == "win32"
_BASE_PATH = "X:\\" if _IS_WINDOWS else "/data"


def make_path(*parts) -> str:
    return os.path.join(_BASE_PATH, *parts)


def safe_repr(path: pathlib.Path) -> str:
    if _IS_WINDOWS:
        return repr(path).replace("/", "\\")
    else:
        return repr(path)
