"""
测试配置管理系统
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.mcp_imgutils.common.config import (
    ConfigManager,
    get_config,
    get_config_manager,
    set_config,
)
from src.mcp_imgutils.common.config_validator import (
    ConfigValidator,
)


class TestConfigManager:
    """测试配置管理器"""
    
    def test_config_manager_creation(self):
        """测试配置管理器创建"""
        config_manager = ConfigManager("test-app")
        assert config_manager.app_name == "test-app"
        assert config_manager._env_prefix == "TEST_APP"
    
    def test_default_config_loading(self):
        """测试默认配置加载"""
        config_manager = ConfigManager("test-app")
        
        # 检查默认配置
        assert config_manager.get("debug") is False
        assert config_manager.get("log_level") == "INFO"
        assert config_manager.get("timeout") == 60
        assert config_manager.get("max_retries") == 3
        assert config_manager.has("image_save_dir")
    
    def test_environment_variable_loading(self):
        """测试环境变量加载"""
        with patch.dict(os.environ, {
            'TEST_APP_DEBUG': 'true',
            'TEST_APP_TIMEOUT': '120',
            'TEST_APP_API_KEY': 'test-key-123'
        }):
            config_manager = ConfigManager("test-app")
            
            assert config_manager.get("debug") == "true"  # 环境变量是字符串
            assert config_manager.get("timeout") == "120"  # 环境变量是字符串
            assert config_manager.get("api_key") == "test-key-123"
            
            # 检查敏感信息标记
            config_value = config_manager.get_config_value("api_key")
            assert config_value.is_sensitive is True
    
    def test_config_file_loading(self):
        """测试配置文件加载"""
        # 创建临时配置文件
        config_data = {
            "debug": True,
            "timeout": 90,
            "bfl": {
                "api_key": "bfl-test-key",
                "model": "flux-dev"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = Path(f.name)
        
        try:
            config_manager = ConfigManager("test-app")
            config_manager._config_files = [config_file]
            config_manager._load_config_files()
            
            assert config_manager.get("debug") is True
            assert config_manager.get("timeout") == 90
            assert config_manager.get("bfl.api_key") == "bfl-test-key"
            assert config_manager.get("bfl.model") == "flux-dev"
            
        finally:
            config_file.unlink()
    
    def test_config_priority(self):
        """测试配置优先级"""
        # 环境变量应该覆盖配置文件
        config_data = {"timeout": 90}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = Path(f.name)
        
        try:
            with patch.dict(os.environ, {'TEST_APP_TIMEOUT': '120'}):
                config_manager = ConfigManager("test-app")
                config_manager._config_files = [config_file]
                config_manager._load_config_files()
                
                # 环境变量优先级更高
                assert config_manager.get("timeout") == "120"
                
        finally:
            config_file.unlink()
    
    def test_config_validation(self):
        """测试配置验证"""
        config_manager = ConfigManager("test-app")
        
        # 测试必需键验证
        required_keys = ["api_key", "base_url"]
        missing_keys = config_manager.validate_required_keys(required_keys)
        assert "api_key" in missing_keys
        assert "base_url" in missing_keys
        
        # 设置配置后再验证
        config_manager.set("api_key", "test-key")
        config_manager.set("base_url", "https://api.test.com")
        
        missing_keys = config_manager.validate_required_keys(required_keys)
        assert len(missing_keys) == 0
    
    def test_config_summary(self):
        """测试配置摘要"""
        config_manager = ConfigManager("test-app")
        config_manager.set("api_key", "secret-key-123", is_sensitive=True)
        config_manager.set("debug", True)
        
        summary = config_manager.get_config_summary()
        
        # 敏感信息应该被遮蔽
        assert "secret-key-123" not in summary["api_key"]["value"]
        assert "***" in summary["api_key"]["value"] or "..." in summary["api_key"]["value"]
        
        # 非敏感信息应该正常显示
        assert summary["debug"]["value"] == "True"


class TestConfigValidator:
    """测试配置验证器"""
    
    def test_validator_creation(self):
        """测试验证器创建"""
        validator = ConfigValidator()
        assert validator.config_manager is not None
    
    def test_generator_config_validation(self):
        """测试生成器配置验证"""
        config_manager = ConfigManager("test-app")
        validator = ConfigValidator(config_manager)
        
        # 测试缺失配置
        is_valid, errors = validator.validate_generator_config("bfl", ["bfl.api_key"])
        assert not is_valid
        assert len(errors) > 0
        assert "Missing required configuration" in errors[0]
        
        # 设置配置后再测试
        config_manager.set("bfl.api_key", "test-bfl-key")
        is_valid, errors = validator.validate_generator_config("bfl", ["bfl.api_key"])
        assert is_valid
        assert len(errors) == 0
    
    def test_api_key_format_validation(self):
        """测试API密钥格式验证"""
        config_manager = ConfigManager("test-app")
        validator = ConfigValidator(config_manager)
        
        # 测试空API密钥
        config_manager.set("bfl.api_key", "")
        is_valid, errors = validator.validate_generator_config("bfl", ["bfl.api_key"])
        assert not is_valid
        
        # 测试过短的API密钥
        config_manager.set("bfl.api_key", "short")
        is_valid, errors = validator.validate_generator_config("bfl", ["bfl.api_key"])
        assert not is_valid
        
        # 测试有效的API密钥
        config_manager.set("bfl.api_key", "valid-api-key-123")
        is_valid, errors = validator.validate_generator_config("bfl", ["bfl.api_key"])
        assert is_valid
    
    def test_configuration_suggestions(self):
        """测试配置建议"""
        config_manager = ConfigManager("test-app")
        validator = ConfigValidator(config_manager)
        
        suggestions = validator.get_configuration_suggestions("bfl")
        assert len(suggestions) > 0
        assert any("BFL" in suggestion for suggestion in suggestions)
        assert any("api.bfl.ai" in suggestion for suggestion in suggestions)
    
    def test_config_report_generation(self):
        """测试配置报告生成"""
        config_manager = ConfigManager("test-app")
        validator = ConfigValidator(config_manager)
        
        report = validator.generate_config_report()
        assert "Configuration Report" in report
        assert "Environment Variables" in report
        assert "MCP_IMGUTILS_" in report


class TestGlobalConfigFunctions:
    """测试全局配置函数"""
    
    def test_global_config_manager(self):
        """测试全局配置管理器"""
        # 清除全局实例
        import src.mcp_imgutils.common.config as config_module
        config_module._config_manager = None
        
        # 获取全局实例
        manager1 = get_config_manager()
        manager2 = get_config_manager()
        
        # 应该是同一个实例
        assert manager1 is manager2
    
    def test_global_config_functions(self):
        """测试全局配置函数"""
        # 清除全局实例
        import src.mcp_imgutils.common.config as config_module
        config_module._config_manager = None
        
        # 测试设置和获取
        set_config("test_key", "test_value")
        assert get_config("test_key") == "test_value"
        assert get_config("nonexistent_key", "default") == "default"
        
        # 测试敏感信息
        set_config("secret_key", "secret_value", is_sensitive=True)
        config_value = get_config_manager().get_config_value("secret_key")
        assert config_value.is_sensitive is True


def test_config_integration():
    """测试配置系统集成"""
    # 这个测试验证配置系统与生成器框架的集成
    # 清除全局配置
    import src.mcp_imgutils.common.config as config_module
    from src.mcp_imgutils.generation.bfl.framework_generator import BFLFrameworkConfig
    config_module._config_manager = None
    
    # 设置BFL配置
    set_config("bfl.api_key", "test-bfl-key")
    set_config("bfl.base_url", "https://test.bfl.ai")
    
    # 创建BFL配置
    bfl_config = BFLFrameworkConfig()
    
    # 验证配置被正确加载
    assert bfl_config.api_key == "test-bfl-key"
    assert bfl_config.base_url == "https://test.bfl.ai"
    assert bfl_config.is_valid()


if __name__ == "__main__":
    pytest.main([__file__])
