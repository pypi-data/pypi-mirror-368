import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class FilterCondition(BaseModel):
    """
    多维表格-记录-筛选参数填写说明
    https://open.feishu.cn/document/docs/bitable-v1/app-table-record/record-filter-guide
    """

    field_name: str | None = None
    operator: str | None = None
    value: list | None = None

    @classmethod
    def is_equal(cls, field_name: str, value: list):
        # 等于
        return cls(field_name=field_name, operator="is", value=value)

    @classmethod
    def is_not(cls, field_name: str, value: list):
        # 不等于（不支持日期字段）
        return cls(field_name=field_name, operator="isNot", value=value)

    @classmethod
    def contains(cls, field_name: str, value: list):
        # 包含（不支持日期字段）
        return cls(field_name=field_name, operator="contains", value=value)

    @classmethod
    def does_not_contain(cls, field_name: str, value: list):
        # 不包含（不支持日期字段）
        return cls(field_name=field_name, operator="doesNotContain", value=value)

    @classmethod
    def is_empty(cls, field_name: str):
        # 为空
        return cls(field_name=field_name, operator="isEmpty", value=[])

    @classmethod
    def is_not_empty(cls, field_name: str):
        # 不为空
        return cls(field_name=field_name, operator="isNotEmpty", value=[])

    @classmethod
    def is_greater(cls, field_name: str, value: list):
        # 大于
        return cls(field_name=field_name, operator="isGreater", value=value)

    @classmethod
    def is_greater_equal(cls, field_name: str, value: list):
        # 大于等于（不支持日期字段）
        return cls(field_name=field_name, operator="isGreaterEqual", value=value)

    @classmethod
    def is_less(cls, field_name: str, value: list):
        # 小于
        return cls(field_name=field_name, operator="isLess", value=value)

    @classmethod
    def is_less_equal(cls, field_name: str, value: list):
        # 小于等于（不支持日期字段）
        return cls(field_name=field_name, operator="isLessEqual", value=value)

    def is_null(self):
        return not self.field_name and not self.operator and not self.value


class SortCondition(BaseModel):
    """
    多维表格-记录-排序参数填写说明
    """

    field_name: str | None = None
    desc: bool | None = False


class BitableRecord(BaseModel):
    """飞书多维表格记录模型"""

    record_id: str
    fields: dict[str, Any]

    def to_hiagent_plugin_compatible(self):
        return {
            "record_id": self.record_id,
            "fields": json.dumps(self.fields, ensure_ascii=False),
        }

    def get_text_field(self, field_name: str) -> str | None:
        """获取文本类型字段值"""
        value = self.fields.get(field_name)
        if not value:
            return None
        if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
            return value[0].get("text")
        return None

    def get_number_field(self, field_name: str) -> float | None:
        """获取数字类型字段值"""
        value = self.fields.get(field_name)
        if value is None:
            return None
        return float(value)

    def get_date_field(self, field_name: str, date_format: str = "%Y-%m-%d") -> str | None:
        """获取日期类型字段值"""
        timestamp = self.fields.get(field_name)
        if not timestamp:
            return None
        # 飞书返回的时间戳是毫秒级
        return datetime.fromtimestamp(timestamp / 1000).strftime(date_format)

    def get_select_field(self, field_name: str) -> str | None:
        """获取单选类型字段值"""
        return self.fields.get(field_name)


class BitableSearchResponseData(BaseModel):
    has_more: bool
    page_token: str | None = None
    total: int
    items: list[BitableRecord]

    def to_hiagent_plugin_compatible(self):
        return {
            "has_more": self.has_more,
            "page_token": self.page_token,
            "total": self.total,
            "items": [item.to_hiagent_plugin_compatible() for item in self.items],
        }


class BitableResponse(BaseModel):
    """飞书多维表格响应模型"""

    records: list[BitableRecord]

    @classmethod
    def from_response(cls, response: list[dict[str, Any]]) -> "BitableResponse":
        """从API响应创建响应模型"""
        return cls(
            records=[
                BitableRecord(record_id=item.get("record_id", ""), fields=item.get("fields", {}))
                for item in response
            ]
        )


class BitableView(BaseModel):
    view_id: str
    view_name: str
    view_public_level: str
    view_type: str
    view_private_owner_id: str | None = None


class BitableViewResponseData(BaseModel):
    items: list[BitableView]
    page_token: str | None = None
    has_more: bool
    total: int
