import logging
import time

from lark_helper.token_manager import TenantAccessTokenManager
from lark_helper.v1_async.file import (
    async_create_import_task,
    async_get_import_task_result,
    async_upload_media_to_cloud_doc,
)

logger = logging.getLogger(__name__)


async def async_markdown_to_docx(
    token_manager: TenantAccessTokenManager,
    markdown_content: str,
    doc_name: str,
    mount_key: str,
):
    """
    将markdown内容转换为docx文件
    Args:
        token_manager: 租户访问令牌管理器
        markdown_content: markdown内容
        doc_name: 文件名
        mount_key: 挂载点密钥
    """
    file_name = doc_name
    if not file_name.endswith(".md"):
        file_name = file_name + ".md"

    binary_data = markdown_content.encode("utf-8")
    file_token = await async_upload_media_to_cloud_doc(
        token_manager,
        file_data=binary_data,
        file_name=file_name,
        parent_type="ccm_import_open",
        extra='{"obj_type":"docx","file_extension":"md"}',
    )
    ticket = await async_create_import_task(
        token_manager, file_token, file_name.replace(".md", ""), mount_key
    )
    import_task_result = await async_get_import_task_result(token_manager, ticket)
    logger.info(f"ticket: {ticket}, import_task_result: {import_task_result}")
    while import_task_result.job_status in (1, 2):
        time.sleep(1)
        import_task_result = await async_get_import_task_result(token_manager, ticket)
        logger.info(f"ticket: {ticket}, import_task_result: {import_task_result}")
    return import_task_result.url
