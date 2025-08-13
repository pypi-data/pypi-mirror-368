"""飞书多维表格记录服务示例"""

from dataclasses import dataclass, field
import os
from decimal import Decimal

from lark_util.lark_bitable import bitable_record
from ..lark_bitable import (
    BitableRecordService,
    BitableFieldType,
    BitableBaseRecord,
    bitable_field_metadata,
    bitable_record,
)


@bitable_record(table_id="tblcqzMZS5yXfTqN", view_id="vewVRZLhiK")
@dataclass
class Product(BitableBaseRecord):

    # test_fake_record_id: str = field(
    #     default="",
    #     metadata=bitable_field_metadata("record_id", BitableFieldType.STRING),
    # )
    product_id: str = field(
        default="",
        metadata=bitable_field_metadata("product_id", BitableFieldType.TEXT),
    )
    product_name: str = field(
        default="",
        metadata=bitable_field_metadata("product_name", BitableFieldType.TEXT),
    )
    affiliate_commission: Decimal = field(
        default=Decimal("0.0"),
        metadata=bitable_field_metadata(
            "affiliate_commission", BitableFieldType.DECIMAL
        ),
    )
    # retail_price: float = field(
    #     default=0.0,
    #     metadata=bitable_field_metadata("retail_price", BitableFieldType.FLOAT),
    # )
    shop_code: str = field(
        default="",
        metadata=bitable_field_metadata("shop_code", BitableFieldType.STRING),
    )


def main():
    # 多维表格应用token
    app_token = "AXYab8AxaaMHWSsr8qmczS3hnWA"

    # 创建服务实例
    service = BitableRecordService(app_token, Product)

    # 创建业务对象
    product = Product(
        product_id="12345",
        product_name="测试商品",
        affiliate_commission=Decimal("0.12"),
        shop_code="BZ-BTB",
    )

    try:
        # 创建记录
        print("=== 创建记录 ===")
        created_record = service.create(product)
        print(f"创建成功，record_id: {created_record.record_id}")

        # # 更新记录
        # print("\n=== 更新记录 ===")
        # created_record.product_name = "更新后的商品名称"
        # updated_record = service.update(created_record)
        # print(f"更新成功，product_name: {updated_record.product_name}")

        # # 搜索记录
        # print("\n=== 搜索记录 ===")
        # records, total = service.search_all(limit=5)
        # print(f"搜索到 {len(records)} 条记录，总计 {total} 条")
        # for record in records:
        #     print(
        #         f"  - record_id: {record.record_id}, product_name: {record.product_name}"
        #     )

    except Exception as e:
        print(f"操作失败: {e}")


if __name__ == "__main__":
    main()
