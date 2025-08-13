"""飞书多维表格记录处理模块"""

from abc import ABC
from dataclasses import dataclass, field
from decimal import Decimal
import json
from typing import Any, Dict, Type, TypeVar
from functools import wraps
from lark_oapi.api.bitable.v1 import AppTableRecord

from .bitable_field_type import BitableFieldType

T = TypeVar("T", bound="BitableBaseRecord")


@dataclass
class BitableBaseRecord(ABC):
    """飞书多维表格基础记录类"""

    record_id: str = field(default="")

    def to_fields(self) -> Dict[str, Any]:
        """将对象转换为字典格式"""
        cls = self.__class__
        result = {}
        for field_name, field_obj in cls.__dataclass_fields__.items():
            alias = _get_field_alias(cls, field_name)
            if not alias:
                continue
            value = getattr(self, field_name)
            result[alias] = _escape_out(cls, field_name, value)
        return result


def bitable_field_metadata(
    field_name: str,
    field_type: BitableFieldType,
) -> Dict[str, Any]:
    """创建多维表格字段元数据"""
    return {"field_name": field_name, "field_type": field_type}


def _escape_out(cls: Any, field_name: str, value: Any) -> Any:
    """字段输出转义"""
    field_obj = cls.__dataclass_fields__[field_name]
    field_type = field_obj.metadata.get("field_type")
    if field_type:
        return field_type.value.escape_out(value)
    return value


def _escape_in(cls: Any, field_name: str, value: Any) -> Any:
    """字段输入转义"""
    field_obj = cls.__dataclass_fields__[field_name]
    field_type = field_obj.metadata.get("field_type")
    if field_type:
        return field_type.value.escape_in(value)
    return value


def _get_field_alias(cls: Any, field_name: str) -> str:
    """获取字段别名"""
    field_obj = cls.__dataclass_fields__[field_name]
    return field_obj.metadata.get("field_name", "")


def parse_bitable_record(cls: Type[T], input: AppTableRecord) -> T:
    """将 AppTableRecord 解析为指定类型的对象"""
    obj = cls()
    # 设置record_id
    if hasattr(input, "record_id") and input.record_id:
        obj.record_id = input.record_id

    # 处理fields字段
    fields = input.fields if hasattr(input, "fields") and input.fields else {}
    for field_name, field_obj in cls.__dataclass_fields__.items():
        if field_name == "record_id":  # BitableBaseRecord
            continue
        alias = _get_field_alias(cls, field_name)
        if alias in fields:
            setattr(obj, field_name, _escape_in(cls, field_name, fields[alias]))
    return obj


class RecordEncoder(json.JSONEncoder):
    """自定义JSON编码器，支持BitableBaseRecord和Decimal类型"""

    def default(self, obj):
        if isinstance(obj, BitableBaseRecord):
            return obj.to_fields()
        elif isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


def bitable_record(table_id: str, view_id: str):
    """飞书多维表格记录装饰器

    用于标注实体类的 table_id 和 view_id

    Args:
        table_id: 多维表格的表格ID
        view_id: 多维表格的视图ID

    Returns:
        装饰后的类，添加了 _table_id 和 _view_id 属性

    Example:
        @bitable_record(table_id="tblXXX", view_id="vewYYY")
        class Product(BitableBaseRecord):
            pass
    """

    def decorator(cls: Type[T]) -> Type[T]:
        # 为类添加表格和视图ID属性
        cls._table_id = table_id
        cls._view_id = view_id

        # 添加获取表格ID的类方法
        @classmethod
        def get_table_id(cls) -> str:
            """获取表格ID"""
            return cls._table_id

        # 添加获取视图ID的类方法
        @classmethod
        def get_view_id(cls) -> str:
            """获取视图ID"""
            return cls._view_id

        # 将方法绑定到类上
        cls.get_table_id = get_table_id
        cls.get_view_id = get_view_id

        return cls

    return decorator
