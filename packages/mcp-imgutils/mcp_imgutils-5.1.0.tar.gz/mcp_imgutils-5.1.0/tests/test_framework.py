"""
测试新的生成器框架
"""



def test_basic_import():
    """测试基础导入"""
    from src.mcp_imgutils.generation import GeneratorRegistry
    assert GeneratorRegistry is not None


def test_registry_creation():
    """测试注册表创建"""
    from src.mcp_imgutils.generation import GeneratorRegistry
    registry = GeneratorRegistry()
    assert registry is not None
    assert len(registry.list_registered_classes()) == 0


def test_bfl_config():
    """测试BFL配置"""
    from src.mcp_imgutils.generation import BFLFrameworkConfig
    config = BFLFrameworkConfig(api_key="test-key")
    assert config.api_key == "test-key"
    assert config.is_valid()


def test_global_registry():
    """测试全局注册表"""
    from src.mcp_imgutils.generation import get_registry
    registry = get_registry()
    assert registry is not None


def test_initialize_generators():
    """测试初始化生成器"""
    from src.mcp_imgutils.generation import initialize_generators

    # 初始化生成器
    initialize_generators()

    # 应该不会抛出异常
    assert True
