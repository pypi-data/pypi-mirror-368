import logging
import time
from typing import Any

from lark_helper.utils.async_request import async_make_lark_request
from lark_helper.utils.request import make_lark_request

logger = logging.getLogger(__name__)


class TenantAccessTokenManager:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.token = None
        self.token_expiry = 0
        self.refresh_threshold = 1800  # 30分钟的刷新阈值（秒）

    def get_tenant_access_token(self):
        current_time = time.time()
        # 如果token不存在，或者剩余有效期小于30分钟，则获取新token
        if self.token is None or (self.token_expiry - current_time) < self.refresh_threshold:
            self.token = self._fetch_tenant_access_token()
            # 使用API返回的实际过期时间来设置过期时间
            self.token_expiry = current_time + self.token["expire"]
            return self.token["token"]
        return self.token["token"]

    def _fetch_tenant_access_token(self):
        """
        https://open.feishu.cn/document/server-docs/authentication-management/access-token/tenant_access_token_internal
        """
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        payload = {"app_id": self.app_id, "app_secret": self.app_secret}

        def extract_token_info(result):
            logger.info("获取租户access_token成功")
            return {
                "token": result.get("tenant_access_token"),
                "expire": result.get("expire"),
            }

        return make_lark_request(
            method="POST",
            url=url,
            headers=headers,
            data=payload,
            data_extractor=extract_token_info,
            use_root_response=True,
        )

    async def async_get_tenant_access_token(self) -> str:
        """
        Get a valid tenant access token.

        If a valid token is cached, return it. Otherwise, fetch a new one.

        Returns:
            Tenant access token
        """
        current_time = time.time()
        if self.token is None or (self.token_expiry - current_time) < self.refresh_threshold:
            self.token = await self._async_fetch_tenant_access_token()
            # 使用API返回的实际过期时间来设置过期时间
            self.token_expiry = current_time + self.token["expire"]
            return self.token["token"]
        return self.token["token"]

    async def _async_fetch_tenant_access_token(self) -> dict[str, Any]:
        """
        Fetch a new tenant access token from the Lark API.

        Returns:
            Token data including tenant_access_token and expire
        """
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        data = {"app_id": self.app_id, "app_secret": self.app_secret}

        def extract_token_info(result):
            logger.info("获取租户access_token成功")
            return {
                "token": result.get("tenant_access_token"),
                "expire": result.get("expire"),
            }

        return await async_make_lark_request(
            method="POST",
            url=url,
            headers=headers,
            data=data,
            data_extractor=extract_token_info,
            use_root_response=True,
        )
