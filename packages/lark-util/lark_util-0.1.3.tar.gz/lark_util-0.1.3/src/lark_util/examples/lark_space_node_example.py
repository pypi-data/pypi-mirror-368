"""飞书知识空间示例

展示如何使用lark_space模块中的函数：
1. 获取不同类型的知识空间节点信息
2. 展示节点的完整结构
3. 包含错误处理示例
"""

import logging
import lark_oapi as lark
from ..lark_space import get_space_node

# 设置lark-oapi日志级别为INFO
lark.logger.setLevel(logging.INFO)


def main():
    # 示例参数
    space_id = "7199901682757066756"
    wiki_token = "wikcnMhxxx1GWUkQWvhqNXtLvqg"
    doc_token = "doxcnXXXXXXXXXXXXXXXX"

    try:
        # 示例1: 获取Wiki类型的节点
        print("\n示例1: 获取Wiki类型的节点信息")
        wiki_node = get_space_node(token=wiki_token, obj_type="wiki")

        # 打印节点信息
        print("节点信息:")
        print("完整的节点结构:")
        print(lark.JSON.marshal(wiki_node, indent=2))

        # 示例2: 获取Doc类型的节点
        print("\n示例2: 获取Doc类型的节点信息")
        try:
            doc_node = get_space_node(token=doc_token, obj_type="doc")
            print("节点信息:")
            print("完整的节点结构:")
            print(lark.JSON.marshal(doc_node, indent=2))
        except Exception as e:
            print("预期的错误处理:")
            print(f"  错误信息: {e}")

        # 示例3: 使用无效的参数（展示错误处理）
        print("\n示例3: 使用无效的参数（错误处理示例）")
        invalid_token = "invalid_token"

        try:
            invalid_node = get_space_node(token=invalid_token, obj_type="wiki")
            print("节点信息:")
            print(lark.JSON.marshal(invalid_node, indent=2))
        except Exception as e:
            print("预期的错误处理:")
            print(f"  错误信息: {e}")

    except Exception as e:
        print(f"\n执行示例时出错: {e}")
        print("请检查token是否正确配置，以及是否具有相应的访问权限")


if __name__ == "__main__":
    main()
