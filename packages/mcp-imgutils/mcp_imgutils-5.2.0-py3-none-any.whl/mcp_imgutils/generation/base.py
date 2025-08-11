"""
图片生成器基类模块

定义标准化的图片生成器接口，为多模型支持提供统一的抽象层。
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

from mcp import types

from ..common.errors import (
    ErrorContext,
    MCPImageUtilsError,
)
from ..common.rate_limiter import RateLimit, get_rate_limiter_manager
from ..common.resource_factory import get_image, store_image
from ..common.retry import RetryConfig, with_retry


class GenerationStatus(Enum):
    """生成状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class GenerationResult:
    """图片生成结果"""
    status: GenerationStatus
    image_data: bytes | None = None
    image_url: str | None = None
    local_path: str | None = None
    prompt_path: str | None = None
    metadata: dict[str, Any] | None = None
    error_message: str | None = None
    
    @property
    def is_success(self) -> bool:
        """是否生成成功"""
        return self.status == GenerationStatus.COMPLETED and (
            self.image_data is not None or 
            self.image_url is not None or 
            self.local_path is not None
        )


@dataclass
class GeneratorConfig:
    """生成器配置基类"""
    api_key: str | None = None
    base_url: str | None = None
    timeout: int = 60
    max_retries: int = 3
    debug: bool = False

    def __post_init__(self):
        """初始化后处理，从统一配置管理器获取值"""
        from ..common.config import get_config_manager

        config_manager = get_config_manager()

        # 如果没有显式设置，尝试从配置管理器获取
        if self.api_key is None:
            self.api_key = config_manager.get(f"{self.get_config_prefix()}.api_key")

        if self.base_url is None:
            self.base_url = config_manager.get(f"{self.get_config_prefix()}.base_url")

        # 从配置管理器获取通用配置
        self.timeout = config_manager.get("timeout", self.timeout)
        self.max_retries = config_manager.get("max_retries", self.max_retries)
        self.debug = config_manager.get("debug", self.debug)

    def get_config_prefix(self) -> str:
        """
        获取配置前缀，子类应该重写此方法

        Returns:
            配置前缀，如 "bfl", "openai" 等
        """
        return "generator"

    def is_valid(self) -> bool:
        """验证配置是否有效"""
        return self.api_key is not None

    def get_required_keys(self) -> list[str]:
        """
        获取必需的配置键列表

        Returns:
            必需的配置键列表
        """
        return [f"{self.get_config_prefix()}.api_key"]

    def validate(self) -> list[str]:
        """
        验证配置并返回错误信息

        Returns:
            错误信息列表，空列表表示验证通过
        """
        errors = []

        if not self.api_key:
            errors.append(f"Missing required configuration: {self.get_config_prefix()}.api_key")

        if self.timeout <= 0:
            errors.append("Timeout must be positive")

        if self.max_retries < 0:
            errors.append("Max retries must be non-negative")

        return errors


class ImageGenerator(ABC):
    """图片生成器抽象基类"""

    def __init__(self, config: GeneratorConfig):
        """
        初始化生成器

        Args:
            config: 生成器配置
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        self._validate_config()

        # 初始化错误处理组件
        self.retry_config = self.get_retry_config()
        self.rate_limit = self.get_rate_limit()
        self.rate_limiter_manager = get_rate_limiter_manager()
    
    @property
    @abstractmethod
    def name(self) -> str:
        """生成器名称"""
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """生成器显示名称"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """生成器描述"""
        pass

    def get_retry_config(self) -> RetryConfig:
        """
        获取重试配置

        Returns:
            RetryConfig: 重试配置
        """
        return RetryConfig(
            max_attempts=3,
            base_delay=1.0,
            max_delay=60.0
        )

    def get_rate_limit(self) -> RateLimit:
        """
        获取速率限制配置

        Returns:
            RateLimit: 速率限制配置
        """
        return RateLimit(
            requests_per_second=1.0,
            requests_per_minute=60.0,
            requests_per_hour=3600.0,
            burst_size=5
        )

    def create_error_context(self, operation: str = None, **kwargs) -> ErrorContext:
        """
        创建错误上下文

        Args:
            operation: 操作名称
            **kwargs: 额外的上下文数据

        Returns:
            ErrorContext: 错误上下文
        """
        return ErrorContext(
            generator_name=self.name,
            operation=operation,
            user_data=kwargs
        )

    async def _execute_with_error_handling(
        self,
        operation: str,
        func,
        *args,
        **kwargs
    ) -> Any:
        """
        执行操作并处理错误

        Args:
            operation: 操作名称
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数

        Returns:
            函数执行结果
        """
        context = self.create_error_context(operation)

        try:
            # 获取速率限制许可
            await self.rate_limiter_manager.acquire(self.name, self.rate_limit)

            # 执行操作（带重试）
            @with_retry(self.retry_config)
            async def execute():
                return await func(*args, **kwargs)

            result = await execute()

            # 记录成功
            await self.rate_limiter_manager.record_success(self.name)
            self.logger.debug(f"Operation {operation} completed successfully")

            return result

        except Exception as error:
            # 记录失败
            await self.rate_limiter_manager.record_failure(self.name, error)

            # 如果不是我们的错误类型，包装它
            if not isinstance(error, MCPImageUtilsError):
                wrapped_error = MCPImageUtilsError(
                    message=str(error),
                    context=context,
                    cause=error
                )
                self.logger.error(f"Operation {operation} failed: {error}", exc_info=True)
                raise wrapped_error
            else:
                # 更新错误上下文
                if error.context.generator_name is None:
                    error.context.generator_name = self.name
                if error.context.operation is None:
                    error.context.operation = operation

                self.logger.error(f"Operation {operation} failed: {error}")
                raise error

    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        **kwargs
    ) -> GenerationResult:
        """
        生成图片
        
        Args:
            prompt: 图片描述提示词
            **kwargs: 模型特定的参数
            
        Returns:
            GenerationResult: 生成结果
            
        Raises:
            ValueError: 参数无效
            RuntimeError: 生成失败
        """
        pass
    
    @abstractmethod
    def get_tool_definition(self) -> types.Tool:
        """
        获取MCP工具定义
        
        Returns:
            types.Tool: MCP工具定义
        """
        pass
    
    @abstractmethod
    def get_supported_parameters(self) -> dict[str, Any]:
        """
        获取支持的参数列表
        
        Returns:
            Dict[str, Any]: 参数名称和描述的映射
        """
        pass
    
    def _validate_config(self) -> None:
        """
        验证配置
        
        Raises:
            ValueError: 配置无效
        """
        if not self.config.is_valid():
            raise ValueError(f"{self.name} generator configuration is invalid")
    
    def _create_error_result(self, error_message: str) -> GenerationResult:
        """
        创建错误结果
        
        Args:
            error_message: 错误消息
            
        Returns:
            GenerationResult: 错误结果
        """
        return GenerationResult(
            status=GenerationStatus.FAILED,
            error_message=error_message
        )
    
    def _create_success_result(
        self,
        image_data: bytes | None = None,
        image_url: str | None = None,
        local_path: str | None = None,
        prompt_path: str | None = None,
        metadata: dict[str, Any] | None = None
    ) -> GenerationResult:
        """
        创建成功结果
        
        Args:
            image_data: 图片二进制数据
            image_url: 图片URL
            local_path: 本地文件路径
            prompt_path: 提示词文件路径
            metadata: 元数据
            
        Returns:
            GenerationResult: 成功结果
        """
        return GenerationResult(
            status=GenerationStatus.COMPLETED,
            image_data=image_data,
            image_url=image_url,
            local_path=local_path,
            prompt_path=prompt_path,
            metadata=metadata
        )

    async def _store_generated_image(
        self,
        image_data: bytes,
        prompt: str,
        model: str | None = None,
        parameters: dict[str, Any] | None = None,
        **kwargs
    ) -> str:
        """
        存储生成的图片到资源管理器

        Args:
            image_data: 图片数据
            prompt: 提示词
            model: 模型名称
            parameters: 生成参数
            **kwargs: 额外的元数据

        Returns:
            本地路径
        """
        return await store_image(
            generator_name=self.name,
            prompt=prompt,
            image_data=image_data,
            model=model,
            parameters=parameters,
            **kwargs
        )

    async def _get_cached_image(
        self,
        prompt: str,
        parameters: dict[str, Any] | None = None
    ) -> str | None:
        """
        从缓存获取图片

        Args:
            prompt: 提示词
            parameters: 生成参数

        Returns:
            本地路径或None
        """
        return await get_image(
            generator_name=self.name,
            prompt=prompt,
            parameters=parameters
        )


class GeneratorError(Exception):
    """生成器错误基类"""
    
    def __init__(self, message: str, generator_name: str = "unknown"):
        self.message = message
        self.generator_name = generator_name
        super().__init__(f"[{generator_name}] {message}")





class GenerationError(GeneratorError):
    """生成错误"""
    pass


class APIError(GeneratorError):
    """API错误"""
    
    def __init__(self, message: str, status_code: int | None = None, generator_name: str = "unknown"):
        self.status_code = status_code
        super().__init__(message, generator_name)
