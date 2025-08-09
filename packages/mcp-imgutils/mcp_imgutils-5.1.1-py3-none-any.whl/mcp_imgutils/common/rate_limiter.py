"""
API速率限制和配额管理

提供智能的API调用频率控制和配额监控。
"""

import asyncio
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from .errors import ErrorContext, QuotaError, RateLimitError

logger = logging.getLogger(__name__)


@dataclass
class RateLimit:
    """速率限制配置"""
    requests_per_second: float = 1.0
    requests_per_minute: float = 60.0
    requests_per_hour: float = 3600.0
    requests_per_day: float = 86400.0
    
    # 突发请求允许量
    burst_size: int = 5
    
    # 配额限制
    daily_quota: int | None = None
    monthly_quota: int | None = None


@dataclass
class UsageStats:
    """使用统计"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limited_requests: int = 0
    quota_exceeded_requests: int = 0
    
    # 时间窗口统计
    requests_last_second: int = 0
    requests_last_minute: int = 0
    requests_last_hour: int = 0
    requests_last_day: int = 0
    
    # 配额使用
    daily_usage: int = 0
    monthly_usage: int = 0
    
    last_reset_time: float = field(default_factory=time.time)


class TokenBucket:
    """令牌桶算法实现"""
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        初始化令牌桶
        
        Args:
            capacity: 桶容量
            refill_rate: 令牌补充速率（每秒）
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> bool:
        """
        消费令牌
        
        Args:
            tokens: 需要消费的令牌数量
            
        Returns:
            是否成功消费令牌
        """
        async with self._lock:
            now = time.time()
            
            # 补充令牌
            time_passed = now - self.last_refill
            new_tokens = time_passed * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + new_tokens)
            self.last_refill = now
            
            # 检查是否有足够的令牌
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            else:
                return False
    
    async def wait_for_tokens(self, tokens: int = 1) -> float:
        """
        等待足够的令牌
        
        Args:
            tokens: 需要的令牌数量
            
        Returns:
            等待时间（秒）
        """
        async with self._lock:
            if self.tokens >= tokens:
                return 0.0
            
            # 计算需要等待的时间
            needed_tokens = tokens - self.tokens
            wait_time = needed_tokens / self.refill_rate
            return wait_time


class SlidingWindowCounter:
    """滑动窗口计数器"""
    
    def __init__(self, window_size: float):
        """
        初始化滑动窗口计数器
        
        Args:
            window_size: 窗口大小（秒）
        """
        self.window_size = window_size
        self.requests = deque()
        self._lock = asyncio.Lock()
    
    async def add_request(self, timestamp: float | None = None) -> None:
        """
        添加请求记录
        
        Args:
            timestamp: 请求时间戳，默认为当前时间
        """
        if timestamp is None:
            timestamp = time.time()
        
        async with self._lock:
            self.requests.append(timestamp)
            await self._cleanup_old_requests()
    
    async def get_count(self) -> int:
        """
        获取当前窗口内的请求数量
        
        Returns:
            请求数量
        """
        async with self._lock:
            await self._cleanup_old_requests()
            return len(self.requests)
    
    async def _cleanup_old_requests(self) -> None:
        """清理过期的请求记录"""
        now = time.time()
        cutoff = now - self.window_size
        
        while self.requests and self.requests[0] < cutoff:
            self.requests.popleft()


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, generator_name: str, rate_limit: RateLimit):
        """
        初始化速率限制器
        
        Args:
            generator_name: 生成器名称
            rate_limit: 速率限制配置
        """
        self.generator_name = generator_name
        self.rate_limit = rate_limit
        self.usage_stats = UsageStats()
        
        # 令牌桶（用于突发请求控制）
        self.token_bucket = TokenBucket(
            capacity=rate_limit.burst_size,
            refill_rate=rate_limit.requests_per_second
        )
        
        # 滑动窗口计数器
        self.counters = {
            'second': SlidingWindowCounter(1.0),
            'minute': SlidingWindowCounter(60.0),
            'hour': SlidingWindowCounter(3600.0),
            'day': SlidingWindowCounter(86400.0),
        }
        
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """
        获取请求许可
        
        Raises:
            RateLimitError: 当超过速率限制时
            QuotaError: 当超过配额限制时
        """
        async with self._lock:
            # 检查配额限制
            await self._check_quota_limits()
            
            # 检查速率限制
            await self._check_rate_limits()
            
            # 消费令牌
            if not await self.token_bucket.consume():
                wait_time = await self.token_bucket.wait_for_tokens()
                raise RateLimitError(
                    message=f"Rate limit exceeded for {self.generator_name}",
                    retry_after=int(wait_time) + 1,
                    context=ErrorContext(generator_name=self.generator_name)
                )
            
            # 记录请求
            await self._record_request()
    
    async def _check_quota_limits(self) -> None:
        """检查配额限制"""
        # 检查每日配额
        if self.rate_limit.daily_quota is not None and self.usage_stats.daily_usage >= self.rate_limit.daily_quota:
            raise QuotaError(
                message=f"Daily quota exceeded for {self.generator_name}",
                quota_type="daily",
                used=self.usage_stats.daily_usage,
                limit=self.rate_limit.daily_quota,
                context=ErrorContext(generator_name=self.generator_name)
            )
        
        # 检查月度配额
        if self.rate_limit.monthly_quota is not None and self.usage_stats.monthly_usage >= self.rate_limit.monthly_quota:
            raise QuotaError(
                message=f"Monthly quota exceeded for {self.generator_name}",
                quota_type="monthly",
                used=self.usage_stats.monthly_usage,
                    limit=self.rate_limit.monthly_quota,
                    context=ErrorContext(generator_name=self.generator_name)
                )
    
    async def _check_rate_limits(self) -> None:
        """检查速率限制"""
        # 检查每秒限制
        second_count = await self.counters['second'].get_count()
        if second_count >= self.rate_limit.requests_per_second:
            raise RateLimitError(
                message=f"Requests per second limit exceeded for {self.generator_name}",
                retry_after=1,
                limit=int(self.rate_limit.requests_per_second),
                remaining=max(0, int(self.rate_limit.requests_per_second) - second_count),
                context=ErrorContext(generator_name=self.generator_name)
            )
        
        # 检查每分钟限制
        minute_count = await self.counters['minute'].get_count()
        if minute_count >= self.rate_limit.requests_per_minute:
            raise RateLimitError(
                message=f"Requests per minute limit exceeded for {self.generator_name}",
                retry_after=60,
                limit=int(self.rate_limit.requests_per_minute),
                remaining=max(0, int(self.rate_limit.requests_per_minute) - minute_count),
                context=ErrorContext(generator_name=self.generator_name)
            )
        
        # 检查每小时限制
        hour_count = await self.counters['hour'].get_count()
        if hour_count >= self.rate_limit.requests_per_hour:
            raise RateLimitError(
                message=f"Requests per hour limit exceeded for {self.generator_name}",
                retry_after=3600,
                limit=int(self.rate_limit.requests_per_hour),
                remaining=max(0, int(self.rate_limit.requests_per_hour) - hour_count),
                context=ErrorContext(generator_name=self.generator_name)
            )
        
        # 检查每日限制
        day_count = await self.counters['day'].get_count()
        if day_count >= self.rate_limit.requests_per_day:
            raise RateLimitError(
                message=f"Requests per day limit exceeded for {self.generator_name}",
                retry_after=86400,
                limit=int(self.rate_limit.requests_per_day),
                remaining=max(0, int(self.rate_limit.requests_per_day) - day_count),
                context=ErrorContext(generator_name=self.generator_name)
            )
    
    async def _record_request(self) -> None:
        """记录请求"""
        now = time.time()
        
        # 更新计数器
        for counter in self.counters.values():
            await counter.add_request(now)
        
        # 更新统计
        self.usage_stats.total_requests += 1
        
        # 更新时间窗口统计
        self.usage_stats.requests_last_second = await self.counters['second'].get_count()
        self.usage_stats.requests_last_minute = await self.counters['minute'].get_count()
        self.usage_stats.requests_last_hour = await self.counters['hour'].get_count()
        self.usage_stats.requests_last_day = await self.counters['day'].get_count()
    
    async def record_success(self) -> None:
        """记录成功请求"""
        async with self._lock:
            self.usage_stats.successful_requests += 1
            self.usage_stats.daily_usage += 1
            self.usage_stats.monthly_usage += 1
    
    async def record_failure(self, error: Exception) -> None:
        """记录失败请求"""
        async with self._lock:
            self.usage_stats.failed_requests += 1
            
            if isinstance(error, RateLimitError):
                self.usage_stats.rate_limited_requests += 1
            elif isinstance(error, QuotaError):
                self.usage_stats.quota_exceeded_requests += 1
    
    def get_usage_stats(self) -> dict[str, Any]:
        """获取使用统计"""
        return {
            "generator_name": self.generator_name,
            "total_requests": self.usage_stats.total_requests,
            "successful_requests": self.usage_stats.successful_requests,
            "failed_requests": self.usage_stats.failed_requests,
            "rate_limited_requests": self.usage_stats.rate_limited_requests,
            "quota_exceeded_requests": self.usage_stats.quota_exceeded_requests,
            "current_usage": {
                "requests_last_second": self.usage_stats.requests_last_second,
                "requests_last_minute": self.usage_stats.requests_last_minute,
                "requests_last_hour": self.usage_stats.requests_last_hour,
                "requests_last_day": self.usage_stats.requests_last_day,
            },
            "quota_usage": {
                "daily_usage": self.usage_stats.daily_usage,
                "daily_limit": self.rate_limit.daily_quota,
                "monthly_usage": self.usage_stats.monthly_usage,
                "monthly_limit": self.rate_limit.monthly_quota,
            },
            "rate_limits": {
                "requests_per_second": self.rate_limit.requests_per_second,
                "requests_per_minute": self.rate_limit.requests_per_minute,
                "requests_per_hour": self.rate_limit.requests_per_hour,
                "requests_per_day": self.rate_limit.requests_per_day,
                "burst_size": self.rate_limit.burst_size,
            }
        }


class RateLimiterManager:
    """速率限制器管理器"""
    
    def __init__(self):
        self.limiters: dict[str, RateLimiter] = {}
        self._lock = asyncio.Lock()
    
    async def get_limiter(self, generator_name: str, rate_limit: RateLimit) -> RateLimiter:
        """
        获取或创建速率限制器
        
        Args:
            generator_name: 生成器名称
            rate_limit: 速率限制配置
            
        Returns:
            速率限制器实例
        """
        async with self._lock:
            if generator_name not in self.limiters:
                self.limiters[generator_name] = RateLimiter(generator_name, rate_limit)
            return self.limiters[generator_name]
    
    async def acquire(self, generator_name: str, rate_limit: RateLimit) -> None:
        """
        获取请求许可
        
        Args:
            generator_name: 生成器名称
            rate_limit: 速率限制配置
        """
        limiter = await self.get_limiter(generator_name, rate_limit)
        await limiter.acquire()
    
    async def record_success(self, generator_name: str) -> None:
        """记录成功请求"""
        if generator_name in self.limiters:
            await self.limiters[generator_name].record_success()
    
    async def record_failure(self, generator_name: str, error: Exception) -> None:
        """记录失败请求"""
        if generator_name in self.limiters:
            await self.limiters[generator_name].record_failure(error)
    
    def get_all_stats(self) -> dict[str, dict[str, Any]]:
        """获取所有生成器的使用统计"""
        return {
            name: limiter.get_usage_stats()
            for name, limiter in self.limiters.items()
        }


# 全局速率限制器管理器
_rate_limiter_manager: RateLimiterManager | None = None


def get_rate_limiter_manager() -> RateLimiterManager:
    """获取全局速率限制器管理器"""
    global _rate_limiter_manager
    if _rate_limiter_manager is None:
        _rate_limiter_manager = RateLimiterManager()
    return _rate_limiter_manager
