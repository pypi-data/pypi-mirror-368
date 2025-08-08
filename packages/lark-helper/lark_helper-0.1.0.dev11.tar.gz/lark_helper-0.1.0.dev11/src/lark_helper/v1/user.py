from lark_helper.token_manager import TenantAccessTokenManager
from lark_helper.utils.request import make_lark_request


def get_user_info(
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
        "Authorization": f"Bearer {token_manager.get_tenant_access_token()}",
    }
    params = {"user_id_type": "open_id"}

    def extract_user(data):
        return data.get("user")

    return make_lark_request(
        method="GET",
        url=url,
        headers=headers,
        params=params,
        data_extractor=extract_user,
    )


def batch_get_open_id(
    token_manager: TenantAccessTokenManager,
    mobile_list: list[str],
):
    """
    批量获取用户ID
    """
    url = "https://open.feishu.cn/open-apis/contact/v3/users/batch_get_id"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {token_manager.get_tenant_access_token()}",
    }
    payload = {
        "mobiles": mobile_list,
    }
    params = {"user_id_type": "open_id"}

    def extract_user_list(data):
        return data.get("user_list")

    return make_lark_request(
        method="POST",
        url=url,
        headers=headers,
        data=payload,
        params=params,
        data_extractor=extract_user_list,
    )
