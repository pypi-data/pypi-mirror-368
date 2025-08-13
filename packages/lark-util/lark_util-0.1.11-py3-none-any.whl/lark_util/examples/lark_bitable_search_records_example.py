"""飞书多维表格搜索记录示例"""

import os
import lark_oapi as lark
from ..lark_bitable import search_bitable_records


def main():
    # 多维表格应用token
    app_token = "AXYab8AxaaMHWSsr8qmczS3hnWA"
    # 表格ID
    table_id = "tblOAOp3VcTHABV3"
    # 视图ID
    view_id = "vewqxZ4Id1"

    field_names = ["handle", "1", "2", "3", "4"]

    # 搜索条件
    conditions = [
        (
            "handle",
            "is",
            ["Sefiora"],
        ),
        (
            "店铺",
            "is",
            ["MX-Sefiora"],
        ),
    ]

    # 排序条件
    sort = [("3", False)]

    # 搜索记录
    try:
        result = search_bitable_records(
            app_token, table_id, view_id, field_names, "and", conditions, sort
        )
        print(f"搜索记录成功: {lark.JSON.marshal(result, indent=4)}")
    except Exception as e:
        print(f"搜索记录失败: {e}")


if __name__ == "__main__":
    main()
