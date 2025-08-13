from abc import ABC, abstractmethod
from decimal import Decimal
from enum import Enum
from optparse import Option
import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


class BaseBitableFieldType(ABC):
    @abstractmethod
    def escape_out(self, value: Any) -> Any:
        pass

    @abstractmethod
    def escape_in(self, value: Any) -> Any:
        pass


class TextBitableFieldType(BaseBitableFieldType):
    def escape_out(self, value: str | None) -> Optional[str]:
        if value is None:
            return None
        return value

    def escape_in(self, value: Any | None) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            if len(value) <= 0:
                return ""
            for item in value:
                if not isinstance(item, dict):
                    continue
                return item.get("text", "")
            return ""
        raise ValueError("TextBitableFieldType escape_in value must be str or list")


class StringBitableFieldType(BaseBitableFieldType):
    def escape_out(self, value: str | None) -> Optional[str]:
        if value is None:
            return None
        return value

    def escape_in(self, value: Any | None) -> Optional[str]:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("StringBitableFieldType escape_in value must be str")
        return value


class DateBitableFieldType(BaseBitableFieldType):
    _date_formats = [
        "%Y-%m-%d",  # yyyy-MM-dd
        "%Y-%m-%d %H:%M:%S",  # yyyy-MM-dd HH:mm:ss
        "%Y-%m-%dT%H:%M:%S%z",  # ISO format with timezone
    ]

    def escape_out(self, value: datetime | None) -> Optional[int]:
        if value is None:
            return None

        if isinstance(value, datetime):
            return int(value.timestamp() * 1000)

        raise ValueError(f"DateBitableFieldType escape_out cannot parse date: {value}")

    def escape_in(self, value: Any | None) -> Optional[datetime]:
        if value is None:
            return None
        if not isinstance(value, int):
            raise ValueError("DateBitableFieldType escape_in value must be int")
        return datetime.fromtimestamp(value / 1000)


class UserBitableFieldType(BaseBitableFieldType):
    def escape_out(self, value: str | None) -> Optional[List[Dict[str, str]]]:
        if value is None:
            return None
        return [{"id": str(value)}]

    def escape_in(self, value: Any | None) -> Optional[str]:
        if value is None:
            return None
        if not isinstance(value, list) or len(value) == 0:
            raise ValueError("UserBitableFieldType escape_in value must be list")
        for item in value:
            if not isinstance(item, dict):
                continue
            return item.get("id", "")
        return ""


class IntBitableFieldType(BaseBitableFieldType):
    def escape_out(self, value: int | None) -> Optional[int]:
        if value is None:
            return None
        if not isinstance(value, int):
            raise ValueError("IntBitableFieldType escape_out value must be int")
        return value

    def escape_in(self, value: Any | None) -> Optional[int]:
        if value is None:
            return None
        if not isinstance(value, int):
            raise ValueError("IntBitableFieldType escape_in value must be int")
        return value


class FloatBitableFieldType(BaseBitableFieldType):
    def escape_out(self, value: float | None) -> Optional[float]:
        if value is None:
            return None
        if not isinstance(value, float):
            raise ValueError("FloatBitableFieldType escape_out value must be float")
        return value

    def escape_in(self, value: Any | None) -> Optional[float]:
        if value is None:
            return None
        if not isinstance(value, float):
            raise ValueError("FloatBitableFieldType escape_in value must be float")
        return value


class DecimalBitableFieldType(BaseBitableFieldType):
    def escape_out(self, value: Decimal | None) -> Optional[float]:
        if value is None:
            return None
        if not isinstance(value, Decimal):
            raise ValueError("DecimalBitableFieldType escape_out value must be Decimal")
        return float(value)

    def escape_in(self, value: float | None) -> Optional[Decimal]:
        if value is None:
            return None
        if not isinstance(value, (int, float, str)):
            raise ValueError(
                "DecimalBitableFieldType escape_in value must be number or string"
            )
        try:
            return Decimal(str(value))
        except:
            raise ValueError(
                "DecimalBitableFieldType escape_in value must be valid decimal"
            )


class CheckBoxBitableFieldType(BaseBitableFieldType):
    def escape_out(self, value: bool | None) -> Optional[bool]:
        if value is None:
            return None
        return value

    def escape_in(self, value: Any | None) -> Optional[bool]:
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        raise ValueError("CheckBoxBitableFieldType escape_in value must be bool")


class BitableFieldType(Enum):
    """多维表格字段类型枚举

    TEXT: 文本类型，转出：string -> [{text, type}]，转入：[{text, link, type}] -> string
    STRING: 字符串类型，转出：string -> string，转入：string -> string
    INT: 整数类型，转出：int -> int，转入：int -> int
    FLOAT: 浮点数类型，转出：float -> float，转入：float -> float
    DECIMAL: 高精度数字类型，转出：str -> str，转入：str -> str
    DATE: 日期类型，转出：string -> timestamp_in_ms，转入：timestamp_in_ms -> string
    USER: 用户类型，转出：string -> [{user_id}]，转入：[{user_id}] -> string
    """

    TEXT = TextBitableFieldType()
    STRING = StringBitableFieldType()
    INT = IntBitableFieldType()
    FLOAT = FloatBitableFieldType()
    DECIMAL = DecimalBitableFieldType()
    DATE = DateBitableFieldType()
    USER = UserBitableFieldType()
    CHECKBOX = UserBitableFieldType()
