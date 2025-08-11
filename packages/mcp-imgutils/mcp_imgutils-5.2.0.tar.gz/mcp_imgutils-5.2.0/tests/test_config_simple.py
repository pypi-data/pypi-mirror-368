"""
简单的配置管理系统测试
"""

import os
from unittest.mock import patch


def test_config_manager_import():
    """测试配置管理器导入"""
    from src.mcp_imgutils.common.config import ConfigManager
    assert ConfigManager is not None


def test_config_manager_creation():
    """测试配置管理器创建"""
    from src.mcp_imgutils.common.config import ConfigManager
    
    config_manager = ConfigManager("test-app")
    assert config_manager.app_name == "test-app"
    assert config_manager._env_prefix == "TEST_APP"


def test_default_config():
    """测试默认配置"""
    from src.mcp_imgutils.common.config import ConfigManager
    
    config_manager = ConfigManager("test-app")
    
    # 检查默认配置
    assert config_manager.get("debug") is False
    assert config_manager.get("log_level") == "INFO"
    assert config_manager.get("timeout") == 60
    assert config_manager.has("image_save_dir")


def test_environment_variables():
    """测试环境变量"""
    from src.mcp_imgutils.common.config import ConfigManager
    
    with patch.dict(os.environ, {
        'TEST_APP_DEBUG': 'true',
        'TEST_APP_API_KEY': 'test-key-123'
    }):
        config_manager = ConfigManager("test-app")
        
        assert config_manager.get("debug") == "true"
        assert config_manager.get("api_key") == "test-key-123"


def test_global_functions():
    """测试全局配置函数"""
    # 清除全局实例
    import src.mcp_imgutils.common.config as config_module
    from src.mcp_imgutils.common.config import get_config, set_config
    config_module._config_manager = None
    
    # 测试设置和获取
    set_config("test_key", "test_value")
    assert get_config("test_key") == "test_value"
    assert get_config("nonexistent_key", "default") == "default"


def test_config_validator_import():
    """测试配置验证器导入"""
    from src.mcp_imgutils.common.config_validator import ConfigValidator
    assert ConfigValidator is not None


def test_bfl_config_integration():
    """测试BFL配置集成"""
    # 清除全局配置
    import src.mcp_imgutils.common.config as config_module
    from src.mcp_imgutils.common.config import set_config
    from src.mcp_imgutils.generation.bfl.framework_generator import BFLFrameworkConfig
    config_module._config_manager = None
    
    # 设置BFL配置
    set_config("bfl.api_key", "test-bfl-key")
    
    # 创建BFL配置
    bfl_config = BFLFrameworkConfig()
    
    # 验证配置被正确加载
    assert bfl_config.api_key == "test-bfl-key"
    assert bfl_config.is_valid()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
