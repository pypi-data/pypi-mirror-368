"""
测试统一错误处理系统
"""

import pytest

from src.mcp_imgutils.common.error_messages import (
    format_error_for_user,
    get_user_message,
)
from src.mcp_imgutils.common.errors import (
    APIError,
    ConfigurationError,
    ErrorCategory,
    ErrorContext,
    ErrorSeverity,
    MCPImageUtilsError,
    NetworkError,
    QuotaError,
    RateLimitError,
)
from src.mcp_imgutils.common.rate_limiter import RateLimit, RateLimiter
from src.mcp_imgutils.common.retry import RetryConfig, RetryStrategy, with_retry


class TestErrorTypes:
    """测试错误类型"""
    
    def test_base_error_creation(self):
        """测试基础错误创建"""
        error = MCPImageUtilsError(
            message="Test error",
            category=ErrorCategory.API,
            severity=ErrorSeverity.HIGH
        )
        
        assert error.message == "Test error"
        assert error.category == ErrorCategory.API
        assert error.severity == ErrorSeverity.HIGH
        assert error.error_code == "MCPIMAGEUTILSERROR_API"
        assert isinstance(error.context, ErrorContext)
    
    def test_configuration_error(self):
        """测试配置错误"""
        error = ConfigurationError("Missing API key")
        
        assert error.category == ErrorCategory.CONFIGURATION
        assert error.severity == ErrorSeverity.HIGH
        assert "Missing API key" in error.message
    
    def test_api_error_with_status_code(self):
        """测试带状态码的API错误"""
        error = APIError(
            message="API call failed",
            status_code=429,
            response_data={"error": "rate limited"}
        )
        
        assert error.status_code == 429
        assert error.response_data["error"] == "rate limited"
        assert error.details["status_code"] == 429
    
    def test_rate_limit_error(self):
        """测试速率限制错误"""
        error = RateLimitError(
            message="Rate limited",
            retry_after=60,
            limit=100,
            remaining=0
        )
        
        assert error.retry_after == 60
        assert error.limit == 100
        assert error.remaining == 0
    
    def test_error_to_dict(self):
        """测试错误转换为字典"""
        context = ErrorContext(generator_name="bfl", operation="generate")
        error = APIError(
            message="API error",
            status_code=500,
            context=context
        )
        
        error_dict = error.to_dict()
        
        assert error_dict["message"] == "API error"
        assert error_dict["category"] == "api"
        assert error_dict["context"]["generator_name"] == "bfl"
        assert error_dict["details"]["status_code"] == 500


class TestErrorMessages:
    """测试错误消息"""
    
    def test_user_message_chinese(self):
        """测试中文用户消息"""
        error = ConfigurationError("Missing API key")
        message = get_user_message(error, "zh")
        
        assert "配置错误" in message
        assert "💡 解决建议" in message
        assert "检查配置文件" in message
    
    def test_user_message_english(self):
        """测试英文用户消息"""
        error = ConfigurationError("Missing API key")
        message = get_user_message(error, "en")
        
        assert "Configuration Error" in message
        assert "💡 Suggestions" in message
        assert "Check if configuration" in message
    
    def test_format_error_for_user(self):
        """测试为用户格式化错误"""
        # 测试我们的错误类型
        our_error = NetworkError("Connection failed")
        formatted = format_error_for_user(our_error, "zh")
        assert "网络错误" in formatted
        
        # 测试其他异常类型
        other_error = ValueError("Invalid value")
        formatted = format_error_for_user(other_error, "zh")
        assert "系统错误" in formatted
        assert "ValueError" in formatted


class TestRetryMechanism:
    """测试重试机制"""
    
    def test_retry_config(self):
        """测试重试配置"""
        config = RetryConfig(
            max_attempts=5,
            base_delay=2.0,
            exponential_base=2.0
        )
        
        assert config.max_attempts == 5
        assert config.base_delay == pytest.approx(2.0)
        assert config.exponential_base == pytest.approx(2.0)
    
    def test_retry_strategy_should_retry(self):
        """测试重试策略判断"""
        config = RetryConfig(max_attempts=3)
        strategy = RetryStrategy(config)
        
        # 网络错误应该重试
        network_error = NetworkError("Connection failed")
        assert strategy.should_retry(network_error, 1) is True
        assert strategy.should_retry(network_error, 3) is False  # 超过最大次数
        
        # 认证错误不应该重试
        auth_error = ConfigurationError("Invalid API key")
        assert strategy.should_retry(auth_error, 1) is False
    
    def test_retry_strategy_api_error(self):
        """测试API错误重试策略"""
        config = RetryConfig(max_attempts=3)
        strategy = RetryStrategy(config)
        
        # 5xx错误应该重试
        server_error = APIError("Server error", status_code=500)
        assert strategy.should_retry(server_error, 1) is True
        
        # 4xx错误不应该重试
        client_error = APIError("Bad request", status_code=400)
        assert strategy.should_retry(client_error, 1) is False
        
        # 429错误应该重试
        rate_limit_error = APIError("Rate limited", status_code=429)
        assert strategy.should_retry(rate_limit_error, 1) is True
    
    def test_retry_delay_calculation(self):
        """测试重试延迟计算"""
        config = RetryConfig(
            base_delay=1.0,
            exponential_base=2.0,
            max_delay=10.0,
            jitter=False
        )
        strategy = RetryStrategy(config)
        
        # 测试指数退避
        assert strategy.calculate_delay(1) == pytest.approx(1.0)
        assert strategy.calculate_delay(2) == pytest.approx(2.0)
        assert strategy.calculate_delay(3) == pytest.approx(4.0)

        # 测试最大延迟限制
        assert strategy.calculate_delay(10) == pytest.approx(10.0)
    
    def test_retry_with_rate_limit_error(self):
        """测试速率限制错误的重试延迟"""
        config = RetryConfig()
        strategy = RetryStrategy(config)
        
        rate_limit_error = RateLimitError("Rate limited", retry_after=30)
        delay = strategy.calculate_delay(1, rate_limit_error)
        
        assert delay == pytest.approx(30.0)
    
    @pytest.mark.asyncio
    async def test_retry_decorator_success(self):
        """测试重试装饰器成功情况"""
        call_count = 0
        
        @with_retry(RetryConfig(max_attempts=3))
        async def test_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await test_function()
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_retry_decorator_with_retries(self):
        """测试重试装饰器重试情况"""
        call_count = 0
        
        @with_retry(RetryConfig(max_attempts=3, base_delay=0.1))
        async def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise NetworkError("Network failed")
            return "success"
        
        result = await test_function()
        assert result == "success"
        assert call_count == 3


class TestRateLimiter:
    """测试速率限制器"""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_creation(self):
        """测试速率限制器创建"""
        rate_limit = RateLimit(requests_per_second=2.0)
        limiter = RateLimiter("test", rate_limit)
        
        assert limiter.generator_name == "test"
        assert limiter.rate_limit.requests_per_second == pytest.approx(2.0)
    
    @pytest.mark.asyncio
    async def test_rate_limiter_acquire_success(self):
        """测试速率限制器获取许可成功"""
        rate_limit = RateLimit(
            requests_per_second=10.0,  # 高限制，不会触发
            requests_per_minute=600.0
        )
        limiter = RateLimiter("test", rate_limit)
        
        # 应该能够成功获取许可
        await limiter.acquire()
        
        # 检查统计
        stats = limiter.get_usage_stats()
        assert stats["total_requests"] == 1
    
    @pytest.mark.asyncio
    async def test_rate_limiter_quota_exceeded(self):
        """测试配额超限"""
        rate_limit = RateLimit(
            requests_per_second=10.0,
            daily_quota=1  # 很低的配额
        )
        limiter = RateLimiter("test", rate_limit)
        
        # 第一次应该成功
        await limiter.acquire()
        await limiter.record_success()
        
        # 第二次应该失败
        with pytest.raises(QuotaError):
            await limiter.acquire()
    
    @pytest.mark.asyncio
    async def test_rate_limiter_stats(self):
        """测试速率限制器统计"""
        rate_limit = RateLimit(requests_per_second=10.0)
        limiter = RateLimiter("test", rate_limit)
        
        await limiter.acquire()
        await limiter.record_success()
        
        stats = limiter.get_usage_stats()
        assert stats["generator_name"] == "test"
        assert stats["total_requests"] == 1
        assert stats["successful_requests"] == 1
        assert stats["failed_requests"] == 0


if __name__ == "__main__":
    pytest.main([__file__])
