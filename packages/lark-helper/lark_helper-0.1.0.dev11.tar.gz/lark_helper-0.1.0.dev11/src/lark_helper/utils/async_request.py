"""
Async HTTP request utilities for lark_helper.

This module provides asynchronous versions of the request utilities in request.py,
using aiohttp for HTTP requests instead of requests.
"""

import json
import logging
from collections.abc import Callable
from typing import Any

import aiohttp

from lark_helper.exception import LarkResponseError

logger = logging.getLogger(__name__)


async def async_handle_lark_response[T](
    response: aiohttp.ClientResponse,
    data_extractor: Callable[[dict[str, Any]], T] | None = None,
    use_root_response: bool = False,
) -> T:
    """
    处理来自飞书 API 的响应

    Args:
        response: aiohttp 响应对象
        data_extractor: 可选的用于从响应数据中提取所需结果的函数
        use_root_response: 是否将提取器应用到整个响应对象而不仅是 data 字段

    Returns:
        根据 data_extractor 处理后的数据或原始响应数据

    Raises:
        LarkResponseError: 当响应状态码不为 200 或响应体中 code 不为 0 时
    """
    if response.status != 200:
        response_text = await response.text()
        logger.error(f"飞书 API 请求失败: HTTP {response.status}, {response_text}")
        raise LarkResponseError(f"HTTP 错误: {response.status}, {response_text}")

    result = await response.json()

    if result.get("code") != 0:
        error_msg = result.get("msg", "未知错误")
        error = result.get("error")
        if error and isinstance(error, dict) and "message" in error:
            error_msg = str(error["message"])
        logger.error(f"飞书 API 请求失败: {error_msg}")
        raise LarkResponseError(f"错误: {error_msg}")

    # 根据 use_root_response 决定应用提取器的对象
    data = result
    if not use_root_response:
        data = result.get("data")

    # 如果没有提供数据提取器，则返回完整的 data 部分
    if data_extractor is None:
        return data

    return data_extractor(data)


async def async_make_lark_request[T](
    method: str,
    url: str,
    headers: dict[str, str],
    data: dict[str, Any] | None = None,
    form_data: aiohttp.FormData | None = None,
    params: dict[str, Any] | None = None,
    data_extractor: Callable[[dict[str, Any]], T] | None = None,
    log_payload: bool = True,
    use_root_response: bool = False,
) -> T:
    """
    Make an async HTTP request to the Lark API.

    Args:
        method: HTTP method (GET, POST, etc.)
        url: URL to request
        headers: HTTP headers
        data: JSON data to send
        form_data: Form data to send
        params: URL parameters
        data_extractor: Function to extract data from response
        log_payload: Whether to log the request payload
        use_root_response: Whether to use the root response instead of the data field

    Returns:
        Response data

    Raises:
        LarkResponseError: If the response contains an error
    """
    if log_payload:
        if data and method.upper() != "GET":
            logger.debug(f"Request payload: {json.dumps(data)}")
        elif form_data:
            logger.debug("Request form data payload")

    request_kwargs: dict[str, Any] = {"headers": headers}
    if params:
        request_kwargs["params"] = params
    if data:
        request_kwargs["json"] = data
    elif form_data:
        request_kwargs["data"] = form_data

    async with aiohttp.ClientSession() as session:
        request_method = getattr(session, method.lower())
        async with request_method(url, **request_kwargs) as response:
            return await async_handle_lark_response(
                response, data_extractor=data_extractor, use_root_response=use_root_response
            )
