import json
import logging
from collections.abc import Callable
from typing import Any

import requests
from requests_toolbelt import MultipartEncoder  # type: ignore[import-untyped]

from lark_helper.exception import LarkResponseError

logger = logging.getLogger(__name__)


def handle_lark_response[T](
    response: requests.Response,
    data_extractor: Callable[[dict[str, Any]], T] | None = None,
    use_root_response: bool = False,
) -> T:
    """
    处理来自飞书 API 的响应

    Args:
        response: requests 响应对象
        data_extractor: 可选的用于从响应数据中提取所需结果的函数
        use_root_response: 是否将提取器应用到整个响应对象而不仅是 data 字段

    Returns:
        根据 data_extractor 处理后的数据或原始响应数据

    Raises:
        LarkResponseError: 当响应状态码不为 200 或响应体中 code 不为 0 时
    """
    if response.status_code != 200:
        response_text = response.text
        logger.error(f"飞书 API 请求失败: HTTP {response.status_code}, {response_text}")
        raise LarkResponseError(f"HTTP 错误: {response.status_code}, {response_text}")

    result = response.json()

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


def make_lark_request[T](
    method: str,
    url: str,
    headers: dict[str, str],
    data: dict[str, Any] | None = None,
    form_data: dict[str, Any] | MultipartEncoder | None = None,
    params: dict[str, Any] | None = None,
    data_extractor: Callable[[dict[str, Any]], T] | None = None,
    log_payload: bool = True,
    use_root_response: bool = False,
) -> T:
    """
    向飞书 API 发送请求并处理响应

    Args:
        method: 请求方法 ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')
        url: 请求 URL
        headers: 请求头
        data: 请求体数据（JSON 格式）
        files: 文件上传数据
        params: URL 参数
        data_extractor: 用于从响应中提取数据的函数
        log_payload: 是否记录请求数据
        use_root_response: 是否将提取器应用到整个响应对象而不仅是 data 字段

    Returns:
        API 响应的处理结果
    """
    if log_payload and data and method.upper() != "GET":
        logger.info(f"请求数据: {json.dumps(data, ensure_ascii=False)}")
    elif log_payload and form_data and isinstance(form_data, dict):
        if "file" in form_data:
            logger.info("正在发送文件数据")
        else:
            logger.info(f"请求数据: {json.dumps(form_data, ensure_ascii=False)}")

    request_kwargs: dict[str, Any] = {"headers": headers}
    if params:
        request_kwargs["params"] = params
    if data:
        request_kwargs["json"] = data
    elif form_data:
        if isinstance(form_data, dict):
            form_data = MultipartEncoder(form_data)
        elif not isinstance(form_data, MultipartEncoder):
            raise ValueError("form_data must be a dict or MultipartEncoder")
        request_kwargs["data"] = form_data
        # 此时 form_data 已经确保是 MultipartEncoder 类型
        assert isinstance(form_data, MultipartEncoder)
        headers["Content-Type"] = str(form_data.content_type)

    response = requests.request(method, url, **request_kwargs)
    return handle_lark_response(response, data_extractor, use_root_response)
