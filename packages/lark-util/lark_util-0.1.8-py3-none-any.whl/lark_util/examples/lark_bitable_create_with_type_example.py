"""飞书多维表格创建记录示例（支持类型转换）"""

from ..lark_bitable import create_bitable_record_with_type
from .product import Product


def main():
    # 多维表格应用token
    app_token = "AXYab8AxaaMHWSsr8qmczS3hnWA"
    # 表格ID
    table_id = "tblOAOp3VcTHABV3"

    # 创建业务对象
    product = Product(
        product_id=12345,
        product_name="测试商品",
        affiliate_commission_percent=0.12,
        shop_code="BZ-BTB",
    )

    # 创建记录
    try:
        record_id = create_bitable_record_with_type(app_token, table_id, product)
        print(f"创建记录成功，记录ID: {record_id}")
    except Exception as e:
        print(f"创建记录失败: {e}")


if __name__ == "__main__":
    main()
