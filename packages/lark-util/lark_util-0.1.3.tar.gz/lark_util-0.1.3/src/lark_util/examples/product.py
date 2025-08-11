"""飞书多维表格产品数据模型"""

from dataclasses import dataclass, field as dataclass_field
from decimal import Decimal

from ..lark_bitable import BitableFieldType, bitable_field_metadata


@dataclass
class Product:
    product_id: int = dataclass_field(
        default=0,
        metadata=bitable_field_metadata("product_id", BitableFieldType.INT),
    )
    product_name: str = dataclass_field(
        default="",
        metadata=bitable_field_metadata("product_name", BitableFieldType.TEXT),
    )
    affiliate_commission: Decimal = dataclass_field(
        default=Decimal("0.0"),
        metadata=bitable_field_metadata(
            "affiliate_commission", BitableFieldType.DECIMAL
        ),
    )
    retail_price: float = dataclass_field(
        default=0.0,
        metadata=bitable_field_metadata("retail_price", BitableFieldType.FLOAT),
    )
    shop_code: str = dataclass_field(
        default="",
        metadata=bitable_field_metadata("shop_code", BitableFieldType.STRING),
    )
