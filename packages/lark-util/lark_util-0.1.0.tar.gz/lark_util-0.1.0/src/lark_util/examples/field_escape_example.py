import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent.parent))

from .product import Product
from ..lark_bitable import convert_in, convert_out


INPUT_DATA = {
    "product_id": 12345,
    "product_name": [
        {"text": "测试商品", "type": "text", "link": "https://www.baidu.com"}
    ],
    "affiliate_commission": 0.12,
    "retail_price": 20.23,
    "shop_code": "BZ-BTB",
}


def main():
    # 转换输入数据为 Product 对象
    product = convert_in(Product, INPUT_DATA)
    print("Product object:", product)

    # 转换 Product 对象为输出数据
    output_data = convert_out(product)
    print("Output data:", output_data)


if __name__ == "__main__":
    main()
