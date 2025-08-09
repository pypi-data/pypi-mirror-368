"""
统一资源管理系统

提供图片资源的统一管理、缓存、清理和元数据管理。
"""

import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """资源类型枚举"""
    IMAGE = "image"
    PROMPT = "prompt"
    METADATA = "metadata"
    CACHE = "cache"


class ResourceStatus(Enum):
    """资源状态枚举"""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    AVAILABLE = "available"
    EXPIRED = "expired"
    ERROR = "error"


@dataclass
class ResourceMetadata:
    """资源元数据"""
    resource_id: str
    resource_type: ResourceType
    status: ResourceStatus
    
    # 基本信息
    original_url: str | None = None
    local_path: str | None = None
    file_size: int | None = None
    mime_type: str | None = None
    
    # 时间信息
    created_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    
    # 生成信息
    generator_name: str | None = None
    prompt: str | None = None
    model: str | None = None
    parameters: dict[str, Any] | None = None
    
    # 缓存信息
    cache_key: str | None = None
    access_count: int = 0
    
    def update_access(self):
        """更新访问时间和次数"""
        self.accessed_at = time.time()
        self.access_count += 1
    
    def is_expired(self) -> bool:
        """检查资源是否过期"""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        # 转换枚举为字符串
        data['resource_type'] = self.resource_type.value
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'ResourceMetadata':
        """从字典创建"""
        # 转换字符串为枚举
        data['resource_type'] = ResourceType(data['resource_type'])
        data['status'] = ResourceStatus(data['status'])
        return cls(**data)


class ResourceManager(ABC):
    """资源管理器抽象基类"""
    
    @abstractmethod
    async def store_resource(
        self,
        resource_id: str,
        data: bytes,
        metadata: ResourceMetadata
    ) -> str:
        """
        存储资源
        
        Args:
            resource_id: 资源ID
            data: 资源数据
            metadata: 资源元数据
            
        Returns:
            本地路径
        """
        pass
    
    @abstractmethod
    async def get_resource(self, resource_id: str) -> tuple[bytes, ResourceMetadata] | None:
        """
        获取资源
        
        Args:
            resource_id: 资源ID
            
        Returns:
            (资源数据, 元数据) 或 None
        """
        pass
    
    @abstractmethod
    async def get_resource_path(self, resource_id: str) -> str | None:
        """
        获取资源本地路径
        
        Args:
            resource_id: 资源ID
            
        Returns:
            本地路径或None
        """
        pass
    
    @abstractmethod
    async def get_metadata(self, resource_id: str) -> ResourceMetadata | None:
        """
        获取资源元数据
        
        Args:
            resource_id: 资源ID
            
        Returns:
            资源元数据或None
        """
        pass
    
    @abstractmethod
    async def delete_resource(self, resource_id: str) -> bool:
        """
        删除资源
        
        Args:
            resource_id: 资源ID
            
        Returns:
            是否删除成功
        """
        pass
    
    @abstractmethod
    async def list_resources(
        self,
        resource_type: ResourceType | None = None,
        generator_name: str | None = None
    ) -> list[ResourceMetadata]:
        """
        列出资源
        
        Args:
            resource_type: 资源类型过滤
            generator_name: 生成器名称过滤
            
        Returns:
            资源元数据列表
        """
        pass
    
    @abstractmethod
    async def cleanup_expired(self) -> int:
        """
        清理过期资源
        
        Returns:
            清理的资源数量
        """
        pass
    
    @abstractmethod
    async def get_storage_stats(self) -> dict[str, Any]:
        """
        获取存储统计信息
        
        Returns:
            存储统计信息
        """
        pass


def generate_resource_id(
    generator_name: str,
    prompt: str,
    parameters: dict[str, Any] | None = None
) -> str:
    """
    生成资源ID
    
    Args:
        generator_name: 生成器名称
        prompt: 提示词
        parameters: 参数
        
    Returns:
        资源ID
    """
    # 创建唯一标识符
    content = f"{generator_name}:{prompt}"
    if parameters:
        # 排序参数以确保一致性
        sorted_params = json.dumps(parameters, sort_keys=True)
        content += f":{sorted_params}"
    
    # 生成哈希
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def generate_cache_key(
    generator_name: str,
    prompt: str,
    parameters: dict[str, Any] | None = None
) -> str:
    """
    生成缓存键
    
    Args:
        generator_name: 生成器名称
        prompt: 提示词
        parameters: 参数
        
    Returns:
        缓存键
    """
    return generate_resource_id(generator_name, prompt, parameters)


def get_resource_filename(
    resource_id: str,
    resource_type: ResourceType,
    extension: str = ""
) -> str:
    """
    生成资源文件名
    
    Args:
        resource_id: 资源ID
        resource_type: 资源类型
        extension: 文件扩展名
        
    Returns:
        文件名
    """
    if not extension.startswith('.') and extension:
        extension = f".{extension}"
    
    return f"{resource_type.value}_{resource_id}{extension}"


def get_mime_type_from_extension(extension: str) -> str:
    """
    根据扩展名获取MIME类型
    
    Args:
        extension: 文件扩展名
        
    Returns:
        MIME类型
    """
    extension = extension.lower()
    if not extension.startswith('.'):
        extension = f".{extension}"
    
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.bmp': 'image/bmp',
        '.txt': 'text/plain',
        '.json': 'application/json',
    }
    
    return mime_types.get(extension, 'application/octet-stream')


def get_extension_from_mime_type(mime_type: str) -> str:
    """
    根据MIME类型获取扩展名
    
    Args:
        mime_type: MIME类型
        
    Returns:
        文件扩展名
    """
    mime_to_ext = {
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
        'image/webp': '.webp',
        'image/bmp': '.bmp',
        'text/plain': '.txt',
        'application/json': '.json',
    }
    
    return mime_to_ext.get(mime_type.lower(), '.bin')


async def ensure_directory(path: str | Path) -> None:
    """
    确保目录存在
    
    Args:
        path: 目录路径
    """
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created directory: {path}")


async def get_file_size(path: str | Path) -> int:
    """
    获取文件大小
    
    Args:
        path: 文件路径
        
    Returns:
        文件大小（字节）
    """
    try:
        return Path(path).stat().st_size
    except (OSError, FileNotFoundError):
        return 0


async def get_directory_size(path: str | Path) -> int:
    """
    获取目录大小
    
    Args:
        path: 目录路径
        
    Returns:
        目录大小（字节）
    """
    total_size = 0
    path = Path(path)
    
    if not path.exists():
        return 0
    
    try:
        for file_path in path.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
    except (OSError, PermissionError):
        pass
    
    return total_size
