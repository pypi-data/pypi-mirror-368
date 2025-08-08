from lark_helper.token_manager import TenantAccessTokenManager
from lark_helper.utils.async_request import async_make_lark_request


async def async_get_user_info(
    token_manager: TenantAccessTokenManager,
    user_id: str,
):
    """
    获取用户信息
    https://open.feishu.cn/document/server-docs/contact-v3/user/get
    """

    url = f"https://open.feishu.cn/open-apis/contact/v3/users/{user_id}"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {await token_manager.async_get_tenant_access_token()}",
    }
    params = {"user_id_type": "open_id"}

    def extract_user(data):
        return data.get("user")

    return await async_make_lark_request(
        method="GET",
        url=url,
        headers=headers,
        params=params,
        data_extractor=extract_user,
    )


async def async_batch_get_open_id(
    token_manager: TenantAccessTokenManager,
    mobile_list: list[str],
):
    """
    批量获取用户ID
    """
    url = "https://open.feishu.cn/open-apis/contact/v3/users/batch_get_id"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {await token_manager.async_get_tenant_access_token()}",
    }
    payload = {
        "mobiles": mobile_list,
    }
    params = {"user_id_type": "open_id"}

    def extract_user_list(data):
        return data.get("user_list")

    return await async_make_lark_request(
        method="POST",
        url=url,
        headers=headers,
        data=payload,
        params=params,
        data_extractor=extract_user_list,
    )
