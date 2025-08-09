"""
智能重试机制

提供网络错误重试、指数退避算法和API限制处理。
"""

import asyncio
import logging
import random
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any

from .errors import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    NetworkError,
    QuotaError,
    RateLimitError,
)

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """重试配置"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    jitter_range: float = 0.1
    
    # 可重试的错误类型
    retryable_errors: list[type[Exception]] = None
    
    # 不可重试的错误类型
    non_retryable_errors: list[type[Exception]] = None
    
    def __post_init__(self):
        if self.retryable_errors is None:
            self.retryable_errors = [
                NetworkError,
                RateLimitError,
                # APIError 需要特殊处理，不在默认列表中
            ]
        
        if self.non_retryable_errors is None:
            self.non_retryable_errors = [
                AuthenticationError,
                AuthorizationError,
                QuotaError,  # 配额错误通常不应该重试
            ]


class RetryStrategy:
    """重试策略"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
    
    def should_retry(self, error: Exception, attempt: int) -> bool:
        """
        判断是否应该重试
        
        Args:
            error: 发生的错误
            attempt: 当前尝试次数
            
        Returns:
            是否应该重试
        """
        # 检查尝试次数
        if attempt >= self.config.max_attempts:
            return False
        
        # 检查不可重试的错误类型
        for non_retryable_type in self.config.non_retryable_errors:
            if isinstance(error, non_retryable_type):
                logger.debug(f"Error {type(error).__name__} is non-retryable")
                return False
        
        # 检查可重试的错误类型
        for retryable_type in self.config.retryable_errors:
            if isinstance(error, retryable_type):
                logger.debug(f"Error {type(error).__name__} is retryable")
                return True
        
        # 特殊处理API错误
        if isinstance(error, APIError):
            return self._should_retry_api_error(error)
        
        # 默认不重试
        return False
    
    def _should_retry_api_error(self, error: APIError) -> bool:
        """
        判断API错误是否应该重试
        
        Args:
            error: API错误
            
        Returns:
            是否应该重试
        """
        if error.status_code is None:
            return True  # 网络错误，可以重试
        
        # 5xx错误通常可以重试
        if 500 <= error.status_code < 600:
            return True
        
        # 429 (Too Many Requests) 可以重试
        if error.status_code == 429:
            return True
        
        # 408 (Request Timeout) 可以重试
        if error.status_code == 408:
            return True
        
        # 502, 503, 504 网关错误可以重试
        if error.status_code in [502, 503, 504]:
            return True
        
        # 4xx错误通常不应该重试
        if 400 <= error.status_code < 500:
            return False
        
        return False
    
    def calculate_delay(self, attempt: int, error: Exception | None = None) -> float:
        """
        计算重试延迟时间
        
        Args:
            attempt: 当前尝试次数
            error: 发生的错误
            
        Returns:
            延迟时间（秒）
        """
        # 处理速率限制错误
        if isinstance(error, RateLimitError) and error.retry_after:
            delay = error.retry_after
            logger.debug(f"Rate limit error, using retry_after: {delay}s")
            # 对于速率限制错误，使用精确的延迟时间，不添加抖动
            return float(delay)
        else:
            # 指数退避算法
            delay = self.config.base_delay * (self.config.exponential_base ** (attempt - 1))

        # 限制最大延迟
        delay = min(delay, self.config.max_delay)

        # 添加抖动
        if self.config.jitter:
            jitter_amount = delay * self.config.jitter_range
            jitter = random.uniform(-jitter_amount, jitter_amount)
            delay += jitter
        
        # 确保延迟为正数
        delay = max(0.1, delay)
        
        logger.debug(f"Calculated retry delay: {delay:.2f}s for attempt {attempt}")
        return delay


class RetryManager:
    """重试管理器"""
    
    def __init__(self, strategy: RetryStrategy):
        self.strategy = strategy
    
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        执行函数并在失败时重试
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
            
        Raises:
            最后一次尝试的异常
        """
        last_error = None
        
        for attempt in range(1, self.strategy.config.max_attempts + 1):
            try:
                logger.debug(f"Executing function {func.__name__}, attempt {attempt}")
                
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                if attempt > 1:
                    logger.info(f"Function {func.__name__} succeeded on attempt {attempt}")
                
                return result
                
            except Exception as error:
                last_error = error
                logger.debug(f"Function {func.__name__} failed on attempt {attempt}: {error}")
                
                # 检查是否应该重试
                if not self.strategy.should_retry(error, attempt):
                    logger.debug("Not retrying due to error type or max attempts reached")
                    raise error
                
                # 如果不是最后一次尝试，则等待后重试
                if attempt < self.strategy.config.max_attempts:
                    delay = self.strategy.calculate_delay(attempt, error)
                    logger.info(f"Retrying {func.__name__} in {delay:.2f}s (attempt {attempt + 1}/{self.strategy.config.max_attempts})")
                    await asyncio.sleep(delay)
        
        # 如果所有尝试都失败了，抛出最后一个错误
        if last_error:
            raise last_error


# 默认重试配置
DEFAULT_RETRY_CONFIG = RetryConfig()
DEFAULT_RETRY_STRATEGY = RetryStrategy(DEFAULT_RETRY_CONFIG)
DEFAULT_RETRY_MANAGER = RetryManager(DEFAULT_RETRY_STRATEGY)


def with_retry(
    config: RetryConfig | None = None,
    strategy: RetryStrategy | None = None
):
    """
    重试装饰器
    
    Args:
        config: 重试配置
        strategy: 重试策略
        
    Returns:
        装饰器函数
    """
    if strategy is None:
        if config is None:
            config = DEFAULT_RETRY_CONFIG
        strategy = RetryStrategy(config)
    
    retry_manager = RetryManager(strategy)
    
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await retry_manager.execute_with_retry(func, *args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 对于同步函数，我们需要在异步环境中运行重试逻辑
            async def async_func():
                return func(*args, **kwargs)
            
            try:
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(retry_manager.execute_with_retry(async_func))
            except RuntimeError:
                # 如果没有事件循环，创建一个新的
                return asyncio.run(retry_manager.execute_with_retry(async_func))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# 便捷的重试函数
async def retry_async(
    func: Callable,
    *args,
    config: RetryConfig | None = None,
    **kwargs
) -> Any:
    """
    异步重试函数
    
    Args:
        func: 要重试的函数
        *args: 函数参数
        config: 重试配置
        **kwargs: 函数关键字参数
        
    Returns:
        函数执行结果
    """
    if config is None:
        config = DEFAULT_RETRY_CONFIG
    
    strategy = RetryStrategy(config)
    manager = RetryManager(strategy)
    
    return await manager.execute_with_retry(func, *args, **kwargs)


def retry_sync(
    func: Callable,
    *args,
    config: RetryConfig | None = None,
    **kwargs
) -> Any:
    """
    同步重试函数
    
    Args:
        func: 要重试的函数
        *args: 函数参数
        config: 重试配置
        **kwargs: 函数关键字参数
        
    Returns:
        函数执行结果
    """
    async def async_func():
        return func(*args, **kwargs)
    
    return asyncio.run(retry_async(async_func, config=config))


# 预定义的重试配置
NETWORK_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    base_delay=1.0,
    max_delay=30.0,
    exponential_base=2.0,
    retryable_errors=[NetworkError, APIError]
)

API_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    base_delay=2.0,
    max_delay=60.0,
    exponential_base=2.0,
    retryable_errors=[APIError, RateLimitError]
)

AGGRESSIVE_RETRY_CONFIG = RetryConfig(
    max_attempts=10,
    base_delay=0.5,
    max_delay=120.0,
    exponential_base=1.5,
    jitter_range=0.2
)
