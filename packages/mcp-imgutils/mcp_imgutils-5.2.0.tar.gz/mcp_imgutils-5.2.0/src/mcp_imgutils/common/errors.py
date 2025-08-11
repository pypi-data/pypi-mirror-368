
"""
统一错误处理系统

提供标准化的错误类型、错误消息和错误处理机制。
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ErrorCategory(Enum):
    """错误类别枚举"""
    CONFIGURATION = "configuration"
    NETWORK = "network"
    API = "api"
    VALIDATION = "validation"
    RESOURCE = "resource"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RATE_LIMIT = "rate_limit"
    QUOTA = "quota"
    INTERNAL = "internal"


class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorContext:
    """错误上下文信息"""
    generator_name: str | None = None
    operation: str | None = None
    request_id: str | None = None
    timestamp: float | None = None
    user_data: dict[str, Any] | None = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class MCPImageUtilsError(Exception):
    """MCP ImageUtils 错误基类"""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.INTERNAL,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
        context: ErrorContext | None = None,
        cause: Exception | None = None,
        suggestions: list[str] | None = None
    ):
        """
        初始化错误

        Args:
            message: 错误消息
            category: 错误类别
            severity: 错误严重程度
            error_code: 错误代码
            details: 错误详细信息
            context: 错误上下文
            cause: 原始异常
            suggestions: 解决建议
        """
        self.message = message
        self.category = category
        self.severity = severity
        self.error_code = error_code or self._generate_error_code()
        self.details = details or {}
        self.context = context or ErrorContext()
        self.cause = cause
        self.suggestions = suggestions or []

        super().__init__(self.message)

    def _generate_error_code(self) -> str:
        """生成错误代码"""
        class_name = self.__class__.__name__
        category_code = self.category.value.upper()
        return f"{class_name.upper()}_{category_code}"

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "details": self.details,
            "context": {
                "generator_name": self.context.generator_name,
                "operation": self.context.operation,
                "request_id": self.context.request_id,
                "timestamp": self.context.timestamp,
                "user_data": self.context.user_data,
            },
            "suggestions": self.suggestions,
            "cause": str(self.cause) if self.cause else None,
        }

    def get_user_message(self, language: str = "zh") -> str:
        """
        获取用户友好的错误消息

        Args:
            language: 语言代码 ("zh" 或 "en")

        Returns:
            用户友好的错误消息
        """
        from .error_messages import get_user_message
        return get_user_message(self, language)


class ConfigurationError(MCPImageUtilsError):
    """配置错误"""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class NetworkError(MCPImageUtilsError):
    """网络错误"""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class APIError(MCPImageUtilsError):
    """API错误"""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
        **kwargs
    ):
        # 从kwargs中提取details，避免重复传递
        details = kwargs.pop("details", {})
        if status_code is not None:
            details["status_code"] = status_code
        if response_data is not None:
            details["response_data"] = response_data

        super().__init__(
            message=message,
            category=ErrorCategory.API,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            **kwargs
        )

        self.status_code = status_code
        self.response_data = response_data


class ValidationError(MCPImageUtilsError):
    """验证错误"""

    def __init__(self, message: str, field: str | None = None, **kwargs):
        details = kwargs.get("details", {})
        if field is not None:
            details["field"] = field

        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            **kwargs
        )

        self.field = field


class ResourceError(MCPImageUtilsError):
    """资源错误"""

    def __init__(self, message: str, resource_type: str | None = None, **kwargs):
        details = kwargs.get("details", {})
        if resource_type is not None:
            details["resource_type"] = resource_type

        super().__init__(
            message=message,
            category=ErrorCategory.RESOURCE,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            **kwargs
        )

        self.resource_type = resource_type


class AuthenticationError(MCPImageUtilsError):
    """认证错误"""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class AuthorizationError(MCPImageUtilsError):
    """授权错误"""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class RateLimitError(MCPImageUtilsError):
    """速率限制错误"""

    def __init__(
        self,
        message: str,
        retry_after: int | None = None,
        limit: int | None = None,
        remaining: int | None = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if retry_after is not None:
            details["retry_after"] = retry_after
        if limit is not None:
            details["limit"] = limit
        if remaining is not None:
            details["remaining"] = remaining

        super().__init__(
            message=message,
            category=ErrorCategory.RATE_LIMIT,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            **kwargs
        )

        self.retry_after = retry_after
        self.limit = limit
        self.remaining = remaining


class QuotaError(MCPImageUtilsError):
    """配额错误"""

    def __init__(
        self,
        message: str,
        quota_type: str | None = None,
        used: int | None = None,
        limit: int | None = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if quota_type is not None:
            details["quota_type"] = quota_type
        if used is not None:
            details["used"] = used
        if limit is not None:
            details["limit"] = limit

        super().__init__(
            message=message,
            category=ErrorCategory.QUOTA,
            severity=ErrorSeverity.HIGH,
            details=details,
            **kwargs
        )

        self.quota_type = quota_type
        self.used = used
        self.limit = limit


# 向后兼容的BFL错误类
class BFLError(APIError):
    """BFL API 错误 (向后兼容)"""

    def __init__(self, code: int, message: str, details: dict[str, Any] | None = None):
        context = ErrorContext(generator_name="bfl")
        # 确保details不为None
        if details is None:
            details = {}

        super().__init__(
            message=message,
            status_code=code,
            details=details,
            context=context
        )

        # 保持向后兼容的属性
        self.code = code
