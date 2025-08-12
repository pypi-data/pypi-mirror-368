import os
from typing import Optional
from typing import Type

from ._base import BaseSchema
from ._esrf_v1 import ESRFv1Schema
from ._esrf_v2 import ESRFv2Schema
from ._esrf_v3 import ESRFv3Schema

_SCHEMAS = {
    "esrf_v3": ESRFv3Schema,
    "esrf_v2": ESRFv2Schema,
    "esrf_v1": ESRFv1Schema,
}


def detect_schema(path_str: str) -> Optional[BaseSchema]:
    path_str = os.path.abspath(path_str)
    for schema in _SCHEMAS.values():
        match = schema.match(path_str)
        if match:
            groups = {k: v for k, v in match.groupdict().items() if v is not None}
            return schema(**groups)
    return None


def get_schema(name: Optional[str] = None) -> Type[BaseSchema]:
    if name is None:
        name = "esrf_v3"
    return _SCHEMAS[name]


def get_schema_name(schema: Type[BaseSchema]) -> str:
    for name, cls in _SCHEMAS.items():
        if cls is schema:
            return name
