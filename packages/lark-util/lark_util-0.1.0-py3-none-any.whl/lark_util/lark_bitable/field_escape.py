from dataclasses import field
from typing import Any, Dict, Type, TypeVar

from .bitable_field_type import BitableFieldType

T = TypeVar("T")


def bitable_field_metadata(
    field_name: str,
    field_type: BitableFieldType,
) -> Dict[str, Any]:
    return {"field_name": field_name, "field_type": field_type}


def escape_out(cls: Any, field_name: str, value: Any) -> Any:
    field_obj = cls.__dataclass_fields__[field_name]
    field_type = field_obj.metadata.get("field_type")
    if field_type:
        return field_type.value.escape_out(value)
    return value


def escape_in(cls: Any, field_name: str, value: Any) -> Any:
    field_obj = cls.__dataclass_fields__[field_name]
    field_type = field_obj.metadata.get("field_type")
    if field_type:
        return field_type.value.escape_in(value)
    return value


def get_field_alias(cls: Any, field_name: str) -> str:
    field_obj = cls.__dataclass_fields__[field_name]
    return field_obj.metadata.get("field_name", field_name)


def convert_in(cls: Type[T], input: Dict[str, Any]) -> T:
    obj = cls()
    for field_name, field_obj in cls.__dataclass_fields__.items():
        alias = get_field_alias(cls, field_name)
        if alias in input:
            setattr(obj, field_name, escape_in(cls, field_name, input[alias]))
    return obj


def convert_out(output: T) -> Dict[str, Any]:
    cls = output.__class__
    result = {}
    for field_name, field_obj in cls.__dataclass_fields__.items():
        alias = get_field_alias(cls, field_name)
        value = getattr(output, field_name)
        result[alias] = escape_out(cls, field_name, value)
    return result
