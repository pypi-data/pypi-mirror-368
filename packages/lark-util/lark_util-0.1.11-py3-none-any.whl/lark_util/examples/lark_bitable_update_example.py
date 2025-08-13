"""飞书多维表格更新记录示例"""

import os
import lark_oapi as lark
from ..lark_bitable import update_bitable_record


def main():
    # 多维表格应用token
    app_token = "AXYab8AxaaMHWSsr8qmczS3hnWA"
    # 表格ID
    table_id = "tblOAOp3VcTHABV3"
    # 记录ID
    record_id = "recuTpwvQv2UkI"

    # 字段值
    fields = {
        "1": "https://www.google.com/6",
        "2": [{"id": "2ge1ge5d"}],
        "3": 1754755200000,
        "handle": "abcd6",
    }

    # 更新记录
    try:
        result = update_bitable_record(app_token, table_id, record_id, fields)
        print(f"更新记录成功: {lark.JSON.marshal(result)}")
    except Exception as e:
        print(f"更新记录失败: {e}")


if __name__ == "__main__":
    main()
