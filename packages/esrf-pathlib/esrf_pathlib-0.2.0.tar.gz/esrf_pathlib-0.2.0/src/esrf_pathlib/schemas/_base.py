import dataclasses
import datetime
import os
import re
import string
from typing import Any
from typing import Callable
from typing import List
from typing import Optional
from typing import Union

SEP = r"[\\/]"
NOTSEP = r"[^\\/]"
FieldValueType = Union[
    str,
    datetime.date,
    datetime.datetime,
    None,
]


def esrfpath_property(func: Callable[[Any], "BaseSchema"]) -> property:
    func._is_esrfpath = True
    return property(func)


class PathSegment:
    def __init__(self, match_pattern: str, render_template: Optional[str] = None):
        r"""
        A path segment used to both match and reconstruct file paths.

        :param match_pattern: A regex pattern (without ^/$ anchors) for matching this segment.
        :param render_template: A Python format string using field names from the schema,
                                e.g. "{collection}_{dataset}" or "{session_date:%Y%m%d}".
        """
        self._match_pattern = match_pattern
        self._render_template = render_template
        self._field_names = [
            fname
            for _, fname, _, _ in string.Formatter().parse(render_template)
            if fname
        ]

    @property
    def match_pattern(self) -> str:
        return self._match_pattern

    def format_segment(self, schema: "BaseSchema") -> Optional[str]:
        fields = {name: getattr(schema, name) for name in self._field_names}
        missing = [name for name, value in fields.items() if value is None]
        if missing:
            return None
        return self._render_template.format(**fields)


@dataclasses.dataclass
class BaseSchema:
    @staticmethod
    def _path_segments() -> List[PathSegment]:
        raise NotImplementedError

    @classmethod
    def match(cls, path: str) -> Any:
        return cls._regex().match(path)

    @classmethod
    def _regex(cls) -> re.Pattern:
        pattern = "".join(s.match_pattern for s in cls._path_segments())
        return re.compile(f"^{pattern}", re.VERBOSE)

    @property
    def field_names(self) -> List[str]:
        return [field.name for field in dataclasses.fields(self)]

    @property
    def path_properties(self) -> List[str]:
        path_properties = []
        cls = type(self)
        for name in dir(cls):
            attr = getattr(cls, name, None)
            if isinstance(attr, property) and getattr(attr.fget, "_is_esrfpath", False):
                path_properties.append(name)
        return path_properties

    def _raise_on_incomplete(self, *required_fields: str):
        for name in required_fields:
            if getattr(self, name) is None:
                raise AttributeError(f"Field has no value: {name!r}")

    def reconstruct_path(self, *required_fields: str) -> str:
        self._raise_on_incomplete(*required_fields)
        parts = []
        for seg in self._path_segments():
            val = seg.format_segment(self)
            if val is None:
                break
            parts.append(val)
        return os.path.join(*parts)

    def replace(self, **changes: FieldValueType) -> "BaseSchema":
        return dataclasses.replace(self, **changes)

    def _replace_and_reconstruct(self, **changes: FieldValueType) -> str:
        schema = self.replace(**changes)
        exclude = [name for name, value in changes.items() if value is None]
        required_fields = [name for name in self.field_names if name not in exclude]
        return schema.reconstruct_path(*required_fields)
