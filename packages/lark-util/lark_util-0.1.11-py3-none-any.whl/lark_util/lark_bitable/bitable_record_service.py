"""飞书多维表格记录服务类

基于官方lark-oapi SDK的多维表格操作功能，提供统一的服务接口
"""

import json
from typing import Dict, Any, Optional, List, Tuple, TypeVar, Type, Generic, Callable
import lark_oapi as lark

from .create_bitable_record import create_bitable_record
from .search_bitable_records import search_bitable_records
from .update_bitable_record import update_bitable_record
from .bitable_record import BitableBaseRecord, parse_bitable_record, RecordEncoder

T = TypeVar("T", bound=BitableBaseRecord)


class BitableRecordService(Generic[T]):
    """飞书多维表格记录服务类

    支持泛型操作，提供创建、更新、查询功能
    """

    def __init__(self, app_token: str, model_cls: Type[T], default_batch: int = 100):
        """初始化服务

        Args:
            app_token: 多维表格应用token
            model_cls: 业务对象类型，必须是BitableBaseRecord的子类
            default_batch: 默认批次大小，默认100
        """
        self.app_token = app_token
        self.model_cls = model_cls
        self.default_batch = default_batch

    def create(self, model: T) -> T:
        """创建多维表格记录

        Args:
            model: 业务对象，record_id必须为空

        Returns:
            T: 创建后的业务对象，包含record_id

        Raises:
            ValueError: 当record_id不为空时抛出异常
        """
        if model.record_id:
            raise ValueError("创建记录时record_id必须为空")

        # 从装饰器获取table_id
        table_id = self.model_cls.get_table_id()

        # 将业务对象转换为字段值字典
        fields = model.to_fields()

        # 创建记录
        record = create_bitable_record(self.app_token, table_id, fields)

        # print(f"fields: {json.dumps(fields, ensure_ascii=False, indent=2)}")
        # print(f"record: {json.dumps(record.__dict__, ensure_ascii=False, indent=2)}")

        # 从返回的记录解析为业务对象
        return parse_bitable_record(self.model_cls, record)

    def update(self, model: T) -> T:
        """更新多维表格记录

        Args:
            model: 业务对象，必须包含record_id

        Returns:
            T: 更新后的业务对象

        Raises:
            ValueError: 当record_id为空时抛出异常
        """
        if not model.record_id:
            raise ValueError("更新记录时record_id不能为空")

        # 从装饰器获取table_id
        table_id = self.model_cls.get_table_id()

        # 将业务对象转换为字段值字典
        fields = model.to_fields()

        result = update_bitable_record(
            self.app_token, table_id, model.record_id, fields
        )

        # 从返回的记录解析为业务对象
        return parse_bitable_record(self.model_cls, result)

    def save(self, model: T) -> T:
        """保存记录

        如果记录有record_id则更新，否则创建新记录

        Args:
            model: 业务对象

        Returns:
            T: 保存后的业务对象
        """
        if hasattr(model, "record_id") and model.record_id:
            return self.update(model)
        else:
            return self.create(model)

    def search(
        self,
        field_names: Optional[List[str]] = None,
        conjunction: Optional[str] = None,
        conditions: Optional[List[Tuple[str, str, List[str]]]] = None,
        sorts: Optional[List[Tuple[str, bool]]] = None,
        limit: Optional[int] = None,
        batch: Optional[int] = None,
    ) -> Tuple[List[T], int]:
        """搜索多维表格记录，支持分页

        Args:
            field_names: 要返回的字段名列表，默认为None（返回所有字段）
            conjunction: 条件连接符，可选值为"and"或"or"，默认为None
            conditions: 筛选条件列表，每个条件为(字段名, 操作符, 值列表)的三元组，默认为None
            sorts: 排序条件列表，每个条件为(字段名, 是否降序)的二元组，默认为None
            limit: 限制返回的记录数量，如果不提供则返回所有记录
            batch: 批次大小，如果不提供则使用default_batch

        Returns:
            Tuple[List[T], int]: 业务对象列表，以及总记录数
        """
        # 从装饰器获取table_id和view_id
        table_id = self.model_cls.get_table_id()
        view_id = self.model_cls.get_view_id()

        all_records = []
        page_token = None
        total = 0
        collected_count = 0

        # 确定使用的批次大小
        current_batch = batch if batch is not None else self.default_batch

        while True:
            # 如果设置了limit，计算本次请求的batch_size
            current_batch_size = current_batch
            if limit is not None:
                remaining = limit - collected_count
                if remaining <= 0:
                    break
                current_batch_size = min(current_batch, remaining)

            result = search_bitable_records(
                self.app_token,
                table_id,
                view_id,
                field_names,
                conjunction,
                conditions,
                sorts,
                page_token,
                current_batch_size,
            )

            # 更新分页状态
            page_token = result.page_token
            total = result.total

            # 解析记录为业务对象
            for item in result.items:
                business_obj = parse_bitable_record(self.model_cls, item)
                all_records.append(business_obj)
                collected_count += 1

                # 如果达到limit，停止收集
                if limit is not None and collected_count >= limit:
                    break

            # 如果没有更多记录或已达到limit，退出循环
            if not result.has_more or (limit is not None and collected_count >= limit):
                break

        return all_records, total

    def search_and_process_batch(
        self,
        process_func: Callable[[List[T]], None],
        field_names: Optional[List[str]] = None,
        conjunction: Optional[str] = None,
        conditions: Optional[List[Tuple[str, str, List[str]]]] = None,
        sorts: Optional[List[Tuple[str, bool]]] = None,
        limit: Optional[int] = None,
        batch: Optional[int] = None,
    ) -> None:
        """搜索记录并批量处理

        Args:
            process_func: 处理函数，接收List[T]，无返回值
            field_names: 要返回的字段名列表，默认为None（返回所有字段）
            conjunction: 条件连接符，可选值为"and"或"or"，默认为None
            conditions: 筛选条件列表，每个条件为(字段名, 操作符, 值列表)的三元组，默认为None
            sorts: 排序条件列表，每个条件为(字段名, 是否降序)的二元组，默认为None
            limit: 限制返回的记录数量，如果不提供则返回所有记录
            batch: 批次大小，如果不提供则使用default_batch
        """
        # 从装饰器获取table_id和view_id
        table_id = self.model_cls.get_table_id()
        view_id = self.model_cls.get_view_id()

        page_token = None
        collected_count = 0

        # 确定使用的批次大小
        current_batch = batch if batch is not None else self.default_batch

        while True:
            # 如果设置了limit，计算本次请求的batch_size
            current_batch_size = current_batch
            if limit is not None:
                remaining = limit - collected_count
                if remaining <= 0:
                    break
                current_batch_size = min(current_batch, remaining)

            result = search_bitable_records(
                self.app_token,
                table_id,
                view_id,
                field_names,
                conjunction,
                conditions,
                sorts,
                page_token,
                current_batch_size,
            )

            # 解析记录为业务对象
            batch_records = []
            for item in result.items:
                business_obj = parse_bitable_record(self.model_cls, item)
                batch_records.append(business_obj)
                collected_count += 1

                # 如果达到limit，停止收集
                if limit is not None and collected_count >= limit:
                    break

            # 处理当前批次的记录
            if batch_records:
                process_func(batch_records)

            # 如果没有更多记录或已达到limit，退出循环
            if not result.has_more or (limit is not None and collected_count >= limit):
                break

            page_token = result.page_token
