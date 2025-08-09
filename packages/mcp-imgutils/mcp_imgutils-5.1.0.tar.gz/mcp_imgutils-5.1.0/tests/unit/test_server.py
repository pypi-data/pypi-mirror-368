"""
单元测试：MCP服务器功能
"""

from unittest.mock import patch

import pytest

from mcp_imgutils.analysis import view_image
from mcp_imgutils.server import get_server


def test_get_server_singleton():
    """测试服务器单例模式"""
    server1 = get_server()
    server2 = get_server()
    assert server1 is server2


@pytest.mark.asyncio
@patch("mcp_imgutils.analysis.viewer.is_url")
@patch("mcp_imgutils.analysis.viewer.validate_image_path")
@patch("mcp_imgutils.analysis.viewer.read_and_encode_image")
@patch("mcp_imgutils.analysis.viewer.get_image_details")
@patch("os.path.getsize")
async def test_view_image_success(
    mock_getsize, mock_get_details, mock_read_encode, mock_validate, mock_is_url
):
    """测试成功查看图片"""
    # 模拟不是URL，是本地文件
    mock_is_url.return_value = False
    # 模拟文件大小和成功读取编码
    mock_getsize.return_value = 1024  # 1KB
    mock_read_encode.return_value = ("base64_encoded_data", "image/jpeg")
    mock_get_details.return_value = {
        "文件路径": "/path/to/image.jpg",
        "文件大小": "1,024 字节",
        "图片格式": "JPEG",
        "颜色模式": "RGB",
        "尺寸": "100 x 100",
        "总像素数": "10,000",
    }

    result = await view_image("view_image", {"image_path": "/path/to/image.jpg"})

    # 验证调用
    mock_validate.assert_called_once_with("/path/to/image.jpg")
    mock_read_encode.assert_called_once_with("/path/to/image.jpg")

    # 验证结果 - 现在返回文本信息 + 图片数据
    assert len(result) == 2

    # 验证文本内容
    assert result[0].type == "text"
    assert "图片详细信息:" in result[0].text

    # 验证图片内容
    assert result[1].type == "image"
    assert result[1].data == "base64_encoded_data"
    assert result[1].mimeType == "image/jpeg"


@pytest.mark.asyncio
async def test_view_image_invalid_tool():
    """测试无效的工具名称"""
    with pytest.raises(ValueError, match="未知工具"):
        await view_image("invalid_tool", {"image_path": "/path/to/image.jpg"})


@pytest.mark.asyncio
async def test_view_image_missing_path():
    """测试缺少图片路径参数"""
    with pytest.raises(ValueError, match="缺少必需参数"):
        await view_image("view_image", {})


@pytest.mark.asyncio
@patch("mcp_imgutils.analysis.viewer.is_url")
@patch("mcp_imgutils.analysis.viewer.validate_image_path")
@patch("os.path.getsize")
async def test_view_image_too_large(mock_getsize, mock_validate, mock_is_url):
    """测试图片文件过大"""
    # 模拟不是URL，是本地文件
    mock_is_url.return_value = False
    # 模拟文件大小超过限制
    mock_getsize.return_value = 10 * 1024 * 1024  # 10MB
    # 模拟验证成功
    mock_validate.return_value = None

    result = await view_image(
        "view_image",
        {
            "image_path": "/path/to/large_image.jpg",
            "max_file_size": 5 * 1024 * 1024,  # 5MB
        },
    )

    # 验证结果是错误消息
    assert len(result) == 1
    assert result[0].type == "text"
    assert "图片文件太大" in result[0].text


@pytest.mark.asyncio
@patch("mcp_imgutils.analysis.viewer.is_url")
@patch("mcp_imgutils.analysis.viewer.validate_image_path")
@patch("mcp_imgutils.analysis.viewer.read_and_encode_image")
@patch("os.path.getsize")
async def test_view_image_processing_error(
    mock_getsize, mock_read_encode, mock_validate, mock_is_url
):
    """测试图片处理错误"""
    # 模拟不是URL，是本地文件
    mock_is_url.return_value = False
    # 模拟文件大小和处理错误
    mock_getsize.return_value = 1024  # 1KB
    mock_read_encode.side_effect = Exception("处理错误")
    # 模拟验证成功
    mock_validate.return_value = None

    result = await view_image("view_image", {"image_path": "/path/to/image.jpg"})

    # 验证结果是错误消息
    assert len(result) == 1
    assert result[0].type == "text"
    assert "处理图片时出错" in result[0].text
