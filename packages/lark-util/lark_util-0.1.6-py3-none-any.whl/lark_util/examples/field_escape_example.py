import json
from lark_oapi.api.bitable.v1 import AppTableRecord

from ..lark_bitable import RecordEncoder
from .product import Product
from ..lark_bitable import parse_bitable_record


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
            }
        )
        .build()
    )

    # 使用新的parse_bitable_record函数，直接接受AppTableRecord
    product = parse_bitable_record(Product, app_table_record)
    print(
        "Product object:",
        json.dumps(product, indent=4, ensure_ascii=False, cls=RecordEncoder),
    )
    print("Record ID from base class:", product.record_id)

    # 使用继承的to_fields方法
    output_data = product.to_fields()
    print(
        "Output data using inherited method:",
        json.dumps(output_data, indent=4, ensure_ascii=False, cls=RecordEncoder),
    )

    # 也可以使用包函数方式
    output_data_func = product.to_fields()
    print("Output data using function:", output_data_func)


if __name__ == "__main__":
    main()
