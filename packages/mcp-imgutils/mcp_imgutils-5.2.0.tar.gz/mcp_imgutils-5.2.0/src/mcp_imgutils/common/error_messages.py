"""
错误消息国际化支持

提供中英文错误消息和用户友好的解决建议。
"""

from .errors import MCPImageUtilsError

# 中文错误消息模板
ZH_MESSAGES = {
    # 配置错误
    "CONFIGURATIONERROR_CONFIGURATION": {
        "title": "配置错误",
        "message": "配置项缺失或无效",
        "suggestions": [
            "请检查配置文件是否存在",
            "运行 'mcp-imgutils diagnose' 诊断配置问题",
            "运行 'mcp-imgutils create-example-config' 创建示例配置"
        ]
    },
    
    # 网络错误
    "NETWORKERROR_NETWORK": {
        "title": "网络错误",
        "message": "网络连接失败",
        "suggestions": [
            "请检查网络连接是否正常",
            "检查防火墙设置是否阻止了连接",
            "稍后重试，可能是临时网络问题"
        ]
    },
    
    # API 相关错误
    "APIERROR_API": {
        "title": "API错误",
        "message": "API调用失败",
        "suggestions": [
            "请检查API密钥是否正确",
            "检查API服务是否正常运行",
            "查看API文档确认请求格式"
        ]
    },
    
    # 验证错误
    "VALIDATIONERROR_VALIDATION": {
        "title": "参数验证错误",
        "message": "输入参数不符合要求",
        "suggestions": [
            "请检查输入参数的格式和范围",
            "参考工具文档了解正确的参数格式",
            "确保所有必需参数都已提供"
        ]
    },
    
    # 资源错误
    "RESOURCEERROR_RESOURCE": {
        "title": "资源错误",
        "message": "资源访问或处理失败",
        "suggestions": [
            "检查文件路径是否正确",
            "确保有足够的磁盘空间",
            "检查文件权限设置"
        ]
    },
    
    # 认证错误
    "AUTHENTICATIONERROR_AUTHENTICATION": {
        "title": "认证错误",
        "message": "API密钥无效或已过期",
        "suggestions": [
            "请检查API密钥是否正确",
            "确认API密钥是否已过期",
            "重新生成API密钥并更新配置"
        ]
    },
    
    # 授权错误
    "AUTHORIZATIONERROR_AUTHORIZATION": {
        "title": "授权错误",
        "message": "没有权限执行此操作",
        "suggestions": [
            "检查API密钥的权限范围",
            "联系服务提供商确认账户权限",
            "确认是否需要升级账户等级"
        ]
    },
    
    # 速率限制错误
    "RATELIMITERROR_RATE_LIMIT": {
        "title": "速率限制",
        "message": "请求频率过高，已被限制",
        "suggestions": [
            "请稍后重试",
            "降低请求频率",
            "考虑升级到更高等级的API计划"
        ]
    },
    
    # 配额错误
    "QUOTAERROR_QUOTA": {
        "title": "配额不足",
        "message": "API使用配额已用完",
        "suggestions": [
            "检查账户余额或配额使用情况",
            "等待配额重置或购买更多配额",
            "优化使用策略以节省配额"
        ]
    },
    
    # 内部错误
    "MCPIMAGEUTILSERROR_INTERNAL": {
        "title": "内部错误",
        "message": "系统内部发生错误",
        "suggestions": [
            "请稍后重试",
            "如果问题持续存在，请报告此错误",
            "检查系统日志获取更多信息"
        ]
    }
}

# 英文错误消息模板
EN_MESSAGES = {
    # Configuration errors
    "CONFIGURATIONERROR_CONFIGURATION": {
        "title": "Configuration Error",
        "message": "Configuration is missing or invalid",
        "suggestions": [
            "Check if configuration file exists",
            "Run 'mcp-imgutils diagnose' to diagnose configuration issues",
            "Run 'mcp-imgutils create-example-config' to create example configuration"
        ]
    },
    
    # Network errors
    "NETWORKERROR_NETWORK": {
        "title": "Network Error",
        "message": "Network connection failed",
        "suggestions": [
            "Check if network connection is working",
            "Check firewall settings",
            "Retry later, might be a temporary network issue"
        ]
    },
    
    # API errors
    "APIERROR_API": {
        "title": "API Error",
        "message": "API call failed",
        "suggestions": [
            "Check if API key is correct",
            "Check if API service is running normally",
            "Refer to API documentation for correct request format"
        ]
    },
    
    # Validation errors
    "VALIDATIONERROR_VALIDATION": {
        "title": "Validation Error",
        "message": "Input parameters do not meet requirements",
        "suggestions": [
            "Check input parameter format and range",
            "Refer to tool documentation for correct parameter format",
            "Ensure all required parameters are provided"
        ]
    },
    
    # Resource errors
    "RESOURCEERROR_RESOURCE": {
        "title": "Resource Error",
        "message": "Resource access or processing failed",
        "suggestions": [
            "Check if file path is correct",
            "Ensure sufficient disk space",
            "Check file permission settings"
        ]
    },
    
    # Authentication errors
    "AUTHENTICATIONERROR_AUTHENTICATION": {
        "title": "Authentication Error",
        "message": "API key is invalid or expired",
        "suggestions": [
            "Check if API key is correct",
            "Confirm if API key has expired",
            "Regenerate API key and update configuration"
        ]
    },
    
    # Authorization errors
    "AUTHORIZATIONERROR_AUTHORIZATION": {
        "title": "Authorization Error",
        "message": "No permission to perform this operation",
        "suggestions": [
            "Check API key permission scope",
            "Contact service provider to confirm account permissions",
            "Check if account upgrade is needed"
        ]
    },
    
    # Rate limit errors
    "RATELIMITERROR_RATE_LIMIT": {
        "title": "Rate Limited",
        "message": "Request frequency too high, rate limited",
        "suggestions": [
            "Please retry later",
            "Reduce request frequency",
            "Consider upgrading to higher tier API plan"
        ]
    },
    
    # Quota errors
    "QUOTAERROR_QUOTA": {
        "title": "Quota Exceeded",
        "message": "API usage quota exhausted",
        "suggestions": [
            "Check account balance or quota usage",
            "Wait for quota reset or purchase more quota",
            "Optimize usage strategy to save quota"
        ]
    },
    
    # Internal errors
    "MCPIMAGEUTILSERROR_INTERNAL": {
        "title": "Internal Error",
        "message": "Internal system error occurred",
        "suggestions": [
            "Please retry later",
            "Report this error if problem persists",
            "Check system logs for more information"
        ]
    }
}

# 特定错误的详细消息
SPECIFIC_MESSAGES = {
    "zh": {
        # BFL特定错误
        "bfl_api_key_invalid": "BFL API密钥无效，请检查密钥是否正确",
        "bfl_quota_exceeded": "BFL积分不足，请充值后重试",
        "bfl_rate_limit": "BFL请求频率过高，请稍后重试",
        "bfl_model_not_supported": "不支持的BFL模型，请选择有效的模型",
        
        # 通用错误
        "file_not_found": "文件未找到，请检查文件路径",
        "permission_denied": "权限不足，请检查文件权限",
        "disk_space_full": "磁盘空间不足，请清理磁盘空间",
        "timeout": "操作超时，请稍后重试",
    },
    "en": {
        # BFL specific errors
        "bfl_api_key_invalid": "BFL API key is invalid, please check the key",
        "bfl_quota_exceeded": "BFL credits insufficient, please recharge and retry",
        "bfl_rate_limit": "BFL request rate too high, please retry later",
        "bfl_model_not_supported": "Unsupported BFL model, please select a valid model",
        
        # Common errors
        "file_not_found": "File not found, please check file path",
        "permission_denied": "Permission denied, please check file permissions",
        "disk_space_full": "Disk space full, please free up disk space",
        "timeout": "Operation timeout, please retry later",
    }
}


def get_user_message(error: MCPImageUtilsError, language: str = "zh") -> str:
    """
    获取用户友好的错误消息
    
    Args:
        error: 错误对象
        language: 语言代码 ("zh" 或 "en")
        
    Returns:
        用户友好的错误消息
    """
    messages = ZH_MESSAGES if language == "zh" else EN_MESSAGES
    
    # 获取错误模板
    template = messages.get(error.error_code, {})
    
    if not template:
        # 回退到通用消息
        return error.message
    
    # 构建用户消息
    title = template.get("title", "错误" if language == "zh" else "Error")
    message = template.get("message", error.message)
    suggestions = template.get("suggestions", [])
    
    # 格式化消息
    user_message = f"❌ {title}: {message}"
    
    # 添加具体错误信息
    if error.details and "status_code" in error.details:
        status_code = error.details["status_code"]
        if language == "zh":
            user_message += f"\n状态码: {status_code}"
        else:
            user_message += f"\nStatus Code: {status_code}"
    
    # 添加解决建议
    if suggestions:
        suggestion_title = "💡 解决建议:" if language == "zh" else "💡 Suggestions:"
        user_message += f"\n\n{suggestion_title}"
        for i, suggestion in enumerate(suggestions, 1):
            user_message += f"\n  {i}. {suggestion}"
    
    # 添加上下文信息
    if error.context and error.context.generator_name:
        context_title = "🔧 相关服务:" if language == "zh" else "🔧 Related Service:"
        user_message += f"\n\n{context_title} {error.context.generator_name.upper()}"
    
    return user_message


def get_specific_message(key: str, language: str = "zh") -> str | None:
    """
    获取特定的错误消息
    
    Args:
        key: 消息键
        language: 语言代码
        
    Returns:
        特定的错误消息，如果不存在则返回None
    """
    return SPECIFIC_MESSAGES.get(language, {}).get(key)


def format_error_for_user(error: Exception, language: str = "zh") -> str:
    """
    为用户格式化任何异常
    
    Args:
        error: 异常对象
        language: 语言代码
        
    Returns:
        格式化的错误消息
    """
    if isinstance(error, MCPImageUtilsError):
        return get_user_message(error, language)
    else:
        # 处理其他类型的异常
        error_type = error.__class__.__name__
        if language == "zh":
            return f"❌ 系统错误: {error_type} - {str(error)}"
        else:
            return f"❌ System Error: {error_type} - {str(error)}"
