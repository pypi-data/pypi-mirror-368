"""
测试 OpenAI 生成器的 download_path 参数功能
"""

import os
import sys
from unittest.mock import patch

import pytest

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_imgutils.generation.openai.config import (
    OpenAIImageModel,
    _is_safe_path,
    get_image_save_directory,
    validate_model_parameters,
)
from mcp_imgutils.generation.openai.framework_generator import (
    get_openai_tool_definition,
)
from mcp_imgutils.generation.openai.generator import generate_image_openai


class TestDownloadPathConfig:
    """测试下载路径配置功能"""

    def test_default_behavior(self):
        """测试默认行为（不提供自定义路径）"""
        # 清除环境变量
        with patch.dict(os.environ, {}, clear=True):
            default_dir = get_image_save_directory()
            assert "OpenAI_Generated" in default_dir
            assert os.path.expanduser("~") in default_dir

    def test_custom_path_priority(self):
        """测试自定义路径优先级最高"""
        import tempfile
        with tempfile.TemporaryDirectory() as custom_path:
            result_dir = get_image_save_directory(custom_path)
            assert result_dir == custom_path

    def test_environment_variable_priority(self):
        """测试环境变量优先级"""
        import tempfile
        with tempfile.TemporaryDirectory() as env_path, patch.dict(os.environ, {"OPENAI_IMAGE_SAVE_DIR": env_path}):
            result_dir = get_image_save_directory()
            assert result_dir == env_path

    def test_custom_path_overrides_env(self):
        """测试自定义路径覆盖环境变量"""
        import tempfile
        with tempfile.TemporaryDirectory() as env_path, tempfile.TemporaryDirectory() as custom_path, patch.dict(os.environ, {"OPENAI_IMAGE_SAVE_DIR": env_path}):
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


class TestOpenAIModelValidation:
    """测试 OpenAI 模型参数验证"""

    def test_dalle3_valid_parameters(self):
        """测试 DALL-E 3 有效参数"""
        params = validate_model_parameters(
            model=OpenAIImageModel.DALLE_3,
            size="1024x1024",
            quality="standard",
            style="vivid",
            n=1
        )
        
        assert params["model"] == "dall-e-3"
        assert params["size"] == "1024x1024"
        assert params["quality"] == "standard"
        assert params["style"] == "vivid"
        assert params["n"] == 1

    def test_dalle3_invalid_size(self):
        """测试 DALL-E 3 无效尺寸"""
        with pytest.raises(ValueError, match="不支持尺寸"):
            validate_model_parameters(
                model=OpenAIImageModel.DALLE_3,
                size="512x512",  # DALL-E 3 不支持
                n=1
            )

    def test_dalle3_invalid_n(self):
        """测试 DALL-E 3 无效的 n 参数"""
        with pytest.raises(ValueError, match="支持的生成数量范围"):
            validate_model_parameters(
                model=OpenAIImageModel.DALLE_3,
                size="1024x1024",
                n=5  # DALL-E 3 只支持 n=1
            )

    def test_dalle2_valid_parameters(self):
        """测试 DALL-E 2 有效参数"""
        params = validate_model_parameters(
            model=OpenAIImageModel.DALLE_2,
            size="512x512",
            n=3
        )
        
        assert params["model"] == "dall-e-2"
        assert params["size"] == "512x512"
        assert params["n"] == 3
        # DALL-E 2 不应该有 quality/style 参数
        assert "quality" not in params
        assert "style" not in params

    def test_dalle2_quality_not_supported(self):
        """测试 DALL-E 2 不支持 quality 参数"""
        with pytest.raises(ValueError, match="不支持 quality 参数"):
            validate_model_parameters(
                model=OpenAIImageModel.DALLE_2,
                size="512x512",
                quality="hd",  # DALL-E 2 不支持
                n=1
            )

    def test_dalle2_style_not_supported(self):
        """测试 DALL-E 2 不支持 style 参数"""
        with pytest.raises(ValueError, match="不支持 style 参数"):
            validate_model_parameters(
                model=OpenAIImageModel.DALLE_2,
                size="512x512",
                style="natural",  # DALL-E 2 不支持
                n=1
            )


class TestOpenAIFrameworkGenerator:
    """测试 OpenAI 框架生成器的工具定义"""

    def test_tool_definition_includes_download_path(self):
        """测试工具定义包含 download_path 参数"""
        tool_def = get_openai_tool_definition()
        properties = tool_def["inputSchema"]["properties"]
        
        # 验证 download_path 参数存在
        assert "download_path" in properties
        
        # 验证参数定义
        download_path_def = properties["download_path"]
        assert download_path_def["type"] == "string"
        assert "临时指定图片下载保存目录" in download_path_def["description"]

    def test_download_path_is_optional(self):
        """测试 download_path 是可选参数"""
        tool_def = get_openai_tool_definition()
        required_params = tool_def["inputSchema"]["required"]
        
        # 验证 download_path 不在必需参数中
        assert "download_path" not in required_params
        assert "prompt" in required_params  # 确保 prompt 仍然是必需的

    def test_model_parameters_in_tool_definition(self):
        """测试模型参数在工具定义中"""
        tool_def = get_openai_tool_definition()
        properties = tool_def["inputSchema"]["properties"]
        
        # 验证模型参数
        assert "model" in properties
        assert properties["model"]["enum"] == ["dall-e-2", "dall-e-3"]
        assert properties["model"]["default"] == "dall-e-3"
        
        # 验证质量参数
        assert "quality" in properties
        assert properties["quality"]["enum"] == ["standard", "hd"]
        
        # 验证风格参数
        assert "style" in properties
        assert properties["style"]["enum"] == ["vivid", "natural"]
        
        # 验证预设尺寸参数
        assert "preset_size" in properties
        expected_presets = ["default", "square", "landscape", "portrait", "medium", "small"]
        assert properties["preset_size"]["enum"] == expected_presets


class TestOpenAIGeneratorFunction:
    """测试 OpenAI 生成器函数的参数处理"""

    @pytest.mark.asyncio
    async def test_download_path_parameter_parsing(self):
        """测试 download_path 参数解析"""
        import tempfile
        with tempfile.TemporaryDirectory() as test_path:
            arguments = {
                "prompt": "test prompt",
                "download_path": test_path
            }

            # Mock API key to avoid configuration issues
            with patch("mcp_imgutils.generation.openai.generator.get_openai_api_key") as mock_get_api_key:
                mock_get_api_key.side_effect = ValueError("API key not configured")

                result = await generate_image_openai("generate_image_openai", arguments)

                # 应该返回错误信息
                assert len(result) == 1
                assert "API key" in result[0].text or "API密钥" in result[0].text

    @pytest.mark.asyncio
    async def test_missing_prompt_error(self):
        """测试缺少 prompt 参数的错误处理"""
        arguments = {}
        
        result = await generate_image_openai("generate_image_openai", arguments)
        
        # 应该返回错误信息
        assert len(result) == 1
        assert "缺少必需参数: prompt" in result[0].text

    @pytest.mark.asyncio
    async def test_invalid_model_error(self):
        """测试无效模型的错误处理"""
        arguments = {
            "prompt": "test prompt",
            "model": "invalid-model"
        }
        
        result = await generate_image_openai("generate_image_openai", arguments)
        
        # 应该返回错误信息
        assert len(result) == 1
        assert "invalid-model" in result[0].text

    @pytest.mark.asyncio
    async def test_invalid_preset_size_error(self):
        """测试无效预设尺寸的错误处理"""
        arguments = {
            "prompt": "test prompt",
            "preset_size": "invalid-preset"
        }
        
        result = await generate_image_openai("generate_image_openai", arguments)
        
        # 应该返回错误信息
        assert len(result) == 1
        assert "未知的预设尺寸" in result[0].text

    @pytest.mark.asyncio
    async def test_backward_compatibility(self):
        """测试向后兼容性 - 不提供 download_path 参数"""
        arguments = {
            "prompt": "test prompt"
        }
        
        # Mock API key to avoid configuration issues
        with patch("mcp_imgutils.generation.openai.generator.get_openai_api_key") as mock_get_api_key:
            mock_get_api_key.side_effect = ValueError("API key not configured")
            
            result = await generate_image_openai("generate_image_openai", arguments)
            
            # 应该返回错误信息，但参数解析正常
            assert len(result) == 1
            assert "API key" in result[0].text or "API密钥" in result[0].text


class TestIntegration:
    """集成测试"""

    def test_parameter_flow(self):
        """测试参数流转的完整流程"""
        # 这个测试验证参数从工具定义到配置函数的完整流程
        
        # 1. 工具定义包含参数
        tool_def = get_openai_tool_definition()
        assert "download_path" in tool_def["inputSchema"]["properties"]
        
        # 2. 配置函数正确处理参数
        import tempfile
        with tempfile.TemporaryDirectory() as test_path:
            result_path = get_image_save_directory(test_path)
            assert result_path == test_path

            # 3. 参数优先级正确
            with tempfile.TemporaryDirectory() as env_path, patch.dict(os.environ, {"OPENAI_IMAGE_SAVE_DIR": env_path}):
                # 自定义路径应该覆盖环境变量
                result_path = get_image_save_directory(test_path)
                assert result_path == test_path

                # 没有自定义路径时应该使用环境变量
                result_path = get_image_save_directory()
                assert result_path == env_path

    def test_model_configuration_consistency(self):
        """测试模型配置的一致性"""
        from mcp_imgutils.generation.openai.config import MODEL_CONFIGS
        
        # 验证所有枚举模型都有配置
        for model in OpenAIImageModel:
            assert model in MODEL_CONFIGS
            config = MODEL_CONFIGS[model]
            assert len(config.supported_sizes) > 0
            assert config.max_n >= 1
            assert config.price_per_image > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])