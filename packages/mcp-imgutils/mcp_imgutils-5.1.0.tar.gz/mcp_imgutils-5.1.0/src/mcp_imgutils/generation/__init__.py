"""
图片生成模块

提供多种模型的图片生成功能和统一的框架接口。
"""

import logging

# 框架基础
from .base import (
    APIError,
    GenerationError,
    GenerationResult,
    GenerationStatus,
    GeneratorConfig,
    GeneratorError,
    ImageGenerator,
)

# 保持向后兼容
from .bfl import generate_image_bfl

# BFL 图片生成器相关模块
from .bfl.framework_generator import BFLFrameworkConfig, BFLFrameworkGenerator
from .bfl.generator import get_bfl_tool_definition
from .registry import GeneratorRegistry, get_registry, register_generator

__all__ = [
    # 框架基础
    "ImageGenerator",
    "GeneratorConfig",
    "GenerationResult",
    "GenerationStatus",
    "GeneratorError",
    "GenerationError",
    "APIError",

    # 注册系统
    "GeneratorRegistry",
    "register_generator",
    "get_registry",

    # BFL 图片生成器
    "BFLFrameworkGenerator",
    "BFLFrameworkConfig",

    # 向后兼容
    "generate_image_bfl",
    "get_bfl_tool_definition",
]


def initialize_generators():
    """初始化所有生成器"""
    registry = get_registry()

    # 注册BFL生成器
    register_generator("bfl", BFLFrameworkGenerator)

    # 尝试创建BFL生成器实例（如果配置有效）
    try:
        bfl_config = BFLFrameworkConfig()
        if bfl_config.is_valid():
            registry.create_generator("bfl", bfl_config)
    except (ImportError, ValueError, KeyError) as e:
        # 配置无效时静默失败，用户可以稍后手动配置
        logger = logging.getLogger(__name__)
        logger.debug(f"Failed to initialize BFL generator: {e}")
