from typing import Any, TypeVar

from pydantic import BaseModel

from lark_helper.models.bitable import (
    BitableRecord,
    BitableSearchResponseData,
    BitableViewResponseData,
    FilterCondition,
    SortCondition,
)
from lark_helper.token_manager import TenantAccessTokenManager
from lark_helper.utils.async_request import async_make_lark_request

T = TypeVar("T", bound=BaseModel)


async def async_add_bitable_record(
    token_manager: TenantAccessTokenManager,
    app_token: str,
    table_id: str,
    fields: dict,
) -> dict[str, Any]:
    """
    多维表格-新增记录
    https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/create
    """
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {await token_manager.async_get_tenant_access_token()}",
    }
    payload = {
        "fields": fields,
    }

    return await async_make_lark_request(method="POST", url=url, headers=headers, data=payload)


async def async_update_bitable_record(
    token_manager: TenantAccessTokenManager,
    app_token: str,
    table_id: str,
    record_id: str,
    fields: dict,
) -> dict:
    """
    多维表格-更新记录
    https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/update
    """
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {await token_manager.async_get_tenant_access_token()}",
    }
    payload = {
        "fields": fields,
    }

    return await async_make_lark_request(method="PUT", url=url, headers=headers, data=payload)


async def async_search_bitable_record_page(
    token_manager: TenantAccessTokenManager,
    app_token: str,
    table_id: str,
    view_id: str | None = None,
    field_names: list[str] | None = None,
    sort_conditions: list[SortCondition] | None = None,
    filter_conditions: list[FilterCondition] | None = None,
    conjunction: str = "and",
    page_size: int = 100,
    page_token: str | None = None,
) -> BitableSearchResponseData:
    """
    多维表格-记录-查询记录
    https://open.feishu.cn/document/docs/bitable-v1/app-table-record/search
    """
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/search"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {await token_manager.async_get_tenant_access_token()}",
    }
    payload: dict[str, Any] = {}
    if view_id:
        payload["view_id"] = view_id
    if field_names:
        payload["field_names"] = field_names
    if sort_conditions:
        payload["sort"] = [condition.model_dump() for condition in sort_conditions]
    if filter_conditions:
        payload["filter"] = {
            "conditions": [condition.model_dump() for condition in filter_conditions],
            "conjunction": conjunction,
        }

    params: dict[str, Any] = {"page_size": page_size or 20}
    if page_token:
        params["page_token"] = page_token

    def extract_page_result(data):
        return BitableSearchResponseData.model_validate(data)

    return await async_make_lark_request(
        method="POST",
        url=url,
        headers=headers,
        data=payload,
        params=params,
        data_extractor=extract_page_result,
    )


async def async_search_all_bitable_records(
    token_manager: TenantAccessTokenManager,
    app_token: str,
    table_id: str,
    view_id: str | None = None,
    field_names: list[str] | None = None,
    sort_conditions: list[SortCondition] | None = None,
    filter_conditions: list[FilterCondition] | None = None,
    conjunction: str = "and",
    page_size: int = 100,
    max_size: int | None = None,
) -> list[BitableRecord]:
    """
    查询多维表格记录

    Args:
        app_token: 多维表格应用令牌
        table_id: 表格ID
        filter_conditions: 筛选条件列表
        conjunction: 条件连接方式，"and"或"or"
        page_size: 每页记录数
        model_class: 记录模型类，默认为None，返回原始数据
                    如果为BitableRecord，返回BitableRecord模型
                    如果为其他继承自BaseModel的类，尝试使用from_bitable_record方法构建对象

    Returns:
        根据model_class参数返回不同类型的结果:
        - None: 返回原始Dict列表
        - BitableRecord: 返回BitableRecord模型列表
        - 其他Pydantic模型: 返回该模型的列表(需要实现from_bitable_record方法)
    """
    all_items: list[BitableRecord] = []
    has_more = True
    page_token = None
    while has_more and (max_size is None or len(all_items) < max_size):
        resp_data = await async_search_bitable_record_page(
            token_manager=token_manager,
            app_token=app_token,
            table_id=table_id,
            view_id=view_id,
            field_names=field_names,
            sort_conditions=sort_conditions,
            filter_conditions=filter_conditions,
            conjunction=conjunction,
            page_size=page_size,
            page_token=page_token,
        )
        all_items.extend(resp_data.items)
        has_more = resp_data.has_more
        page_token = resp_data.page_token

    if max_size and len(all_items) > max_size:
        all_items = all_items[:max_size]

    return all_items


async def async_list_bitable_views_page(
    token_manager: TenantAccessTokenManager,
    app_token: str,
    table_id: str,
) -> BitableViewResponseData:
    """
    多维表格-视图-查询视图
    https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-view/list
    """

    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/views"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {await token_manager.async_get_tenant_access_token()}",
    }

    def extract_views_result(data):
        return BitableViewResponseData.model_validate(data)

    return await async_make_lark_request(
        method="GET", url=url, headers=headers, data_extractor=extract_views_result
    )
