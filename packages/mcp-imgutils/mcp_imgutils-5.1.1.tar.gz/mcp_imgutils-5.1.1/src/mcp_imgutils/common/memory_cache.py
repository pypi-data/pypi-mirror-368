"""
内存缓存管理器

提供高性能的内存缓存功能，支持LRU和TTL策略。
"""

import asyncio
import logging
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any

from .resource_manager import ResourceMetadata

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    data: bytes
    metadata: ResourceMetadata
    created_at: float
    accessed_at: float
    access_count: int = 0
    
    def update_access(self):
        """更新访问信息"""
        self.accessed_at = time.time()
        self.access_count += 1
    
    def is_expired(self, ttl: float | None = None) -> bool:
        """检查是否过期"""
        if ttl is None:
            return False
        return time.time() - self.created_at > ttl
    
    @property
    def size(self) -> int:
        """获取条目大小"""
        return len(self.data)


class MemoryCache:
    """内存缓存管理器"""
    
    def __init__(
        self,
        max_size: int = 100 * 1024 * 1024,  # 100MB
        max_entries: int = 1000,
        default_ttl: float | None = 3600.0,  # 1小时
    ):
        """
        初始化内存缓存
        
        Args:
            max_size: 最大缓存大小（字节）
            max_entries: 最大缓存条目数
            default_ttl: 默认TTL（秒），None表示不过期
        """
        self.max_size = max_size
        self.max_entries = max_entries
        self.default_ttl = default_ttl
        
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._current_size = 0
        self._lock = asyncio.Lock()
        
        # 统计信息
        self._hits = 0
        self._misses = 0
        self._evictions = 0
    
    async def get(self, key: str) -> tuple[bytes, ResourceMetadata] | None:
        """
        获取缓存项
        
        Args:
            key: 缓存键
            
        Returns:
            (数据, 元数据) 或 None
        """
        async with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._misses += 1
                return None
            
            # 检查是否过期
            if entry.is_expired(self.default_ttl):
                await self._remove_entry(key)
                self._misses += 1
                return None
            
            # 更新访问信息
            entry.update_access()
            
            # 移动到末尾（LRU）
            self._cache.move_to_end(key)
            
            self._hits += 1
            logger.debug(f"Cache hit for key: {key}")
            return entry.data, entry.metadata
    
    async def put(
        self,
        key: str,
        data: bytes,
        metadata: ResourceMetadata,
        ttl: float | None = None
    ) -> bool:
        """
        存储缓存项
        
        Args:
            key: 缓存键
            data: 数据
            metadata: 元数据
            ttl: TTL（秒），None使用默认值
            
        Returns:
            是否存储成功
        """
        if ttl is None:
            ttl = self.default_ttl
        
        data_size = len(data)
        
        # 检查单个条目是否超过最大大小
        if data_size > self.max_size:
            logger.warning(f"Data too large for cache: {data_size} > {self.max_size}")
            return False
        
        async with self._lock:
            now = time.time()
            
            # 如果键已存在，先删除
            if key in self._cache:
                await self._remove_entry(key)
            
            # 确保有足够空间
            await self._ensure_space(data_size)
            
            # 创建新条目
            entry = CacheEntry(
                key=key,
                data=data,
                metadata=metadata,
                created_at=now,
                accessed_at=now
            )
            
            # 添加到缓存
            self._cache[key] = entry
            self._current_size += data_size
            
            logger.debug(f"Cached data for key: {key}, size: {data_size}")
            return True
    
    async def remove(self, key: str) -> bool:
        """
        删除缓存项
        
        Args:
            key: 缓存键
            
        Returns:
            是否删除成功
        """
        async with self._lock:
            return await self._remove_entry(key)
    
    async def _remove_entry(self, key: str) -> bool:
        """删除缓存条目（内部方法）"""
        entry = self._cache.pop(key, None)
        if entry:
            self._current_size -= entry.size
            logger.debug(f"Removed cache entry: {key}")
            return True
        return False
    
    async def _ensure_space(self, needed_size: int) -> None:
        """确保有足够的缓存空间"""
        # 清理过期条目
        await self._cleanup_expired()
        
        # 如果仍然需要更多空间，使用LRU策略清理
        while (
            self._current_size + needed_size > self.max_size or
            len(self._cache) >= self.max_entries
        ):
            if not self._cache:
                break
            
            # 删除最久未使用的条目
            oldest_key = next(iter(self._cache))
            await self._remove_entry(oldest_key)
            self._evictions += 1
    
    async def _cleanup_expired(self) -> int:
        """清理过期条目"""
        if self.default_ttl is None:
            return 0
        
        expired_keys = []
        for key, entry in self._cache.items():
            if entry.is_expired(self.default_ttl):
                expired_keys.append(key)
        
        for key in expired_keys:
            await self._remove_entry(key)
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    async def clear(self) -> None:
        """清空缓存"""
        async with self._lock:
            self._cache.clear()
            self._current_size = 0
            logger.debug("Cache cleared")
    
    async def get_stats(self) -> dict[str, Any]:
        """获取缓存统计信息"""
        async with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0
            
            return {
                "max_size": self.max_size,
                "max_entries": self.max_entries,
                "current_size": self._current_size,
                "current_entries": len(self._cache),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
                "evictions": self._evictions,
                "default_ttl": self.default_ttl,
            }
    
    async def get_entries_info(self) -> list[dict[str, Any]]:
        """获取缓存条目信息"""
        async with self._lock:
            entries_info = []
            for key, entry in self._cache.items():
                entries_info.append({
                    "key": key,
                    "size": entry.size,
                    "created_at": entry.created_at,
                    "accessed_at": entry.accessed_at,
                    "access_count": entry.access_count,
                    "is_expired": entry.is_expired(self.default_ttl),
                    "resource_type": entry.metadata.resource_type.value,
                    "generator_name": entry.metadata.generator_name,
                })
            return entries_info
    
    async def cleanup_by_generator(self, generator_name: str) -> int:
        """
        清理特定生成器的缓存
        
        Args:
            generator_name: 生成器名称
            
        Returns:
            清理的条目数量
        """
        async with self._lock:
            keys_to_remove = []
            for key, entry in self._cache.items():
                if entry.metadata.generator_name == generator_name:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                await self._remove_entry(key)
            
            if keys_to_remove:
                logger.debug(f"Cleaned up {len(keys_to_remove)} cache entries for generator: {generator_name}")
            
            return len(keys_to_remove)
    
    async def cleanup_by_age(self, max_age: float) -> int:
        """
        清理超过指定年龄的缓存
        
        Args:
            max_age: 最大年龄（秒）
            
        Returns:
            清理的条目数量
        """
        async with self._lock:
            now = time.time()
            keys_to_remove = []
            
            for key, entry in self._cache.items():
                if now - entry.created_at > max_age:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                await self._remove_entry(key)
            
            if keys_to_remove:
                logger.debug(f"Cleaned up {len(keys_to_remove)} old cache entries")
            
            return len(keys_to_remove)
    
    def __len__(self) -> int:
        """获取缓存条目数量"""
        return len(self._cache)
    
    @property
    def size(self) -> int:
        """获取当前缓存大小"""
        return self._current_size
