"""
Lark Helper - A Python library for interacting with Lark APIs.

This library provides both synchronous and asynchronous interfaces for Lark API operations.

Synchronous API:
    from lark_helper.token_manager import TenantAccessTokenManager
    from lark_helper.v1 import bitable, message, file

Asynchronous API (requires aiohttp):
    from lark_helper.token_manager import TenantAccessTokenManager
    from lark_helper.v1_async import bitable, message, file
"""

__version__ = "0.1.0.dev11"
__author__ = "philo-veritas"
__email__ = "edison.gee.lan@gmail.com"

# Re-export commonly used classes for convenience
from .token_manager import TenantAccessTokenManager

__all__ = [
    "TenantAccessTokenManager",
]
