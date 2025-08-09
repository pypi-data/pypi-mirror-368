"""
单元测试：图片处理工具函数
"""

from unittest.mock import patch

import pytest

from mcp_imgutils.analysis.utils import get_image_mimetype, validate_image_path


def test_get_image_mimetype():
    """测试获取图片MIME类型功能"""
    assert get_image_mimetype("test.jpg") == "image/jpeg"
    assert get_image_mimetype("test.jpeg") == "image/jpeg"
    assert get_image_mimetype("test.png") == "image/png"
    assert get_image_mimetype("test.gif") == "image/gif"
    assert get_image_mimetype("test.bmp") == "image/bmp"
    assert get_image_mimetype("test.webp") == "image/webp"
    assert get_image_mimetype("test.unknown") == "application/octet-stream"


@patch("mcp_imgutils.analysis.utils.Path")
def test_validate_image_path_not_exists(mock_path):
    """测试验证不存在的图片路径"""
    # 模拟文件不存在
    mock_path_instance = mock_path.return_value
    mock_path_instance.exists.return_value = False

    with pytest.raises(ValueError, match="图片文件不存在"):
        validate_image_path("nonexistent.jpg")


@patch("mcp_imgutils.analysis.utils.Path")
def test_validate_image_path_not_file(mock_path):
    """测试验证非文件的路径"""
    # 模拟路径存在但不是文件
    mock_path_instance = mock_path.return_value
    mock_path_instance.exists.return_value = True
    mock_path_instance.is_file.return_value = False

    with pytest.raises(ValueError, match="路径不是文件"):
        validate_image_path("directory.jpg")


@patch("mcp_imgutils.analysis.utils.Path")
def test_validate_image_path_unsupported_format(mock_path):
    """测试验证不支持的图片格式"""
    # 模拟文件存在但格式不支持
    mock_path_instance = mock_path.return_value
    mock_path_instance.exists.return_value = True
    mock_path_instance.is_file.return_value = True
    mock_path_instance.suffix = ".txt"

    with pytest.raises(ValueError, match="不支持的图片格式"):
        validate_image_path("image.txt")


@patch("mcp_imgutils.analysis.utils.Path")
def test_validate_image_path_valid(mock_path):
    """测试验证有效的图片路径"""
    # 模拟有效的图片文件
    mock_path_instance = mock_path.return_value
    mock_path_instance.exists.return_value = True
    mock_path_instance.is_file.return_value = True
    mock_path_instance.suffix = ".jpg"

    # 不应抛出异常
    validate_image_path("valid.jpg")
