import logging

import aiohttp

from lark_helper.constants.file import IMPORT_TASK_JOB_STATUS_ERROR_MAP
from lark_helper.exception import ImportTaskError
from lark_helper.models.file import ImportTaskResult, TmpDownloadUrl
from lark_helper.token_manager import TenantAccessTokenManager
from lark_helper.utils.async_request import async_make_lark_request

logger = logging.getLogger(__name__)


async def async_get_message_resource(
    token_manager: TenantAccessTokenManager,
    message_id: str,
    file_key: str,
    type_: str,
) -> bytes:
    """
    获取消息中的资源文件
    https://open.feishu.cn/document/server-docs/im-v1/message/get-2
    """
    url = f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/resources/{file_key}"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {await token_manager.async_get_tenant_access_token()}",
    }
    params = {"type": type_}

    # 特殊处理二进制数据返回
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                return await response.read()
            else:
                raise Exception(f"HTTP Error: {response.status} {await response.text()}")


async def async_upload_media_to_cloud_doc(
    token_manager: TenantAccessTokenManager,
    file_data: bytes,
    file_name: str,
    parent_type: str,
    parent_node: str | None = None,
    extra: str | None = None,
) -> str:
    """上传素材
    https://open.feishu.cn/document/server-docs/docs/drive-v1/media/upload_all
    素材概述
    https://open.feishu.cn/document/server-docs/docs/drive-v1/media/introduction

    Args:
        file_data: 文件二进制数据
        file_name: 上传后的文件名称，默认使用原文件名
        parent_type: 上传点的类型，默认为bitable_image
        parent_node: 父节点ID，上传点的类型为 ccm_import_open 时不必填

    Returns:
        上传后的文件token
    """
    url = "https://open.feishu.cn/open-apis/drive/v1/medias/upload_all"

    headers = {"Authorization": f"Bearer {await token_manager.async_get_tenant_access_token()}"}
    # 准备表单数据
    form_data = aiohttp.FormData()
    form_data.add_field("file_name", file_name)
    form_data.add_field("parent_type", parent_type)
    if parent_node:
        form_data.add_field("parent_node", parent_node)
    form_data.add_field("size", str(len(file_data)))
    form_data.add_field(
        "file", file_data, filename=file_name, content_type="application/octet-stream"
    )
    if extra:
        form_data.add_field("extra", extra)

    def extract_file_token(data):
        return data.get("file_token")

    return await async_make_lark_request(
        method="POST",
        url=url,
        headers=headers,
        form_data=form_data,
        data_extractor=extract_file_token,
    )


async def async_download_media_from_cloud_doc(
    token_manager: TenantAccessTokenManager,
    file_token: str,
) -> bytes:
    """
    下载素材，下载各类云文档中的素材，例如电子表格中的图片。
    https://open.feishu.cn/document/server-docs/docs/drive-v1/media/download
    """
    url = f"https://open.feishu.cn/open-apis/drive/v1/medias/{file_token}/download"
    headers = {
        "Authorization": f"Bearer {await token_manager.async_get_tenant_access_token()}",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.read()
            else:
                raise Exception(f"HTTP Error: {response.status} {await response.text()}")


async def async_upload_image(
    token_manager: TenantAccessTokenManager,
    image_binary_data: bytes,
    image_type: str = "message",
) -> str:
    """
    上传图片到飞书
    https://open.feishu.cn/document/server-docs/im-v1/image/create
    """
    url = "https://open.feishu.cn/open-apis/im/v1/images"
    headers = {
        "Authorization": f"Bearer {await token_manager.async_get_tenant_access_token()}",
    }

    # form_data = {
    #     "image_type": image_type,
    #     "image": image_binary_data,
    # }
    form_data = aiohttp.FormData()
    form_data.add_field("image", image_binary_data)
    form_data.add_field("image_type", image_type)

    def extract_image_key(data):
        return data.get("image_key")

    return await async_make_lark_request(
        method="POST",
        url=url,
        headers=headers,
        form_data=form_data,
        data_extractor=extract_image_key,
    )


async def async_create_import_task(
    token_manager: TenantAccessTokenManager,
    file_token: str,
    file_name: str,
    mount_key: str,
) -> str:
    """
    创建导入任务
    https://open.feishu.cn/document/server-docs/docs/drive-v1/import_task/create

    Args:
        mount_key: 挂载点key
    """
    url = "https://open.feishu.cn/open-apis/drive/v1/import_tasks"
    headers = {
        "Authorization": f"Bearer {await token_manager.async_get_tenant_access_token()}",
    }
    payload = {
        "file_extension": "md",
        "file_name": file_name,
        "file_token": file_token,
        "point": {"mount_key": mount_key, "mount_type": 1},
        "type": "docx",
    }

    def extract_ticket(data):
        return data.get("ticket")

    return await async_make_lark_request(
        method="POST",
        url=url,
        headers=headers,
        data=payload,
        data_extractor=extract_ticket,
    )


async def async_get_import_task_result(
    token_manager: TenantAccessTokenManager,
    ticket: str,
) -> ImportTaskResult:
    """
    获取导入任务结果
    https://open.feishu.cn/document/server-docs/docs/drive-v1/import_task/get
    """
    url = f"https://open.feishu.cn/open-apis/drive/v1/import_tasks/{ticket}"
    headers = {
        "Authorization": f"Bearer {await token_manager.async_get_tenant_access_token()}",
    }

    def extract_result(data):
        result = data.get("result")
        import_task_result = ImportTaskResult(**result)
        if import_task_result.job_status in IMPORT_TASK_JOB_STATUS_ERROR_MAP:
            logger.error(
                f"导入任务失败: {import_task_result.job_status}, {IMPORT_TASK_JOB_STATUS_ERROR_MAP[import_task_result.job_status]}"
            )
            raise ImportTaskError(
                import_task_result.job_status,
                IMPORT_TASK_JOB_STATUS_ERROR_MAP[import_task_result.job_status],
            )

        return import_task_result

    return await async_make_lark_request(
        method="GET", url=url, headers=headers, data_extractor=extract_result
    )


async def async_batch_get_tmp_download_url(
    token_manager: TenantAccessTokenManager, file_tokens: list[str]
) -> list[TmpDownloadUrl]:
    url = "https://open.feishu.cn/open-apis/drive/v1/medias/batch_get_tmp_download_url"
    params = {
        "file_tokens": file_tokens,
    }
    headers = {
        "Authorization": f"Bearer {await token_manager.async_get_tenant_access_token()}",
    }

    def extract_url(data) -> list[TmpDownloadUrl]:
        return [TmpDownloadUrl.model_validate(item) for item in data.get("tmp_download_urls")]

    return await async_make_lark_request(
        method="GET",
        url=url,
        headers=headers,
        params=params,
        data_extractor=extract_url,
    )
