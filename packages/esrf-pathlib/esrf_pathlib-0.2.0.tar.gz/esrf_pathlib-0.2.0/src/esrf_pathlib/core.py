import pathlib
import sys
from typing import Any
from typing import List
from typing import Optional

from .schemas import detect_schema
from .schemas._base import FieldValueType
from .schemas._utils import get_schema
from .schemas._utils import get_schema_name

if sys.version_info >= (3, 12):
    # https://docs.python.org/3/whatsnew/3.12.html
    # -> The pathlib.Path class now supports subclassing

    class _BaseESRFPath(pathlib.Path):
        __slots__ = ("_esrf_schema",)

        def __init__(self, *args):
            super().__init__(*args)
            _add_esrf_schema(self, *args)

else:

    class _BaseESRFPath(type(pathlib.Path())):
        __slots__ = ("_esrf_schema",)

        def __new__(cls, *args):
            self = super().__new__(cls, *args)
            _add_esrf_schema(self, *args)
            return self

        @classmethod
        def _from_parts(cls, args, **kwargs):
            self = super()._from_parts(args, **kwargs)
            _add_esrf_schema(self, *args)
            return self

        @classmethod
        def _from_parsed_parts(cls, drv, root, parts):
            self = super()._from_parsed_parts(drv, root, parts)
            _add_esrf_schema(self)
            return self


class ESRFPath(_BaseESRFPath):
    def __getattr__(self, name: str) -> Optional[str]:
        if self._esrf_schema is None:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}' (not an ESRF path)"
            )

        if name in self._get_schema_field_names():
            return getattr(self._esrf_schema, name)

        if name in self._get_schema_path_properties():
            return self.__class__(getattr(self._esrf_schema, name))

        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    def __setattr__(self, name: str, value: Any) -> None:
        if not name.startswith("_") and name in self._get_schema_field_names():
            raise AttributeError(f"can't set attribute {name!r}")
        return super().__setattr__(name, value)

    def _get_schema_field_names(self) -> List[str]:
        if self._esrf_schema is None:
            return []
        return self._esrf_schema.field_names

    def _get_schema_path_properties(self) -> List[str]:
        if self._esrf_schema is None:
            return []
        return self._esrf_schema.path_properties

    def __dir__(self) -> List[str]:
        return sorted(
            set(super().__dir__())
            | set(self._get_schema_field_names())
            | set(self._get_schema_path_properties())
        )

    @property
    def schema_name(self) -> Optional[str]:
        """Name of the ESRF path schema if it matches a known schema."""
        if self._esrf_schema:
            return get_schema_name(type(self._esrf_schema))

    def replace_fields(self, **changes: FieldValueType) -> "ESRFPath":
        """Creates a new `ESRFPath`, replacing fields with values from `changes`."""
        if self._esrf_schema is None:
            raise RuntimeError("Not an ESRF path")
        original_schema_base = self._esrf_schema.reconstruct_path()
        sub_path = self.relative_to(original_schema_base)
        new_schema_base = self._esrf_schema.replace(**changes).reconstruct_path()
        return self.__class__(new_schema_base) / sub_path

    @classmethod
    def from_fields(
        cls, schema_name: Optional[str] = None, **fields: FieldValueType
    ) -> "ESRFPath":
        """Create `ESRFPath` from schema fields."""
        return cls(get_schema(schema_name)(**fields).reconstruct_path())


def _add_esrf_schema(self: _BaseESRFPath, *args) -> None:
    self._esrf_schema = None
    _esrf_schema = detect_schema(str(self))
    if _esrf_schema is None:
        for arg in args:
            if isinstance(arg, ESRFPath):
                _esrf_schema = arg._esrf_schema
                if _esrf_schema is not None:
                    break
    self._esrf_schema = _esrf_schema
