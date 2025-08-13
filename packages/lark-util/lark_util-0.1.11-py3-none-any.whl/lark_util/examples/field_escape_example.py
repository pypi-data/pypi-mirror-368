import json
from lark_oapi.api.bitable.v1 import AppTableRecord

from ..lark_bitable import RecordEncoder
from .product import Product
from ..lark_bitable import parse_bitable_record

import dataclasses
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import orjson


def dump_json(obj: Any) -> str:
    """用 orjson 把任意对象转成 JSON 字符串"""

    def default(o):
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, Decimal):
            return float(o)
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)  # type: ignore
        if isinstance(o, uuid.UUID):
            return str(o)
        if hasattr(o, "__dict__"):
            return o.__dict__
        raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")

    return orjson.dumps(obj, default=default, option=orjson.OPT_INDENT_2).decode(
        "utf-8"
    )


def main():
    # 模拟从飞书API获取的AppTableRecord数据
    app_table_record = (
        AppTableRecord.builder()
        .record_id("rec123456")
        .fields(
            {
                "record_id": "fake_record_id_1",
                "product_id": 12345,
                "product_name": [
                    {
                        "text": "测试商品",
                        "type": "text",
                        "link": "https://www.baidu.com",
                    }
                ],
                "affiliate_commission": 0.12,
                "retail_price": 20.23,
                "shop_code": "BZ-BTB",
                "create_time": 1755010462000,
                "update_time": None,
            }
        )
        .build()
    )

    # 使用新的parse_bitable_record函数，直接接受AppTableRecord
    product = parse_bitable_record(Product, app_table_record)
    print("Product object:", dump_json(product))
    print("Record ID from base class:", product.record_id)

    # 使用继承的to_fields方法
    output_data = product.to_fields()
    print("Output data using inherited method:", dump_json(output_data))

    # 也可以使用包函数方式
    output_data_func = product.to_fields()
    print("Output data using function:", output_data_func)


if __name__ == "__main__":
    main()
