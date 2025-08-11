"""
OpenAI 生成器简单测试
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_imgutils.generation.openai.config import (
    OpenAIImageModel,
    get_image_save_directory,
)
from mcp_imgutils.generation.openai.framework_generator import (
    get_openai_tool_definition,
)


def test_openai_models():
    """测试 OpenAI 模型枚举"""
    models = [model.value for model in OpenAIImageModel]
    assert "dall-e-2" in models
    assert "dall-e-3" in models


def test_tool_definition():
    """测试工具定义"""
    tool_def = get_openai_tool_definition()
    assert tool_def["name"] == "generate_image_openai"
    assert "prompt" in tool_def["inputSchema"]["required"]
    assert "download_path" in tool_def["inputSchema"]["properties"]


def test_default_directory():
    """测试默认目录"""
    import os
    from unittest.mock import patch
    
    with patch.dict(os.environ, {}, clear=True):
        default_dir = get_image_save_directory()
        assert "OpenAI_Generated" in default_dir


if __name__ == "__main__":
    pytest.main([__file__, "-v"])