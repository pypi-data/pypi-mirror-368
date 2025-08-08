from lark_helper.token_manager import TenantAccessTokenManager
from lark_helper.utils.async_request import async_make_lark_request


async def async_get_application_info(
    token_manager: TenantAccessTokenManager,
    app_id: str,
) -> dict:
    url = f"https://open.feishu.cn/open-apis/application/v6/applications/{app_id}?lang=zh_cn"
    headers = {
        "Authorization": f"Bearer {token_manager.get_tenant_access_token()}",
        "Content-Type": "application/json; charset=utf-8",
    }

    def extract_data(data):
        return data

    return await async_make_lark_request(
        method="GET", url=url, headers=headers, data_extractor=extract_data
    )
