"""
简单的资源管理系统测试
"""

import tempfile
from pathlib import Path

import pytest


def test_resource_manager_import():
    """测试资源管理器导入"""
    from src.mcp_imgutils.common.resource_manager import ResourceMetadata, ResourceType
    assert ResourceMetadata is not None
    assert ResourceType is not None


def test_resource_id_generation():
    """测试资源ID生成"""
    from src.mcp_imgutils.common.resource_manager import generate_resource_id
    
    resource_id1 = generate_resource_id("bfl", "test prompt")
    resource_id2 = generate_resource_id("bfl", "test prompt")
    resource_id3 = generate_resource_id("bfl", "different prompt")
    
    # 相同输入应该生成相同ID
    assert resource_id1 == resource_id2
    
    # 不同输入应该生成不同ID
    assert resource_id1 != resource_id3
    
    # ID应该是16位十六进制字符串
    assert len(resource_id1) == 16


def test_resource_metadata():
    """测试资源元数据"""
    from src.mcp_imgutils.common.resource_manager import (
        ResourceMetadata,
        ResourceStatus,
        ResourceType,
    )
    
    metadata = ResourceMetadata(
        resource_id="test123",
        resource_type=ResourceType.IMAGE,
        status=ResourceStatus.AVAILABLE,
        generator_name="bfl",
        prompt="test prompt"
    )
    
    assert metadata.resource_id == "test123"
    assert metadata.resource_type == ResourceType.IMAGE
    assert metadata.generator_name == "bfl"
    assert metadata.access_count == 0
    
    # 测试访问更新
    metadata.update_access()
    assert metadata.access_count == 1


@pytest.mark.asyncio
async def test_disk_manager_basic():
    """测试磁盘管理器基础功能"""
    from src.mcp_imgutils.common.disk_resource_manager import DiskResourceManager
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = DiskResourceManager(temp_dir)
        
        # 检查目录是否创建
        await manager._ensure_directories()
        assert manager.base_directory.exists()
        assert manager.metadata_directory.exists()
        assert manager.data_directory.exists()


@pytest.mark.asyncio
async def test_memory_cache_basic():
    """测试内存缓存基础功能"""
    from src.mcp_imgutils.common.memory_cache import MemoryCache
    from src.mcp_imgutils.common.resource_manager import (
        ResourceMetadata,
        ResourceStatus,
        ResourceType,
    )
    
    cache = MemoryCache(max_size=1024, max_entries=10)
    
    # 创建测试数据
    test_data = b"test data"
    metadata = ResourceMetadata(
        resource_id="test123",
        resource_type=ResourceType.IMAGE,
        status=ResourceStatus.AVAILABLE
    )
    
    # 存储数据
    success = await cache.put("test_key", test_data, metadata)
    assert success
    
    # 获取数据
    result = await cache.get("test_key")
    assert result is not None
    
    data, retrieved_metadata = result
    assert data == test_data
    assert retrieved_metadata.resource_id == "test123"


def test_resource_factory():
    """测试资源工厂"""
    from src.mcp_imgutils.common.disk_resource_manager import DiskResourceManager
    from src.mcp_imgutils.common.resource_factory import ResourceManagerFactory
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建磁盘管理器
        disk_manager = ResourceManagerFactory.create_resource_manager(
            manager_type="disk",
            base_directory=temp_dir
        )
        assert isinstance(disk_manager, DiskResourceManager)


@pytest.mark.asyncio
async def test_store_and_get_resource():
    """测试存储和获取资源"""
    from src.mcp_imgutils.common.disk_resource_manager import DiskResourceManager
    from src.mcp_imgutils.common.resource_manager import (
        ResourceMetadata,
        ResourceStatus,
        ResourceType,
    )
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = DiskResourceManager(temp_dir)
        
        # 创建测试数据
        resource_id = "test123"
        test_data = b"test image data"
        metadata = ResourceMetadata(
            resource_id=resource_id,
            resource_type=ResourceType.IMAGE,
            status=ResourceStatus.PENDING,
            generator_name="test",
            prompt="test prompt",
            mime_type="image/jpeg"
        )
        
        # 存储资源
        local_path = await manager.store_resource(resource_id, test_data, metadata)
        assert Path(local_path).exists()
        
        # 获取资源
        result = await manager.get_resource(resource_id)
        assert result is not None
        
        data, retrieved_metadata = result
        assert data == test_data
        assert retrieved_metadata.resource_id == resource_id
        assert retrieved_metadata.status == ResourceStatus.AVAILABLE


if __name__ == "__main__":
    pytest.main([__file__])
