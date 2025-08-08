import json

import lark_oapi as lark
from lark_oapi.api.docx.v1 import GetDocumentRequest, GetDocumentResponse
from lark_oapi.api.drive.v1 import (
    BatchQueryMetaRequest,
    BatchQueryMetaResponse,
    MetaRequest,
    RequestDoc,
)
from lark_oapi.api.wiki.v2 import GetNodeSpaceRequest, GetNodeSpaceResponse, Node

from lark_helper.token_manager import TenantAccessTokenManager


class DocType:
    DOC = "doc"
    DOCX = "docx"
    SHEET = "sheet"
    MINDNOTE = "mindnote"
    BITABLE = "bitable"
    WIKI = "wiki"
    FILE = "file"
    SLIDES = "slides"


def get_node_space(
    token_manager: TenantAccessTokenManager, doc_type: str, token: str
) -> Node | None:
    # 创建client
    client = (
        lark.Client.builder()
        .app_id(token_manager.app_id)
        .app_secret(token_manager.app_secret)
        .log_level(lark.LogLevel.INFO)
        .build()
    )

    # 构造请求对象
    request: GetNodeSpaceRequest = (
        GetNodeSpaceRequest.builder().token(token).obj_type(doc_type).build()
    )

    # 发起请求
    response: GetNodeSpaceResponse = client.wiki.v2.space.get_node(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.wiki.v2.space.get_node failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}"
        )
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))
    return response.data.node


# SDK 使用说明: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/preparations-before-development
# 以下示例代码默认根据文档示例值填充，如果存在代码问题，请在 API 调试台填上相关必要参数后再复制代码使用
# 复制该 Demo 后, 需要将 "YOUR_APP_ID", "YOUR_APP_SECRET" 替换为自己应用的 APP_ID, APP_SECRET.
def get_document(token_manager: TenantAccessTokenManager, document_id: str) -> dict:
    # 创建client
    client = (
        lark.Client.builder()
        .app_id(token_manager.app_id)
        .app_secret(token_manager.app_secret)
        .log_level(lark.LogLevel.INFO)
        .build()
    )

    # 构造请求对象
    request: GetDocumentRequest = GetDocumentRequest.builder().document_id(document_id).build()

    # 发起请求
    response: GetDocumentResponse = client.docx.v1.document.get(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.docx.v1.document.get failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}"
        )
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))

    return response.data


# SDK 使用说明: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/preparations-before-development
# 以下示例代码默认根据文档示例值填充，如果存在代码问题，请在 API 调试台填上相关必要参数后再复制代码使用
# 复制该 Demo 后, 需要将 "YOUR_APP_ID", "YOUR_APP_SECRET" 替换为自己应用的 APP_ID, APP_SECRET.
def get_file_meta(token_manager: TenantAccessTokenManager, doc_token: str, doc_type: str) -> dict:
    # 创建client
    client = (
        lark.Client.builder()
        .app_id(token_manager.app_id)
        .app_secret(token_manager.app_secret)
        .log_level(lark.LogLevel.DEBUG)
        .build()
    )

    # 构造请求对象
    request: BatchQueryMetaRequest = (
        BatchQueryMetaRequest.builder()
        .user_id_type("open_id")
        .request_body(
            MetaRequest.builder()
            .request_docs([RequestDoc.builder().doc_token(doc_token).doc_type(doc_type).build()])
            .with_url(False)
            .build()
        )
        .build()
    )

    # 发起请求
    response: BatchQueryMetaResponse = client.drive.v1.meta.batch_query(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.drive.v1.meta.batch_query failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}"
        )
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))
    return response.data
