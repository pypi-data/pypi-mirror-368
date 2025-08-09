"""
资源管理器工厂

提供资源管理器的创建和全局管理功能。
"""

import logging
import os
from pathlib import Path
from typing import Any

from .cached_resource_manager import CachedResourceManager
from .config import get_config_manager
from .disk_resource_manager import DiskResourceManager
from .resource_manager import ResourceManager

logger = logging.getLogger(__name__)


class ResourceManagerFactory:
    """资源管理器工厂"""
    
    @staticmethod
    def create_resource_manager(
        manager_type: str = "cached",
        base_directory: str | None = None,
        **kwargs
    ) -> ResourceManager:
        """
        创建资源管理器
        
        Args:
            manager_type: 管理器类型 ("disk", "cached")
            base_directory: 基础存储目录
            **kwargs: 额外配置参数
            
        Returns:
            资源管理器实例
        """
        if base_directory is None:
            base_directory = ResourceManagerFactory._get_default_directory()
        
        if manager_type == "disk":
            return DiskResourceManager(base_directory)
        elif manager_type == "cached":
            return CachedResourceManager(base_directory, **kwargs)
        else:
            raise ValueError(f"Unknown resource manager type: {manager_type}")
    
    @staticmethod
    def _get_default_directory() -> str:
        """获取默认存储目录"""
        config_manager = get_config_manager()
        
        # 尝试从配置获取
        base_dir = config_manager.get("resource_manager.base_directory")
        if base_dir:
            return base_dir
        
        # 使用图片保存目录
        image_dir = config_manager.get("image_save_dir")
        if image_dir:
            return str(Path(image_dir) / "cache")
        
        # 默认目录
        home = Path.home()
        if os.name == "nt":  # Windows
            default_dir = home / "AppData" / "Local" / "MCP-ImageUtils" / "cache"
        else:  # macOS/Linux
            default_dir = home / ".cache" / "mcp-imgutils"
        
        return str(default_dir)
    
    @staticmethod
    def create_from_config() -> ResourceManager:
        """从配置创建资源管理器"""
        config_manager = get_config_manager()
        
        # 获取配置
        manager_type = config_manager.get("resource_manager.type", "cached")
        base_directory = config_manager.get("resource_manager.base_directory")
        
        # 缓存配置
        cache_config = {}
        if manager_type == "cached":
            cache_config.update({
                "memory_cache_size": config_manager.get("resource_manager.memory_cache_size", 100 * 1024 * 1024),
                "memory_cache_entries": config_manager.get("resource_manager.memory_cache_entries", 1000),
                "memory_cache_ttl": config_manager.get("resource_manager.memory_cache_ttl", 3600.0),
                "disk_cache_ttl": config_manager.get("resource_manager.disk_cache_ttl", 86400.0 * 7),
            })
        
        return ResourceManagerFactory.create_resource_manager(
            manager_type=manager_type,
            base_directory=base_directory,
            **cache_config
        )


class GlobalResourceManager:
    """全局资源管理器"""
    
    def __init__(self):
        self._manager: ResourceManager | None = None
        self._initialized = False
    
    def initialize(self, manager: ResourceManager | None = None) -> None:
        """
        初始化全局资源管理器
        
        Args:
            manager: 资源管理器实例，如果为None则从配置创建
        """
        if self._initialized:
            logger.warning("Global resource manager already initialized")
            return
        
        if manager is None:
            manager = ResourceManagerFactory.create_from_config()
        
        self._manager = manager
        self._initialized = True
        logger.info(f"Global resource manager initialized: {type(manager).__name__}")
    
    def get_manager(self) -> ResourceManager:
        """
        获取全局资源管理器
        
        Returns:
            资源管理器实例
            
        Raises:
            RuntimeError: 如果未初始化
        """
        if not self._initialized or self._manager is None:
            # 自动初始化
            self.initialize()
        
        return self._manager
    
    async def close(self) -> None:
        """关闭全局资源管理器"""
        if self._manager and hasattr(self._manager, 'close'):
            await self._manager.close()
        
        self._manager = None
        self._initialized = False
        logger.info("Global resource manager closed")
    
    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._initialized


# 全局实例
_global_resource_manager = GlobalResourceManager()


def get_resource_manager() -> ResourceManager:
    """
    获取全局资源管理器
    
    Returns:
        资源管理器实例
    """
    return _global_resource_manager.get_manager()


def initialize_resource_manager(manager: ResourceManager | None = None) -> None:
    """
    初始化全局资源管理器
    
    Args:
        manager: 资源管理器实例，如果为None则从配置创建
    """
    _global_resource_manager.initialize(manager)


async def close_resource_manager() -> None:
    """关闭全局资源管理器"""
    await _global_resource_manager.close()


def is_resource_manager_initialized() -> bool:
    """检查全局资源管理器是否已初始化"""
    return _global_resource_manager.is_initialized()


# 便捷函数
async def store_image(
    generator_name: str,
    prompt: str,
    image_data: bytes,
    model: str | None = None,
    parameters: dict[str, Any] | None = None,
    **kwargs
) -> str:
    """
    存储图片资源
    
    Args:
        generator_name: 生成器名称
        prompt: 提示词
        image_data: 图片数据
        model: 模型名称
        parameters: 生成参数
        **kwargs: 额外的元数据
        
    Returns:
        本地路径
    """
    from .resource_manager import (
        ResourceMetadata,
        ResourceStatus,
        ResourceType,
        generate_cache_key,
        generate_resource_id,
    )
    
    # 生成资源ID
    resource_id = generate_resource_id(generator_name, prompt, parameters)
    
    # 创建元数据
    metadata = ResourceMetadata(
        resource_id=resource_id,
        resource_type=ResourceType.IMAGE,
        status=ResourceStatus.PENDING,
        generator_name=generator_name,
        prompt=prompt,
        model=model,
        parameters=parameters,
        cache_key=generate_cache_key(generator_name, prompt, parameters),
        mime_type="image/jpeg",  # 默认JPEG
        **kwargs
    )
    
    # 存储资源
    manager = get_resource_manager()
    return await manager.store_resource(resource_id, image_data, metadata)


async def get_image(
    generator_name: str,
    prompt: str,
    parameters: dict[str, Any] | None = None
) -> str | None:
    """
    获取图片资源路径
    
    Args:
        generator_name: 生成器名称
        prompt: 提示词
        parameters: 生成参数
        
    Returns:
        本地路径或None
    """
    from .resource_manager import generate_resource_id
    
    # 生成资源ID
    resource_id = generate_resource_id(generator_name, prompt, parameters)
    
    # 获取资源路径
    manager = get_resource_manager()
    return await manager.get_resource_path(resource_id)


async def cleanup_resources(
    max_age_hours: float | None = None,
    max_disk_size_mb: float | None = None,
    generator_name: str | None = None
) -> int:
    """
    清理资源
    
    Args:
        max_age_hours: 最大年龄（小时）
        max_disk_size_mb: 最大磁盘大小（MB）
        generator_name: 特定生成器名称
        
    Returns:
        清理的资源数量
    """
    manager = get_resource_manager()
    cleaned_count = 0
    
    # 清理过期资源
    cleaned_count += await manager.cleanup_expired()
    
    # 按生成器清理
    if generator_name and hasattr(manager, 'cleanup_by_generator'):
        cleaned_count += await manager.cleanup_by_generator(generator_name)
    
    # 按大小清理
    if max_disk_size_mb and hasattr(manager, 'cleanup_by_size'):
        max_size = int(max_disk_size_mb * 1024 * 1024)
        cleaned_count += await manager.cleanup_by_size(max_size)
    
    # 按年龄清理（如果是缓存管理器）
    if max_age_hours and hasattr(manager, 'memory_cache'):
        max_age_seconds = max_age_hours * 3600
        if hasattr(manager.memory_cache, 'cleanup_by_age'):
            cleaned_count += await manager.memory_cache.cleanup_by_age(max_age_seconds)
    
    return cleaned_count


async def get_resource_stats() -> dict[str, Any]:
    """
    获取资源统计信息
    
    Returns:
        资源统计信息
    """
    manager = get_resource_manager()
    return await manager.get_storage_stats()
