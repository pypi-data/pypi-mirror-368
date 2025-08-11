"""飞书多维表格创建记录模块

基于官方lark-oapi SDK的多维表格创建记录功能，封装类型转换逻辑
"""

from typing import Dict, Any, TypeVar, Type

from .create_bitable_record import create_bitable_record
from .field_escape import convert_out

T = TypeVar("T")


def create_bitable_record_with_type[T](  # type: ignore
    app_token: str,
    table_id: str,
    model: T,
) -> str:
    """创建多维表格记录，支持类型转换

    Args:
        app_token: 多维表格应用token
        table_id: 表格ID
        model: 业务对象

    Returns:
        str: 新创建的记录ID
    """
    # 将业务对象转换为字段值字典
    fields = convert_out(model)

    # 创建记录
    record = create_bitable_record(app_token, table_id, fields)

    # 返回记录ID
    return record["record_id"]
