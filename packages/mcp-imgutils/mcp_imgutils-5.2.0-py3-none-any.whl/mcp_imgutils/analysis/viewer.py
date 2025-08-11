"""
图片查看器模块

提供图片查看和分析功能，支持本地文件和网络URL。
"""

import contextlib
import os
from typing import Any

import mcp.types as types

from .utils import (
    DEFAULT_MAX_FILE_SIZE,
    download_image_from_url,
    get_image_details,
    is_url,
    read_and_encode_image,
    validate_image_path,
)

# 常量定义
EXIF_DATA_KEY = "EXIF数据"


def _validate_arguments(name: str, arguments: dict[str, Any]) -> tuple[str, int]:
    """验证参数并返回image_path和max_file_size"""
    if name != "view_image":
        raise ValueError(f"未知工具：{name}")

    if "image_path" not in arguments:
        raise ValueError("缺少必需参数 'image_path'")

    image_path = arguments["image_path"]
    max_file_size = arguments.get("max_file_size", DEFAULT_MAX_FILE_SIZE)

    return image_path, max_file_size


async def _get_actual_path(image_path: str) -> tuple[str, str | None]:
    """获取实际文件路径，返回(actual_path, temp_file_path)"""
    temp_file_path = None

    if is_url(image_path):
        # 从URL下载图片
        temp_file_path = await download_image_from_url(image_path)
        actual_path = temp_file_path
    else:
        # 本地文件路径
        validate_image_path(image_path)
        actual_path = image_path

    return actual_path, temp_file_path


def _check_file_size(image_path: str, actual_path: str, max_file_size: int) -> list[types.TextContent] | None:
    """检查文件大小，返回错误响应或None"""
    # 检查文件大小（仅对本地文件，URL下载的图片信任MCP协议处理）
    if not is_url(image_path):
        file_size = os.path.getsize(actual_path)
        if file_size > max_file_size:
            return [
                types.TextContent(
                    type="text",
                    text=f"图片文件太大：{file_size} 字节。最大允许大小：{max_file_size} 字节",
                )
            ]
    return None


def _create_response(encoded_image: str, mime_type: str, details: dict) -> list[types.TextContent | types.ImageContent]:
    """创建响应内容"""
    # 获取文件名（从文件路径中提取）
    import os
    file_path = details.get('文件路径', '')
    file_name = os.path.basename(file_path) if file_path else '未知'

    # 构建详细信息文本
    info_text = (
        f"图片详细信息:\n"
        f"文件名: {file_name}\n"
        f"文件路径: {details['文件路径']}\n"
        f"文件大小: {details['文件大小']}\n"
        f"图片格式: {details['图片格式']}\n"
        f"分辨率: {details['尺寸']}\n"
        f"颜色模式: {details['颜色模式']}\n"
        f"总像素数: {details['总像素数']}\n"
    )

    # 添加EXIF数据（如果有）
    if EXIF_DATA_KEY in details and details[EXIF_DATA_KEY]:
        info_text += "\nEXIF Metadata:\n"
        for key, value in details[EXIF_DATA_KEY].items():
            info_text += f"{key}: {value}\n"

    # 返回混合内容：详细信息 + 图片数据
    return [
        types.TextContent(type="text", text=info_text),
        types.ImageContent(type="image", data=encoded_image, mimeType=mime_type),
    ]


async def view_image(
    name: str, arguments: dict[str, Any]
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    查看本地图片或网络图片并将其发送给LLM进行分析

    支持本地文件路径和HTTP/HTTPS图片URL。网络图片会自动下载到临时文件进行处理。

    Args:
        name: 工具名称
        arguments: 工具参数，包含image_path（本地路径或URL）和可选的max_file_size

    Returns:
        包含图片内容和详细信息的响应列表

    Raises:
        ValueError: 当参数无效或图片处理出错时抛出
    """
    # 验证参数
    image_path, max_file_size = _validate_arguments(name, arguments)

    temp_file_path = None
    try:
        # 获取实际文件路径
        actual_path, temp_file_path = await _get_actual_path(image_path)

        # 检查文件大小
        size_error = _check_file_size(image_path, actual_path, max_file_size)
        if size_error:
            return size_error

        try:
            # 读取并编码图片
            encoded_image, mime_type = read_and_encode_image(actual_path)

            # 获取图片详细信息
            details = get_image_details(actual_path)

            # 创建响应
            return _create_response(encoded_image, mime_type, details)

        except Exception as e:
            return [types.TextContent(type="text", text=f"处理图片时出错：{str(e)}")]

    finally:
        # 清理临时文件
        if temp_file_path and os.path.exists(temp_file_path):
            with contextlib.suppress(OSError):
                os.unlink(temp_file_path)
