"""
简单的错误处理系统测试
"""

import pytest


def test_error_import():
    """测试错误类型导入"""
    from src.mcp_imgutils.common.errors import ConfigurationError, MCPImageUtilsError
    assert MCPImageUtilsError is not None
    assert ConfigurationError is not None


def test_error_creation():
    """测试错误创建"""
    from src.mcp_imgutils.common.errors import ConfigurationError, ErrorCategory
    
    error = ConfigurationError("Missing API key")
    assert error.message == "Missing API key"
    assert error.category == ErrorCategory.CONFIGURATION


def test_error_messages():
    """测试错误消息"""
    from src.mcp_imgutils.common.error_messages import get_user_message
    from src.mcp_imgutils.common.errors import ConfigurationError
    
    error = ConfigurationError("Missing API key")
    message = get_user_message(error, "zh")
    
    assert "配置错误" in message
    assert "💡 解决建议" in message


def test_retry_config():
    """测试重试配置"""
    from src.mcp_imgutils.common.retry import RetryConfig
    
    config = RetryConfig(max_attempts=5)
    assert config.max_attempts == 5


def test_rate_limit():
    """测试速率限制"""
    from src.mcp_imgutils.common.rate_limiter import RateLimit
    
    rate_limit = RateLimit(requests_per_second=2.0)
    assert rate_limit.requests_per_second == pytest.approx(2.0)


def test_backward_compatibility():
    """测试向后兼容性"""
    from src.mcp_imgutils.common import BFLError, get_error_message
    
    # 测试BFL错误
    error = BFLError(401, "Invalid API key")
    assert error.code == 401
    assert error.message == "Invalid API key"
    
    # 测试错误消息函数
    message = get_error_message(401)
    assert "API key 无效" in message


@pytest.mark.asyncio
async def test_rate_limiter_basic():
    """测试速率限制器基础功能"""
    from src.mcp_imgutils.common.rate_limiter import RateLimit, RateLimiter
    
    rate_limit = RateLimit(requests_per_second=10.0)
    limiter = RateLimiter("test", rate_limit)
    
    # 应该能够成功获取许可
    await limiter.acquire()
    
    # 检查统计
    stats = limiter.get_usage_stats()
    assert stats["total_requests"] == 1


if __name__ == "__main__":
    pytest.main([__file__])
