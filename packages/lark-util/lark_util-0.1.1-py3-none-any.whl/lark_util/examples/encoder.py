"""飞书多维表格数据编码器"""

from decimal import Decimal
import json

from .product import Product


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        # 处理 Product 类型
        if isinstance(obj, Product):
            return obj.__dict__
        # 处理 Decimal 类型
        if isinstance(obj, Decimal):
            return str(obj)
        # 让父类处理其他类型
        return super().default(obj)
