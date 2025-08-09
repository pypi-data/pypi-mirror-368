"""
测试资源管理系统
"""

import tempfile
from pathlib import Path

import pytest

from src.mcp_imgutils.common.cached_resource_manager import CachedResourceManager
from src.mcp_imgutils.common.disk_resource_manager import DiskResourceManager
from src.mcp_imgutils.common.memory_cache import MemoryCache
from src.mcp_imgutils.common.resource_factory import (
    ResourceManagerFactory,
    get_image,
    get_resource_manager,
    initialize_resource_manager,
    store_image,
)
from src.mcp_imgutils.common.resource_manager import (
    ResourceMetadata,
    ResourceStatus,
    ResourceType,
    generate_cache_key,
    generate_resource_id,
)


class TestResourceManager:
    """测试资源管理器基础功能"""
    
    def test_resource_id_generation(self):
        """测试资源ID生成"""
        resource_id1 = generate_resource_id("bfl", "test prompt")
        resource_id2 = generate_resource_id("bfl", "test prompt")
        resource_id3 = generate_resource_id("bfl", "different prompt")
        
        # 相同输入应该生成相同ID
        assert resource_id1 == resource_id2
        
        # 不同输入应该生成不同ID
        assert resource_id1 != resource_id3
        
        # ID应该是16位十六进制字符串
        assert len(resource_id1) == 16
        assert all(c in '0123456789abcdef' for c in resource_id1)
    
    def test_cache_key_generation(self):
        """测试缓存键生成"""
        cache_key1 = generate_cache_key("bfl", "test prompt")
        cache_key2 = generate_cache_key("bfl", "test prompt", {"model": "flux-dev"})
        
        # 不同参数应该生成不同缓存键
        assert cache_key1 != cache_key2
    
    def test_resource_metadata(self):
        """测试资源元数据"""
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
        
        # 测试字典转换
        data_dict = metadata.to_dict()
        assert data_dict["resource_id"] == "test123"
        assert data_dict["resource_type"] == "image"
        
        # 测试从字典创建
        new_metadata = ResourceMetadata.from_dict(data_dict)
        assert new_metadata.resource_id == metadata.resource_id
        assert new_metadata.resource_type == metadata.resource_type


class TestDiskResourceManager:
    """测试磁盘资源管理器"""
    
    @pytest.mark.asyncio
    async def test_disk_manager_creation(self):
        """测试磁盘管理器创建"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = DiskResourceManager(temp_dir)
            
            # 检查目录是否创建
            await manager._ensure_directories()
            assert manager.base_directory.exists()
            assert manager.metadata_directory.exists()
            assert manager.data_directory.exists()
    
    @pytest.mark.asyncio
    async def test_store_and_get_resource(self):
        """测试存储和获取资源"""
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
    
    @pytest.mark.asyncio
    async def test_list_and_delete_resources(self):
        """测试列出和删除资源"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = DiskResourceManager(temp_dir)
            
            # 存储多个资源
            for i in range(3):
                resource_id = f"test{i}"
                test_data = f"test data {i}".encode()
                metadata = ResourceMetadata(
                    resource_id=resource_id,
                    resource_type=ResourceType.IMAGE,
                    status=ResourceStatus.PENDING,
                    generator_name="test"
                )
                await manager.store_resource(resource_id, test_data, metadata)
            
            # 列出资源
            resources = await manager.list_resources()
            assert len(resources) == 3
            
            # 按类型过滤
            image_resources = await manager.list_resources(resource_type=ResourceType.IMAGE)
            assert len(image_resources) == 3
            
            # 删除资源
            success = await manager.delete_resource("test0")
            assert success
            
            # 验证删除
            resources = await manager.list_resources()
            assert len(resources) == 2


class TestMemoryCache:
    """测试内存缓存"""
    
    @pytest.mark.asyncio
    async def test_memory_cache_basic(self):
        """测试内存缓存基础功能"""
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
        
        # 获取统计
        stats = await cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 0
        assert stats["current_entries"] == 1
    
    @pytest.mark.asyncio
    async def test_memory_cache_lru(self):
        """测试LRU策略"""
        cache = MemoryCache(max_size=100, max_entries=2)
        
        metadata = ResourceMetadata(
            resource_id="test",
            resource_type=ResourceType.IMAGE,
            status=ResourceStatus.AVAILABLE
        )
        
        # 添加两个条目
        await cache.put("key1", b"data1", metadata)
        await cache.put("key2", b"data2", metadata)
        
        # 添加第三个条目，应该淘汰第一个
        await cache.put("key3", b"data3", metadata)
        
        # 验证第一个条目被淘汰
        result = await cache.get("key1")
        assert result is None
        
        # 验证其他条目仍然存在
        result = await cache.get("key2")
        assert result is not None
        
        result = await cache.get("key3")
        assert result is not None


class TestCachedResourceManager:
    """测试多级缓存资源管理器"""
    
    @pytest.mark.asyncio
    async def test_cached_manager_creation(self):
        """测试缓存管理器创建"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = CachedResourceManager(temp_dir)
            
            assert manager.disk_manager is not None
            assert manager.memory_cache is not None
            
            # 清理
            await manager.close()
    
    @pytest.mark.asyncio
    async def test_cached_manager_store_and_get(self):
        """测试缓存管理器存储和获取"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = CachedResourceManager(temp_dir)
            
            try:
                # 创建测试数据
                resource_id = "test123"
                test_data = b"test image data"
                metadata = ResourceMetadata(
                    resource_id=resource_id,
                    resource_type=ResourceType.IMAGE,
                    status=ResourceStatus.PENDING,
                    generator_name="test",
                    prompt="test prompt"
                )
                
                # 存储资源
                local_path = await manager.store_resource(resource_id, test_data, metadata)
                assert Path(local_path).exists()
                
                # 第一次获取（从磁盘加载到内存）
                result = await manager.get_resource(resource_id)
                assert result is not None
                
                # 第二次获取（从内存缓存）
                result = await manager.get_resource(resource_id)
                assert result is not None
                
                data, retrieved_metadata = result
                assert data == test_data
                
                # 检查缓存统计
                stats = await manager.get_storage_stats()
                assert "disk" in stats
                assert "memory" in stats
                
            finally:
                await manager.close()


class TestResourceFactory:
    """测试资源工厂"""
    
    def test_factory_creation(self):
        """测试工厂创建"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建磁盘管理器
            disk_manager = ResourceManagerFactory.create_resource_manager(
                manager_type="disk",
                base_directory=temp_dir
            )
            assert isinstance(disk_manager, DiskResourceManager)
            
            # 创建缓存管理器
            cached_manager = ResourceManagerFactory.create_resource_manager(
                manager_type="cached",
                base_directory=temp_dir
            )
            assert isinstance(cached_manager, CachedResourceManager)
    
    @pytest.mark.asyncio
    async def test_global_resource_manager(self):
        """测试全局资源管理器"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建管理器
            manager = ResourceManagerFactory.create_resource_manager(
                manager_type="disk",
                base_directory=temp_dir
            )
            
            # 初始化全局管理器
            initialize_resource_manager(manager)
            
            # 获取全局管理器
            global_manager = get_resource_manager()
            assert global_manager is manager
    
    @pytest.mark.asyncio
    async def test_convenience_functions(self):
        """测试便捷函数"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 初始化管理器
            manager = ResourceManagerFactory.create_resource_manager(
                manager_type="disk",
                base_directory=temp_dir
            )
            initialize_resource_manager(manager)
            
            # 测试存储图片
            test_data = b"test image data"
            local_path = await store_image(
                generator_name="test",
                prompt="test prompt",
                image_data=test_data
            )
            assert Path(local_path).exists()
            
            # 测试获取图片
            retrieved_path = await get_image(
                generator_name="test",
                prompt="test prompt"
            )
            assert retrieved_path == local_path


if __name__ == "__main__":
    pytest.main([__file__])
