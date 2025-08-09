"""
通用模块

提供错误处理、配置管理、重试机制等通用功能。
"""

from .config import ConfigManager, get_config, get_config_manager, set_config
from .error_messages import format_error_for_user, get_user_message
from .errors import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    BFLError,
    ErrorCategory,
    ErrorContext,
    ErrorSeverity,
    MCPImageUtilsError,
    NetworkError,
    QuotaError,
    RateLimitError,
    ResourceError,
    ValidationError,
)
from .rate_limiter import RateLimit, RateLimiter, get_rate_limiter_manager
from .resource_factory import (
    ResourceManagerFactory,
    cleanup_resources,
    get_image,
    get_resource_manager,
    get_resource_stats,
    initialize_resource_manager,
    store_image,
)
from .resource_manager import (
    ResourceManager,
    ResourceMetadata,
    ResourceStatus,
    ResourceType,
    generate_cache_key,
    generate_resource_id,
)
from .retry import RetryConfig, RetryStrategy, with_retry

__all__ = [
    # 错误类型
    "BFLError",
    "MCPImageUtilsError",
    "NetworkError",
    "APIError",
    "ValidationError",
    "ResourceError",
    "AuthenticationError",
    "AuthorizationError",
    "RateLimitError",
    "QuotaError",
    "ErrorCategory",
    "ErrorSeverity",
    "ErrorContext",

    # 错误消息
    "get_user_message",
    "format_error_for_user",

    # 配置管理
    "ConfigManager",
    "get_config_manager",
    "get_config",
    "set_config",

    # 重试机制
    "RetryConfig",
    "RetryStrategy",
    "with_retry",

    # 速率限制
    "RateLimit",
    "RateLimiter",
    "get_rate_limiter_manager",

    # 资源管理
    "ResourceManager",
    "ResourceMetadata",
    "ResourceType",
    "ResourceStatus",
    "generate_resource_id",
    "generate_cache_key",
    "ResourceManagerFactory",
    "get_resource_manager",
    "initialize_resource_manager",
    "store_image",
    "get_image",
    "cleanup_resources",
    "get_resource_stats",
]


# 向后兼容的函数
def get_error_message(status_code: int, default_message: str = None) -> str:
    """
    获取错误信息 (向后兼容)

    Args:
        status_code: HTTP状态码
        default_message: 默认消息

    Returns:
        错误消息
    """
    error_messages = {
        401: "API key 无效",
        402: "积分不足",
        429: "超出并发限制",
        400: "请求参数错误",
        500: "服务器内部错误"
    }

    return error_messages.get(status_code, default_message or f"未知错误: {status_code}")
