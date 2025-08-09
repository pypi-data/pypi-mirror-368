"""
磁盘资源管理器

基于磁盘存储的资源管理器实现。
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

import aiofiles

from .resource_manager import (
    ResourceManager,
    ResourceMetadata,
    ResourceStatus,
    ResourceType,
    ensure_directory,
    get_directory_size,
    get_mime_type_from_extension,
)

logger = logging.getLogger(__name__)


class DiskResourceManager(ResourceManager):
    """磁盘资源管理器"""
    
    def __init__(self, base_directory: str):
        """
        初始化磁盘资源管理器
        
        Args:
            base_directory: 基础存储目录
        """
        self.base_directory = Path(base_directory)
        self.metadata_directory = self.base_directory / "metadata"
        self.data_directory = self.base_directory / "data"
        self._lock = asyncio.Lock()

        # 确保目录存在（延迟到第一次使用时）
        self._directories_ensured = False
    
    async def _ensure_directories(self):
        """确保必要的目录存在"""
        if not self._directories_ensured:
            await ensure_directory(self.base_directory)
            await ensure_directory(self.metadata_directory)
            await ensure_directory(self.data_directory)
            self._directories_ensured = True
    
    def _get_metadata_path(self, resource_id: str) -> Path:
        """获取元数据文件路径"""
        return self.metadata_directory / f"{resource_id}.json"
    
    def _get_data_path(self, resource_id: str, extension: str = "") -> Path:
        """获取数据文件路径"""
        if extension and not extension.startswith('.'):
            extension = f".{extension}"
        return self.data_directory / f"{resource_id}{extension}"
    
    async def store_resource(
        self,
        resource_id: str,
        data: bytes,
        metadata: ResourceMetadata
    ) -> str:
        """存储资源"""
        async with self._lock:
            await self._ensure_directories()
            
            # 确定文件扩展名
            extension = ""
            if metadata.mime_type:
                from .resource_manager import get_extension_from_mime_type
                extension = get_extension_from_mime_type(metadata.mime_type)
            elif metadata.local_path:
                extension = Path(metadata.local_path).suffix
            
            # 存储数据文件
            data_path = self._get_data_path(resource_id, extension)
            async with aiofiles.open(data_path, 'wb') as f:
                await f.write(data)
            
            # 更新元数据
            metadata.local_path = str(data_path)
            metadata.file_size = len(data)
            metadata.status = ResourceStatus.AVAILABLE
            
            if not metadata.mime_type and extension:
                metadata.mime_type = get_mime_type_from_extension(extension)
            
            # 存储元数据
            await self._save_metadata(resource_id, metadata)
            
            logger.debug(f"Stored resource {resource_id} at {data_path}")
            return str(data_path)
    
    async def get_resource(self, resource_id: str) -> tuple[bytes, ResourceMetadata] | None:
        """获取资源"""
        metadata = await self.get_metadata(resource_id)
        if not metadata or not metadata.local_path:
            return None
        
        try:
            async with aiofiles.open(metadata.local_path, 'rb') as f:
                data = await f.read()
            
            # 更新访问信息
            metadata.update_access()
            await self._save_metadata(resource_id, metadata)
            
            return data, metadata
        except (FileNotFoundError, OSError) as e:
            logger.warning(f"Failed to read resource {resource_id}: {e}")
            # 更新状态为错误
            metadata.status = ResourceStatus.ERROR
            await self._save_metadata(resource_id, metadata)
            return None
    
    async def get_resource_path(self, resource_id: str) -> str | None:
        """获取资源本地路径"""
        metadata = await self.get_metadata(resource_id)
        if not metadata or not metadata.local_path:
            return None
        
        # 检查文件是否存在
        if not Path(metadata.local_path).exists():
            logger.warning(f"Resource file not found: {metadata.local_path}")
            metadata.status = ResourceStatus.ERROR
            await self._save_metadata(resource_id, metadata)
            return None
        
        # 更新访问信息
        metadata.update_access()
        await self._save_metadata(resource_id, metadata)
        
        return metadata.local_path
    
    async def get_metadata(self, resource_id: str) -> ResourceMetadata | None:
        """获取资源元数据"""
        metadata_path = self._get_metadata_path(resource_id)
        
        if not metadata_path.exists():
            return None
        
        try:
            async with aiofiles.open(metadata_path, encoding='utf-8') as f:
                data = json.loads(await f.read())
            return ResourceMetadata.from_dict(data)
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to load metadata for {resource_id}: {e}")
            return None
    
    async def _save_metadata(self, resource_id: str, metadata: ResourceMetadata) -> None:
        """保存资源元数据"""
        metadata_path = self._get_metadata_path(resource_id)
        
        try:
            async with aiofiles.open(metadata_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(metadata.to_dict(), indent=2))
        except OSError as e:
            logger.error(f"Failed to save metadata for {resource_id}: {e}")
    
    async def delete_resource(self, resource_id: str) -> bool:
        """删除资源"""
        async with self._lock:
            success = True
            
            # 删除元数据文件
            metadata_path = self._get_metadata_path(resource_id)
            if metadata_path.exists():
                try:
                    metadata_path.unlink()
                except OSError as e:
                    logger.warning(f"Failed to delete metadata {metadata_path}: {e}")
                    success = False
            
            # 删除数据文件
            # 尝试不同的扩展名
            for ext in ['', '.jpg', '.png', '.gif', '.webp', '.txt', '.json']:
                data_path = self._get_data_path(resource_id, ext)
                if data_path.exists():
                    try:
                        data_path.unlink()
                        logger.debug(f"Deleted resource file: {data_path}")
                    except OSError as e:
                        logger.warning(f"Failed to delete data file {data_path}: {e}")
                        success = False
            
            return success
    
    async def list_resources(
        self,
        resource_type: ResourceType | None = None,
        generator_name: str | None = None
    ) -> list[ResourceMetadata]:
        """列出资源"""
        resources = []
        
        if not self.metadata_directory.exists():
            return resources
        
        for metadata_file in self.metadata_directory.glob("*.json"):
            try:
                async with aiofiles.open(metadata_file, encoding='utf-8') as f:
                    data = json.loads(await f.read())
                metadata = ResourceMetadata.from_dict(data)
                
                # 应用过滤器
                if resource_type and metadata.resource_type != resource_type:
                    continue
                if generator_name and metadata.generator_name != generator_name:
                    continue
                
                resources.append(metadata)
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to load metadata from {metadata_file}: {e}")
        
        return resources
    
    async def cleanup_expired(self) -> int:
        """清理过期资源"""
        async with self._lock:
            cleaned_count = 0
            resources = await self.list_resources()
            
            for metadata in resources:
                if (metadata.is_expired() or metadata.status == ResourceStatus.ERROR) and await self.delete_resource(metadata.resource_id):
                    cleaned_count += 1
                    logger.debug(f"Cleaned up expired/error resource: {metadata.resource_id}")
            
            return cleaned_count
    
    async def get_storage_stats(self) -> dict[str, Any]:
        """获取存储统计信息"""
        stats = {
            "base_directory": str(self.base_directory),
            "total_size": 0,
            "metadata_size": 0,
            "data_size": 0,
            "resource_count": 0,
            "resource_types": {},
            "generators": {},
        }
        
        # 计算目录大小
        if self.base_directory.exists():
            stats["total_size"] = await get_directory_size(self.base_directory)
        
        if self.metadata_directory.exists():
            stats["metadata_size"] = await get_directory_size(self.metadata_directory)
        
        if self.data_directory.exists():
            stats["data_size"] = await get_directory_size(self.data_directory)
        
        # 统计资源信息
        resources = await self.list_resources()
        stats["resource_count"] = len(resources)
        
        for metadata in resources:
            # 按类型统计
            type_name = metadata.resource_type.value
            if type_name not in stats["resource_types"]:
                stats["resource_types"][type_name] = 0
            stats["resource_types"][type_name] += 1
            
            # 按生成器统计
            if metadata.generator_name:
                if metadata.generator_name not in stats["generators"]:
                    stats["generators"][metadata.generator_name] = 0
                stats["generators"][metadata.generator_name] += 1
        
        return stats
    
    async def cleanup_by_size(self, max_size: int) -> int:
        """
        按大小清理资源（LRU策略）
        
        Args:
            max_size: 最大允许大小（字节）
            
        Returns:
            清理的资源数量
        """
        current_size = await get_directory_size(self.data_directory)
        if current_size <= max_size:
            return 0
        
        # 获取所有资源，按访问时间排序（最久未访问的在前）
        resources = await self.list_resources()
        resources.sort(key=lambda x: x.accessed_at)
        
        cleaned_count = 0
        for metadata in resources:
            if current_size <= max_size:
                break
            
            if metadata.file_size:
                current_size -= metadata.file_size
            
            if await self.delete_resource(metadata.resource_id):
                cleaned_count += 1
                logger.debug(f"Cleaned up resource for size limit: {metadata.resource_id}")
        
        return cleaned_count
