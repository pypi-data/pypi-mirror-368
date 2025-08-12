"""飞书多维表格分页查询示例"""

from typing import Any, Tuple, List
import json
import lark_oapi as lark

from ..lark_bitable import (
    search_bitable_records_with_page,
)
from .product import Product
from ..lark_bitable import RecordEncoder


def main():
    # 多维表格应用token
    app_token = "AXYab8AxaaMHWSsr8qmczS3hnWA"
    # 表格ID
    table_id = "tblcqzMZS5yXfTqN"
    # 视图ID
    view_id = "vewVRZLhiK"

    # 要返回的字段名列表
    field_names = ["product_id", "product_name", "affiliate_commission", "shop_code"]

    # 搜索条件
    conditions = [
        (
            "shop_code",
            "is",
            ["MX-Sefiora"],
        ),
    ]

    # 排序条件
    sorts = [("product_id", False)]

    # 获取第一页记录
    records, total = search_bitable_records_with_page(
        app_token,
        table_id,
        view_id,
        Product,
        field_names,
        "and",
        conditions,
        sorts,
        page_num=1,
        page_size=10,
    )

    print(f"总记录数: {total}")
    print(
        f"第一页: {json.dumps(records, cls=RecordEncoder, indent=2, ensure_ascii=False)}"
    )


if __name__ == "__main__":
    main()
