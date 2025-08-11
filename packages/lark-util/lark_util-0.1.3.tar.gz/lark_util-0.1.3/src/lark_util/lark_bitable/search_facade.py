"""飞书多维表格查询迭代器模块

基于官方lark-oapi SDK的多维表格搜索功能，封装翻页逻辑
"""

from typing import Dict, Any, Optional, List, Tuple, TypeVar, Type, Generic

from .search_bitable_records import search_bitable_records
from .field_escape import convert_in

T = TypeVar("T")


def search_bitable_records_with_page[T](  # type: ignore
    app_token: str,
    table_id: str,
    view_id: str,
    model_cls: Type[T],
    field_names: Optional[List[str]] = None,
    conjunction: Optional[str] = None,
    conditions: Optional[List[Tuple[str, str, List[str]]]] = None,
    sorts: Optional[List[Tuple[str, bool]]] = None,
    page_num: int = 1,
    page_size: int = 20,
) -> Tuple[List[Tuple[str, T]], int]:
    """搜索多维表格记录，支持分页

    Args:
        app_token: 多维表格应用token
        table_id: 表格ID
        view_id: 视图ID
        model_cls: 业务对象类型
        field_names: 要返回的字段名列表，默认为None（返回所有字段）
        conjunction: 条件连接符，可选值为"and"或"or"，默认为None
        conditions: 筛选条件列表，每个条件为(字段名, 操作符, 值列表)的三元组，默认为None
        sorts: 排序条件列表，每个条件为(字段名, 是否降序)的二元组，默认为None
        page_num: 页码，从1开始，默认为1
        page_size: 每页记录数，默认为20

    Returns:
        Tuple[List[Tuple[str, T]], int]: 记录ID和业务对象的元组列表，以及总记录数
    """
    # 初始化分页状态
    page_token = None
    has_more = True
    total = 0
    current_page = 0

    # 如果当前页码小于目标页码，继续获取下一页
    while current_page < page_num:
        response = search_bitable_records(
            app_token,
            table_id,
            view_id,
            field_names,
            conjunction,
            conditions,
            sorts,
            page_token,
            page_size,
        )

        # 更新分页状态
        has_more = response.has_more
        page_token = response.page_token
        total = response.total
        current_page += 1

        # 如果已经到达目标页码，转换并返回记录列表
        if current_page == page_num:
            return [
                (item.record_id, convert_in(model_cls, item.fields))
                for item in response.items
            ], total

        # 如果没有更多数据，提前返回空列表
        if not has_more:
            return [], total

    return [], total
