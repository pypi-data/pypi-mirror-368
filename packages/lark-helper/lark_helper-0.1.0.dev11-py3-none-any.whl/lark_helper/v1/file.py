import json
import logging

import lark_oapi as lark
import requests
from lark_oapi.api.drive.v1 import (
    CreateExportTaskRequest,
    CreateExportTaskResponse,
    DownloadExportTaskRequest,
    DownloadExportTaskResponse,
    ExportTask,
    GetExportTaskRequest,
    GetExportTaskResponse,
)

from lark_helper.constants.file import (
    EXPORT_TASK_JOB_STATUS_ERROR_MAP,
    IMPORT_TASK_JOB_STATUS_ERROR_MAP,
)
from lark_helper.exception import ExportTaskError, ImportTaskError
from lark_helper.models.file import ImportTaskResult, TmpDownloadUrl
from lark_helper.token_manager import TenantAccessTokenManager
from lark_helper.utils.request import make_lark_request

logger = logging.getLogger(__name__)


def get_message_resource(
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
        "Authorization": f"Bearer {token_manager.get_tenant_access_token()}",
    }
    params = {"type": type_}

    # 特殊处理二进制数据返回
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"HTTP Error: {response.status_code} {response.text}")
    return response.content


def upload_media_to_cloud_doc(
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

    headers = {"Authorization": f"Bearer {token_manager.get_tenant_access_token()}"}

    # 准备表单数据
    form_data = {
        "file_name": file_name,
        "parent_type": parent_type,
        "size": str(len(file_data)),
        "file": file_data,
    }
    if parent_node:
        form_data["parent_node"] = parent_node
    if extra:
        form_data["extra"] = extra

    def extract_file_token(data):
        return data.get("file_token")

    return make_lark_request(
        method="POST",
        url=url,
        headers=headers,
        form_data=form_data,
        data_extractor=extract_file_token,
    )


def download_media_from_cloud_doc(
    token_manager: TenantAccessTokenManager,
    file_token: str,
) -> bytes:
    """
    下载素材，下载各类云文档中的素材，例如电子表格中的图片。
    https://open.feishu.cn/document/server-docs/docs/drive-v1/media/download
    """
    url = f"https://open.feishu.cn/open-apis/drive/v1/medias/{file_token}/download"
    headers = {
        "Authorization": f"Bearer {token_manager.get_tenant_access_token()}",
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"HTTP Error: {response.status_code} {response.text}")
    return response.content


def upload_image(
    token_manager: TenantAccessTokenManager,
    image_binary_data: bytes,
    image_type: str = "message",
) -> str:
    """
    上传图片到飞书
    https://open.feishu.cn/document/server-docs/im-v1/image/create
    """
    url = "https://open.feishu.cn/open-apis/im/v1/images"
    token = token_manager.get_tenant_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
    }

    form_data = {
        "image_type": image_type,
        "image": image_binary_data,
    }

    def extract_image_key(data):
        return data.get("image_key")

    return make_lark_request(
        method="POST",
        url=url,
        headers=headers,
        form_data=form_data,
        data_extractor=extract_image_key,
    )


def create_import_task(
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
        "Authorization": f"Bearer {token_manager.get_tenant_access_token()}",
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

    return make_lark_request(
        method="POST",
        url=url,
        headers=headers,
        data=payload,
        data_extractor=extract_ticket,
    )


def get_import_task_result(
    token_manager: TenantAccessTokenManager,
    ticket: str,
) -> ImportTaskResult:
    """
    获取导入任务结果
    https://open.feishu.cn/document/server-docs/docs/drive-v1/import_task/get
    """
    url = f"https://open.feishu.cn/open-apis/drive/v1/import_tasks/{ticket}"
    headers = {
        "Authorization": f"Bearer {token_manager.get_tenant_access_token()}",
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

    return make_lark_request(method="GET", url=url, headers=headers, data_extractor=extract_result)


def batch_get_tmp_download_url(
    token_manager: TenantAccessTokenManager, file_tokens: list[str]
) -> list[TmpDownloadUrl]:
    url = "https://open.feishu.cn/open-apis/drive/v1/medias/batch_get_tmp_download_url"
    params = {
        "file_tokens": file_tokens,
    }
    headers = {
        "Authorization": f"Bearer {token_manager.get_tenant_access_token()}",
    }

    def extract_url(data) -> list[TmpDownloadUrl]:
        return [TmpDownloadUrl.model_validate(item) for item in data.get("tmp_download_urls")]

    return make_lark_request(
        method="GET",
        url=url,
        headers=headers,
        params=params,
        data_extractor=extract_url,
    )


def create_export_task(
    token_manager: TenantAccessTokenManager,
    file_token: str,
    file_type: str,
    type_: str = "pdf",
) -> str:
    """
    创建导出任务
    https://open.feishu.cn/document/server-docs/docs/drive-v1/export_task/create

    Args:
        file_token: 源云文档token
        file_type: 云文档类型，如"docx", "sheet", "bitable"等
        type_: 导出类型，如"pdf", "docx", "xlsx", "csv"等

    Returns:
        导出任务ticket
    """
    # 创建client
    client = (
        lark.Client.builder()
        .app_id(token_manager.app_id)
        .app_secret(token_manager.app_secret)
        .log_level(lark.LogLevel.INFO)
        .build()
    )

    # 构造请求对象
    request: CreateExportTaskRequest = (
        CreateExportTaskRequest.builder()
        .file_extension(file_type)
        .token(file_token)
        .type(type_)
        .build()
    )

    # 发起请求
    response: CreateExportTaskResponse = client.drive.v1.export_task.create(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.drive.v1.export_task.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}"
        )
        raise Exception(f"创建导出任务失败: {response.msg}")

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))
    return response.data.ticket


def get_export_task_result(
    token_manager: TenantAccessTokenManager,
    ticket: str,
) -> ExportTask:
    """
    查询导出任务结果
    https://open.feishu.cn/document/server-docs/docs/drive-v1/export_task/get

    Args:
        ticket: 导出任务ticket

    Returns:
        导出任务结果
    """
    # 创建client
    client = (
        lark.Client.builder()
        .app_id(token_manager.app_id)
        .app_secret(token_manager.app_secret)
        .log_level(lark.LogLevel.INFO)
        .build()
    )

    # 构造请求对象
    request: GetExportTaskRequest = GetExportTaskRequest.builder().ticket(ticket).build()

    # 发起请求
    response: GetExportTaskResponse = client.drive.v1.export_task.get(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.drive.v1.export_task.get failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}"
        )
        raise Exception(f"查询导出任务失败: {response.msg}")

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))

    # 构建返回结果
    export_task_result: ExportTask = response.data.result

    if export_task_result.job_status in EXPORT_TASK_JOB_STATUS_ERROR_MAP:
        logger.error(
            f"导出任务失败: {export_task_result.job_status}, {EXPORT_TASK_JOB_STATUS_ERROR_MAP[export_task_result.job_status]}"
        )
        raise ExportTaskError(
            export_task_result.job_status,
            EXPORT_TASK_JOB_STATUS_ERROR_MAP[export_task_result.job_status],
        )

    return export_task_result


def download_export_file(
    token_manager: TenantAccessTokenManager,
    file_token: str,
) -> bytes:
    """
    下载导出文件
    https://open.feishu.cn/document/server-docs/docs/drive-v1/export_task/download

    Args:
        file_token: 导出文件token

    Returns:
        文件二进制数据
    """
    # 创建client
    client = (
        lark.Client.builder()
        .app_id(token_manager.app_id)
        .app_secret(token_manager.app_secret)
        .log_level(lark.LogLevel.INFO)
        .build()
    )

    # 构造请求对象
    request: DownloadExportTaskRequest = (
        DownloadExportTaskRequest.builder().file_token(file_token).build()
    )

    # 发起请求
    response: DownloadExportTaskResponse = client.drive.v1.export_task.download(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.drive.v1.export_task.download failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
        )
        raise Exception(f"下载导出文件失败: {response.msg}")

    # 处理业务结果 - 返回二进制数据
    return response.raw.content
