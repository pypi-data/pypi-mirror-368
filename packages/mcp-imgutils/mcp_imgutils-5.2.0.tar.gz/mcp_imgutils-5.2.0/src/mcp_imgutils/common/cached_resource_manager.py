"""
多级缓存资源管理器

结合内存缓存和磁盘存储的多级缓存资源管理器。
"""

import asyncio
import contextlib
import logging
import time
from typing import Any

from .disk_resource_manager import DiskResourceManager
from .memory_cache import MemoryCache
from .resource_manager import (
    ResourceManager,
    ResourceMetadata,
    ResourceType,
)

logger = logging.getLogger(__name__)


class CachedResourceManager(ResourceManager):
    """多级缓存资源管理器"""
    
    def __init__(
        self,
        base_directory: str,
        memory_cache_size: int = 100 * 1024 * 1024,  # 100MB
        memory_cache_entries: int = 1000,
        memory_cache_ttl: float | None = 3600.0,  # 1小时
        disk_cache_ttl: float | None = 86400.0 * 7,  # 7天
    ):
        """
        初始化多级缓存资源管理器
        
        Args:
            base_directory: 磁盘存储基础目录
            memory_cache_size: 内存缓存最大大小
            memory_cache_entries: 内存缓存最大条目数
            memory_cache_ttl: 内存缓存TTL
            disk_cache_ttl: 磁盘缓存TTL
        """
        self.disk_manager = DiskResourceManager(base_directory)
        self.memory_cache = MemoryCache(
            max_size=memory_cache_size,
            max_entries=memory_cache_entries,
            default_ttl=memory_cache_ttl
        )
        self.disk_cache_ttl = disk_cache_ttl

        # 清理任务将在第一次使用时创建
        self._cleanup_task: asyncio.Task | None = None

    def _ensure_cleanup_task(self):
        """确保清理任务已创建"""
        if self._cleanup_task is None:
            with contextlib.suppress(RuntimeError):
                # 没有运行的事件循环时会抛出 RuntimeError
                self._cleanup_task = asyncio.create_task(self._periodic_cleanup())

    async def store_resource(
        self,
        resource_id: str,
        data: bytes,
        metadata: ResourceMetadata
    ) -> str:
        """存储资源"""
        # 确保清理任务已创建
        self._ensure_cleanup_task()

        # 设置过期时间
        if self.disk_cache_ttl and not metadata.expires_at:
            metadata.expires_at = time.time() + self.disk_cache_ttl
        
        # 存储到磁盘
        local_path = await self.disk_manager.store_resource(resource_id, data, metadata)
        
        # 存储到内存缓存
        cache_key = metadata.cache_key or resource_id
        await self.memory_cache.put(cache_key, data, metadata)
        
        logger.debug(f"Stored resource {resource_id} in both disk and memory cache")
        return local_path
    
    async def get_resource(self, resource_id: str) -> tuple[bytes, ResourceMetadata] | None:
        """获取资源"""
        # 首先尝试从内存缓存获取
        result = await self.memory_cache.get(resource_id)
        if result:
            logger.debug(f"Resource {resource_id} found in memory cache")
            return result
        
        # 从磁盘获取
        result = await self.disk_manager.get_resource(resource_id)
        if result:
            data, metadata = result
            
            # 检查磁盘缓存是否过期
            if metadata.is_expired():
                logger.debug(f"Resource {resource_id} expired on disk")
                await self.disk_manager.delete_resource(resource_id)
                return None
            
            # 将数据加载到内存缓存
            cache_key = metadata.cache_key or resource_id
            await self.memory_cache.put(cache_key, data, metadata)
            
            logger.debug(f"Resource {resource_id} loaded from disk to memory cache")
            return result
        
        logger.debug(f"Resource {resource_id} not found")
        return None
    
    async def get_resource_path(self, resource_id: str) -> str | None:
        """获取资源本地路径"""
        # 检查资源是否存在（这会更新访问时间）
        metadata = await self.get_metadata(resource_id)
        if not metadata:
            return None
        
        return await self.disk_manager.get_resource_path(resource_id)
    
    async def get_metadata(self, resource_id: str) -> ResourceMetadata | None:
        """获取资源元数据"""
        return await self.disk_manager.get_metadata(resource_id)
    
    async def delete_resource(self, resource_id: str) -> bool:
        """删除资源"""
        # 从内存缓存删除
        await self.memory_cache.remove(resource_id)
        
        # 从磁盘删除
        return await self.disk_manager.delete_resource(resource_id)
    
    async def list_resources(
        self,
        resource_type: ResourceType | None = None,
        generator_name: str | None = None
    ) -> list[ResourceMetadata]:
        """列出资源"""
        return await self.disk_manager.list_resources(resource_type, generator_name)
    
    async def cleanup_expired(self) -> int:
        """清理过期资源"""
        # 清理内存缓存中的过期项
        memory_cleaned = await self.memory_cache._cleanup_expired()
        
        # 清理磁盘上的过期资源
        disk_cleaned = await self.disk_manager.cleanup_expired()
        
        total_cleaned = memory_cleaned + disk_cleaned
        if total_cleaned > 0:
            logger.info(f"Cleaned up {total_cleaned} expired resources ({memory_cleaned} from memory, {disk_cleaned} from disk)")
        
        return total_cleaned
    
    async def get_storage_stats(self) -> dict[str, Any]:
        """获取存储统计信息"""
        disk_stats = await self.disk_manager.get_storage_stats()
        memory_stats = await self.memory_cache.get_stats()
        
        return {
            "disk": disk_stats,
            "memory": memory_stats,
            "total_resources": disk_stats["resource_count"],
            "cache_efficiency": {
                "hit_rate": memory_stats["hit_rate"],
                "memory_usage": f"{memory_stats['current_size'] / (1024*1024):.2f} MB",
                "disk_usage": f"{disk_stats['total_size'] / (1024*1024):.2f} MB",
            }
        }
    
    async def cleanup_by_size(self, max_disk_size: int, max_memory_size: int | None = None) -> int:
        """
        按大小清理资源
        
        Args:
            max_disk_size: 磁盘最大大小
            max_memory_size: 内存最大大小（可选）
            
        Returns:
            清理的资源数量
        """
        cleaned_count = 0
        
        # 清理磁盘
        if hasattr(self.disk_manager, 'cleanup_by_size'):
            cleaned_count += await self.disk_manager.cleanup_by_size(max_disk_size)
        
        # 清理内存缓存
        if max_memory_size and self.memory_cache.size > max_memory_size:
            # 内存缓存会自动使用LRU策略清理
            pass
        
        return cleaned_count
    
    async def cleanup_by_generator(self, generator_name: str) -> int:
        """
        清理特定生成器的资源
        
        Args:
            generator_name: 生成器名称
            
        Returns:
            清理的资源数量
        """
        cleaned_count = 0
        
        # 清理内存缓存
        memory_cleaned = await self.memory_cache.cleanup_by_generator(generator_name)
        cleaned_count += memory_cleaned
        
        # 清理磁盘资源
        resources = await self.disk_manager.list_resources(generator_name=generator_name)
        for metadata in resources:
            if await self.disk_manager.delete_resource(metadata.resource_id):
                cleaned_count += 1
        
        logger.info(f"Cleaned up {cleaned_count} resources for generator: {generator_name}")
        return cleaned_count
    
    async def preload_to_cache(self, resource_ids: list[str]) -> int:
        """
        预加载资源到内存缓存
        
        Args:
            resource_ids: 资源ID列表
            
        Returns:
            成功预加载的资源数量
        """
        loaded_count = 0
        
        for resource_id in resource_ids:
            try:
                result = await self.disk_manager.get_resource(resource_id)
                if result:
                    data, metadata = result
                    cache_key = metadata.cache_key or resource_id
                    if await self.memory_cache.put(cache_key, data, metadata):
                        loaded_count += 1
            except Exception as e:
                logger.warning(f"Failed to preload resource {resource_id}: {e}")
        
        logger.debug(f"Preloaded {loaded_count} resources to memory cache")
        return loaded_count
    
    async def get_cache_info(self) -> dict[str, Any]:
        """获取缓存详细信息"""
        memory_entries = await self.memory_cache.get_entries_info()
        disk_resources = await self.list_resources()
        
        return {
            "memory_cache": {
                "entries": memory_entries,
                "stats": await self.memory_cache.get_stats(),
            },
            "disk_cache": {
                "resources": [metadata.to_dict() for metadata in disk_resources],
                "stats": await self.disk_manager.get_storage_stats(),
            }
        }
    
    async def _periodic_cleanup(self):
        """定期清理任务"""
        while True:
            try:
                await asyncio.sleep(3600)  # 每小时清理一次
                await self.cleanup_expired()
            except asyncio.CancelledError:
                # 重新抛出 CancelledError 以确保正确的异步取消行为
                raise
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")
    
    async def close(self):
        """关闭资源管理器"""
        if hasattr(self, '_cleanup_task') and self._cleanup_task is not None:
            self._cleanup_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._cleanup_task
        
        await self.memory_cache.clear()
        logger.info("Cached resource manager closed")
    
    def __del__(self):
        """析构函数"""
        if hasattr(self, '_cleanup_task') and self._cleanup_task is not None and not self._cleanup_task.done():
            self._cleanup_task.cancel()
