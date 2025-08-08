"""
Tests for lark_helper.v1.application module
"""

import pytest

from lark_helper.v1.application import get_application_info
from lark_helper.v1_async.application import async_get_application_info
from tests.config import APP_ADMIN_APP_ID, app_admin_token_manager


def test_get_application_info():
    app_info = get_application_info(app_admin_token_manager, APP_ADMIN_APP_ID)
    print(app_info)


@pytest.mark.asyncio
async def test_async_get_application_info():
    app_info = await async_get_application_info(app_admin_token_manager, APP_ADMIN_APP_ID)
    print(app_info)
    