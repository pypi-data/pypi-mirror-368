import asyncio
import logging
import time

from lark_helper.constants.message import MessageType, ReceiveIdType
from lark_helper.models.message import MessageContent
from lark_helper.token_manager import TenantAccessTokenManager
from lark_helper.utils.async_request import async_make_lark_request
from lark_helper.utils.decorator import simple_timing

logger = logging.getLogger(__name__)


@simple_timing
async def async_send_message(
    token_manager: TenantAccessTokenManager,
    receive_id: str,
    receive_id_type: ReceiveIdType,
    message_type: MessageType,
    content: str,
) -> str:
    """
    发送消息
    https://open.feishu.cn/document/server-docs/im-v1/message/create
    发送消息内容结构
    https://open.feishu.cn/document/server-docs/im-v1/message-content-description/create_json
    """
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={receive_id_type.value}"
    logger.info(f"发送消息: {url}")
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {await token_manager.async_get_tenant_access_token()}",
    }
    payload = {
        "receive_id": receive_id,
        "msg_type": message_type.value,
        "content": content,
    }

    def extract_message_id(data):
        return data.get("message_id")

    return await async_make_lark_request(
        method="POST",
        url=url,
        headers=headers,
        data=payload,
        data_extractor=extract_message_id,
    )


@simple_timing
async def async_reply_message(
    token_manager: TenantAccessTokenManager,
    message_id: str,
    content: MessageContent,
) -> str:
    """
    回复消息
    https://open.feishu.cn/document/server-docs/im-v1/message/reply
    发送消息内容结构
    https://open.feishu.cn/document/server-docs/im-v1/message-content-description/create_json
    """
    url = f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/reply"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {await token_manager.async_get_tenant_access_token()}",
    }
    payload = {
        "content": content.json_str(),
        "msg_type": content.message_type.value,
    }

    def extract_message_id(data):
        return data.get("message_id")

    return await async_make_lark_request(
        method="POST",
        url=url,
        headers=headers,
        data=payload,
        data_extractor=extract_message_id,
    )


@simple_timing
async def async_update_msg(
    token_manager: TenantAccessTokenManager,
    message_id: str,
    content: MessageContent,
) -> dict:
    """
    更新应用发送的消息卡片
    https://open.feishu.cn/document/server-docs/im-v1/message-card/patch

    单条消息更新频控为 5 QPS
    """
    url = f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {await token_manager.async_get_tenant_access_token()}",
    }
    payload = {
        "content": content.json_str(),
    }
    return await async_make_lark_request(
        method="PATCH",
        url=url,
        headers=headers,
        data=payload,
    )


# 消息卡片更新限速器（优化版）
MESSAGE_UPDATE_INTERVAL = 0.21  # 秒
message_locks: dict[str, asyncio.Lock] = {}  # 存储每个消息的锁
message_update_timestamps: dict[str, float] = {}


def can_async_update_message(message_id: str) -> bool:
    """
    检查指定的 message_id 在当前限速规则下是否可以立即更新消息。

    Args:
        message_id: 要检查的消息ID

    Returns:
        bool: True 表示可以立即更新，False 表示需要等待
    """
    last_update_time = message_update_timestamps.get(message_id, 0)
    current_time = time.monotonic()
    elapsed_time = current_time - last_update_time

    return elapsed_time >= MESSAGE_UPDATE_INTERVAL


async def async_rate_limited_update_msg(
    token_manager: TenantAccessTokenManager,
    message_id: str,
    content: MessageContent,
) -> dict:
    """
    带有限速功能的消息更新函数（优化版）。
    为每个不同的 message_id 使用独立的锁，确保不同消息之间不会互相阻塞。
    对于单条消息，确保更新间隔至少为 MESSAGE_UPDATE_INTERVAL 秒。
    """
    # 获取或创建该消息的专用锁
    lock = message_locks.get(message_id)
    if lock is None:
        lock = asyncio.Lock()
        message_locks[message_id] = lock

    # 仅对单个消息ID加锁，不影响其他消息
    async with lock:
        last_update_time = message_update_timestamps.get(message_id, 0.0)
        current_time = time.monotonic()

        elapsed_time = current_time - last_update_time

        if elapsed_time < MESSAGE_UPDATE_INTERVAL:
            wait_time = MESSAGE_UPDATE_INTERVAL - elapsed_time
            logger.debug(f"消息 {message_id} 触发限速。等待 {wait_time:.3f} 秒。")
            await asyncio.sleep(wait_time)

        # 更新时间戳
        message_update_timestamps[message_id] = time.monotonic()

        # 清除过期数据
        current_time = time.monotonic()
        message_ids_to_remove = [
            msg_id
            for msg_id, value in message_update_timestamps.items()
            if value < current_time - MESSAGE_UPDATE_INTERVAL * 10  # 设置更长的过期时间
        ]
        for msg_id in message_ids_to_remove:
            message_update_timestamps.pop(msg_id, None)
            message_locks.pop(msg_id, None)  # 同时清理锁对象

    # 锁释放后执行API调用，避免在API调用期间持有锁
    logger.info(f"更新消息 {message_id} 的内容。")
    result = await async_update_msg(token_manager, message_id, content)
    logger.info(f"消息 {message_id} 更新成功。")
    return result
