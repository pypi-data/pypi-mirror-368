"""
OSLisLim - Open Source License Limitation
开源许可限制协议

保护开源项目免受商业滥用的技术解决方案
"""

__version__ = "0.3.2"
__author__ = "OSLisLim Contributors"
__email__ = "oslislim@suwork.eu.org"

# 核心加密保护功能
from .crypto_client import (
    decrypt_and_execute,
    protect_function,
    generate_protection_bundle,
    create_default_tracker,
    create_default_config,
    detect_packaging_environment,
    get_environment_info
)

# 异常类
from .exceptions import OSLisLimError, ValidationError, ProtectionError

__all__ = [
    # 核心保护功能
    "decrypt_and_execute",
    "protect_function",

    # 生成保护包功能
    "generate_protection_bundle",
    "create_default_tracker",
    "create_default_config",

    # 环境检测功能
    "detect_packaging_environment",
    "get_environment_info",

    # 异常类
    "OSLisLimError",
    "ValidationError",
    "ProtectionError"
]
