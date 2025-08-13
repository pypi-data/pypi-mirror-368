"""飞书多维表格产品数据模型"""

from dataclasses import dataclass, field
import datetime
from decimal import Decimal
from typing import Optional

from ..lark_bitable import BitableFieldType, bitable_field_metadata, bitable_record
from ..lark_bitable.bitable_record import BitableBaseRecord


@bitable_record(table_id="tblcqzMZS5yXfTqN", view_id="vewVRZLhiK")
@dataclass
class Product(BitableBaseRecord):

    test_fake_record_id: str = field(
        default="",
        metadata=bitable_field_metadata("record_id", BitableFieldType.STRING),
    )
    product_id: int = field(
        default=0,
        metadata=bitable_field_metadata("product_id", BitableFieldType.INT),
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
    retail_price: float = field(
        default=0.0,
        metadata=bitable_field_metadata("retail_price", BitableFieldType.FLOAT),
    )
    shop_code: str = field(
        default="",
        metadata=bitable_field_metadata("shop_code", BitableFieldType.STRING),
    )
    create_time: Optional[datetime] = field(
        default=None,
        metadata=bitable_field_metadata("create_time", BitableFieldType.DATE),
    )
    update_time: Optional[datetime] = field(
        default=None,
        metadata=bitable_field_metadata("update_time", BitableFieldType.DATE),
    )
