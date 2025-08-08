import logging

from lark_helper.constants.message import MessageType, ReceiveIdType
from lark_helper.models.message import MessageContent
from lark_helper.token_manager import TenantAccessTokenManager
from lark_helper.utils.decorator import simple_timing
from lark_helper.utils.request import make_lark_request

logger = logging.getLogger(__name__)


@simple_timing
def send_message(
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
        "Authorization": f"Bearer {token_manager.get_tenant_access_token()}",
    }
    payload = {
        "receive_id": receive_id,
        "msg_type": message_type.value,
        "content": content,
    }

    def extract_message_id(data):
        return data.get("message_id")

    return make_lark_request(
        method="POST",
        url=url,
        headers=headers,
        data=payload,
        data_extractor=extract_message_id,
    )


@simple_timing
def reply_message(
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
        "Authorization": f"Bearer {token_manager.get_tenant_access_token()}",
    }
    payload = {
        "content": content.json_str(),
        "msg_type": content.message_type.value,
    }

    def extract_message_id(data):
        return data.get("message_id")

    return make_lark_request(
        method="POST",
        url=url,
        headers=headers,
        data=payload,
        data_extractor=extract_message_id,
    )


@simple_timing
def update_msg(
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
        "Authorization": f"Bearer {token_manager.get_tenant_access_token()}",
    }
    payload = {
        "content": content.json_str(),
    }
    return make_lark_request(
        method="PATCH",
        url=url,
        headers=headers,
        data=payload,
    )
