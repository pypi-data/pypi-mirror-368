"""
飞书Wiki工具

基于官方lark-oapi SDK的Wiki功能
"""

import json
import lark_oapi as lark
from lark_oapi.api.wiki.v2 import GetNodeSpaceRequest


"""飞书知识空间工具

基于官方lark-oapi SDK的知识空间功能
"""

import json
import lark_oapi as lark
from lark_oapi.api.wiki.v2 import GetNodeSpaceRequest
from typing import Dict, Any
from ..lark_client import client


def get_space_node(token: str, obj_type: str = "wiki") -> Dict[str, Any]:
    """
    获取知识空间节点信息

    Args:
        token: 知识空间节点token
        obj_type: 对象类型，默认为"wiki"

    Returns:
        Dict[str, Any]: 知识空间节点信息字典

    Raises:
        Exception: 获取节点信息失败时抛出异常
    """
    # 构造请求对象
    request = GetNodeSpaceRequest.builder().token(token).obj_type(obj_type).build()

    # 发起请求
    response = client.wiki.v2.space.get_node(request)

    # 处理失败返回
    if not response.success():
        error_msg = f"获取知识空间节点信息失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
        lark.logger.error(error_msg)
        raise Exception(error_msg)

    # 从raw.content中解析数据
    if response.raw and response.raw.content:
        try:
            response_data = json.loads(response.raw.content.decode("utf-8"))
            return response_data.get("data", {})
        except (json.JSONDecodeError, KeyError) as e:
            error_msg = f"解析响应数据失败: {e}"
            lark.logger.error(error_msg)
            raise Exception(error_msg)
    else:
        raise Exception("响应数据为空")
