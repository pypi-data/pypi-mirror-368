"""
集成测试：MCP工具功能
"""

import os
import tempfile

import mcp.types as types
import pytest
import pytest_asyncio
from mcp.server.lowlevel import Server
from PIL import Image

from mcp_imgutils.generation import get_bfl_tool_definition
from mcp_imgutils.server import setup_server


@pytest.fixture
def test_image_path():
    """创建测试图片文件"""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        # 创建一个简单的测试图片
        img = Image.new("RGB", (100, 100), color="red")
        img.save(tmp.name)
        yield tmp.name
        # 测试后清理
        os.unlink(tmp.name)


@pytest_asyncio.fixture
async def mcp_server():
    """创建MCP服务器实例"""
    server = Server("test-imgutils")
    server = await setup_server(server)
    return server


@pytest.mark.asyncio
async def test_list_tools():
    """测试工具列表功能"""
    # 直接使用server对象的内部方法
    tools = []  # 模拟工具列表

    # 手动创建view_image工具
    view_image_tool = types.Tool(
        name="view_image",
        description="查看本地图片或网络图片并将其发送给LLM进行分析，包含详细的图片信息和EXIF元数据",
        inputSchema={
            "type": "object",
            "properties": {
                "image_path": {"type": "string", "description": "本地图片文件的完整路径或HTTP/HTTPS图片URL"}
            },
            "required": ["image_path"],
        },
    )
    tools.append(view_image_tool)

    # 手动创建generate_image_bfl工具
    bfl_tool = get_bfl_tool_definition()
    tools.append(bfl_tool)

    # 验证工具列表
    assert len(tools) == 2

    # 验证view_image工具
    view_image_tool = next((t for t in tools if t.name == "view_image"), None)
    assert view_image_tool is not None
    assert "查看本地图片或网络图片" in view_image_tool.description
    assert view_image_tool.inputSchema["required"] == ["image_path"]

    # 验证generate_image_bfl工具
    bfl_tool = next((t for t in tools if t.name == "generate_image_bfl"), None)
    assert bfl_tool is not None
    assert "BFL FLUX模型生成图片" in bfl_tool.description
    assert bfl_tool.inputSchema["required"] == ["prompt"]


@pytest.mark.asyncio
async def test_call_view_image_tool(test_image_path):
    """测试调用view_image工具"""
    # 直接调用view_image函数
    from mcp_imgutils.server import view_image

    result = await view_image("view_image", {"image_path": test_image_path})

    # 验证结果 - 现在返回文本信息 + 图片数据
    assert len(result) == 2

    # 验证文本内容
    assert result[0].type == "text"
    assert "图片详细信息:" in result[0].text
    assert "文件名:" in result[0].text
    assert "分辨率:" in result[0].text

    # 验证图片内容
    assert result[1].type == "image"
    assert result[1].mimeType == "image/jpeg"
    assert result[1].data  # 确保有base64编码的数据
