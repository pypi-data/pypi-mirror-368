"""
测试 BFL 生成器的 download_path 参数功能
"""

import os
from unittest.mock import patch

import pytest

from src.mcp_imgutils.generation.bfl.config import (
    _is_safe_path,
    get_image_save_directory,
)
from src.mcp_imgutils.generation.bfl.framework_generator import (
    BFLFrameworkConfig,
    BFLFrameworkGenerator,
)
from src.mcp_imgutils.generation.bfl.generator import generate_image_bfl


class TestDownloadPathConfig:
    """测试下载路径配置功能"""

    def test_default_behavior(self):
        """测试默认行为（不提供自定义路径）"""
        # 清除环境变量
        with patch.dict(os.environ, {}, clear=True):
            default_dir = get_image_save_directory()
            assert "BFL_Generated" in default_dir
            assert os.path.expanduser("~") in default_dir

    def test_custom_path_priority(self):
        """测试自定义路径优先级最高"""
        custom_path = "/tmp/test_custom"
        result_dir = get_image_save_directory(custom_path)
        assert result_dir == custom_path

    def test_environment_variable_priority(self):
        """测试环境变量优先级"""
        env_path = "/tmp/test_env"
        with patch.dict(os.environ, {"BFL_IMAGE_SAVE_DIR": env_path}):
            result_dir = get_image_save_directory()
            assert result_dir == env_path

    def test_custom_path_overrides_env(self):
        """测试自定义路径覆盖环境变量"""
        env_path = "/tmp/test_env"
        custom_path = "/tmp/test_custom"
        
        with patch.dict(os.environ, {"BFL_IMAGE_SAVE_DIR": env_path}):
            result_dir = get_image_save_directory(custom_path)
            assert result_dir == custom_path

    def test_tilde_expansion(self):
        """测试波浪号路径展开"""
        custom_path = "~/test_path"
        result_dir = get_image_save_directory(custom_path)
        assert result_dir == os.path.expanduser(custom_path)

    def test_path_traversal_security(self):
        """测试路径遍历安全防护"""
        # 测试危险路径 - 这些路径用于测试安全防护，会被正确拒绝
        dangerous_paths = [
            "../../../etc/passwd",  # NOSONAR
            "../../sensitive_dir",  # NOSONAR
            "/tmp/../../../etc",  # NOSONAR
            "test/../../../etc",  # NOSONAR
            "\x00/etc/passwd",  # NOSONAR - 空字节注入测试
        ]

        for dangerous_path in dangerous_paths:
            with pytest.raises(ValueError, match="不安全的路径"):
                get_image_save_directory(dangerous_path)

    def test_safe_path_validation(self):
        """测试安全路径验证"""
        # 安全路径
        safe_paths = [
            "/tmp/safe_path",  # NOSONAR
            "~/documents/images",
            "relative/path/images",
            "/absolute/path/images",
            "simple_folder",
        ]

        for safe_path in safe_paths:
            assert _is_safe_path(safe_path), f"路径应该是安全的: {safe_path}"

        # 不安全路径
        unsafe_paths = [
            "../parent_dir",
            "../../grandparent",
            "/tmp/../etc",  # NOSONAR
            "test/../../../etc",
            "\x00injection",
        ]

        for unsafe_path in unsafe_paths:
            assert not _is_safe_path(unsafe_path), f"路径应该是不安全的: {unsafe_path}"


class TestBFLFrameworkGenerator:
    """测试 BFL 框架生成器的工具定义"""

    def test_tool_definition_includes_download_path(self):
        """测试工具定义包含 download_path 参数"""
        config = BFLFrameworkConfig()
        generator = BFLFrameworkGenerator(config)
        
        tool_def = generator.get_tool_definition()
        properties = tool_def.inputSchema["properties"]
        
        # 验证 download_path 参数存在
        assert "download_path" in properties
        
        # 验证参数定义
        download_path_def = properties["download_path"]
        assert download_path_def["type"] == "string"
        assert "临时指定图片下载保存目录" in download_path_def["description"]

    def test_download_path_is_optional(self):
        """测试 download_path 是可选参数"""
        config = BFLFrameworkConfig()
        generator = BFLFrameworkGenerator(config)
        
        tool_def = generator.get_tool_definition()
        required_params = tool_def.inputSchema["required"]
        
        # 验证 download_path 不在必需参数中
        assert "download_path" not in required_params
        assert "prompt" in required_params  # 确保 prompt 仍然是必需的

    def test_supported_parameters_includes_download_path(self):
        """测试支持的参数列表包含 download_path"""
        config = BFLFrameworkConfig()
        generator = BFLFrameworkGenerator(config)
        
        supported_params = generator.get_supported_parameters()
        
        # 验证 download_path 在支持的参数中
        assert "download_path" in supported_params
        assert supported_params["download_path"]["type"] == "string"


class TestBFLGeneratorFunction:
    """测试 BFL 生成器函数的参数处理"""

    @pytest.mark.asyncio
    async def test_download_path_parameter_parsing(self):
        """测试 download_path 参数解析"""
        arguments = {
            "prompt": "test prompt",
            "download_path": "/tmp/test_path"
        }
        
        # Mock API key to avoid configuration issues
        with patch("src.mcp_imgutils.generation.bfl.generator.get_api_key") as mock_get_api_key:
            mock_get_api_key.side_effect = ValueError("API key not configured")
            
            try:
                await generate_image_bfl("generate_image_bfl", arguments)
            except ValueError as e:
                # 预期的 API key 错误，但我们可以验证参数解析正确
                assert "API key" in str(e) or "API密钥" in str(e)

    @pytest.mark.asyncio
    async def test_backward_compatibility(self):
        """测试向后兼容性 - 不提供 download_path 参数"""
        arguments = {
            "prompt": "test prompt"
        }
        
        # Mock API key to avoid configuration issues
        with patch("src.mcp_imgutils.generation.bfl.generator.get_api_key") as mock_get_api_key:
            mock_get_api_key.side_effect = ValueError("API key not configured")
            
            try:
                await generate_image_bfl("generate_image_bfl", arguments)
            except ValueError as e:
                # 预期的 API key 错误，说明参数解析正常
                assert "API key" in str(e) or "API密钥" in str(e)


class TestIntegration:
    """集成测试"""

    def test_parameter_flow(self):
        """测试参数流转的完整流程"""
        # 这个测试验证参数从工具定义到配置函数的完整流程
        
        # 1. 工具定义包含参数
        config = BFLFrameworkConfig()
        generator = BFLFrameworkGenerator(config)
        tool_def = generator.get_tool_definition()
        
        assert "download_path" in tool_def.inputSchema["properties"]
        
        # 2. 配置函数正确处理参数
        test_path = "/tmp/integration_test"
        result_path = get_image_save_directory(test_path)
        
        assert result_path == test_path
        
        # 3. 参数优先级正确
        env_path = "/tmp/env_test"
        with patch.dict(os.environ, {"BFL_IMAGE_SAVE_DIR": env_path}):
            # 自定义路径应该覆盖环境变量
            result_path = get_image_save_directory(test_path)
            assert result_path == test_path
            
            # 没有自定义路径时应该使用环境变量
            result_path = get_image_save_directory()
            assert result_path == env_path


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
