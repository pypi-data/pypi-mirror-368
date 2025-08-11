"""
图片处理工具模块

提供图片验证、读取、编码等功能
"""

import base64
import os
from pathlib import Path
from urllib.parse import urlparse

import httpx
from PIL import Image
from PIL.ExifTags import TAGS

# 常量定义
DEFAULT_MAX_FILE_SIZE = 5 * 1024 * 1024  # 默认最大文件大小：5MB

# 图片格式常量
WEBP_EXTENSION = ".webp"
ALLOWED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", WEBP_EXTENSION]


def is_url(path: str) -> bool:
    """
    检测路径是否为URL

    Args:
        path: 要检测的路径字符串

    Returns:
        如果是有效的HTTP/HTTPS URL返回True，否则返回False
    """
    if not path:
        return False

    try:
        parsed = urlparse(path)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except (ValueError, AttributeError):
        return False


def validate_image_path(image_path: str) -> None:
    """
    验证图片路径的有效性

    Args:
        image_path: 图片文件路径

    Raises:
        ValueError: 当路径无效时抛出
    """
    if not image_path:
        raise ValueError("图片路径不能为空")

    path = Path(image_path)

    if not path.exists():
        raise ValueError(f"图片文件不存在：{image_path}")

    if not path.is_file():
        raise ValueError(f"路径不是文件：{image_path}")

    # 检查文件扩展名
    if path.suffix.lower() not in ALLOWED_IMAGE_FORMATS:
        raise ValueError(
            f"不支持的图片格式：{path.suffix}。支持的格式：{', '.join(ALLOWED_IMAGE_FORMATS)}"
        )


def get_image_mimetype(image_path: str) -> str:
    """
    根据文件扩展名获取MIME类型

    Args:
        image_path: 图片文件路径

    Returns:
        MIME类型字符串
    """
    extension = Path(image_path).suffix.lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
        WEBP_EXTENSION: "image/webp",
    }
    return mime_types.get(extension, "application/octet-stream")


async def download_image_from_url(url: str) -> str:
    """
    从URL下载图片到临时文件

    Args:
        url: 图片URL

    Returns:
        临时文件路径

    Raises:
        ValueError: 当下载失败时抛出
    """
    try:
        # 验证URL格式
        if not is_url(url):
            raise ValueError(f"无效的URL格式: {url}")

        # 创建异步HTTP客户端
        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={"User-Agent": "mcp-imgutils/2.0.0"},
        ) as client:
            # 下载图片
            response = await client.get(url)
            response.raise_for_status()

            # 检查Content-Type
            content_type = response.headers.get("content-type", "").lower()
            if not content_type.startswith("image/"):
                raise ValueError(f"URL返回的不是图片内容: {content_type}")

            # 创建临时文件
            suffix = ".jpg"  # 默认后缀
            if "png" in content_type:
                suffix = ".png"
            elif "gif" in content_type:
                suffix = ".gif"
            elif "webp" in content_type:
                suffix = WEBP_EXTENSION

            # 使用异步文件操作
            import aiofiles.tempfile
            async with aiofiles.tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                await temp_file.write(response.content)
                temp_file_name = temp_file.name

            return temp_file_name

    except httpx.RequestError as e:
        raise ValueError(f"网络请求失败: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise ValueError(f"HTTP错误 {e.response.status_code}: {e.response.text}")
    except Exception as e:
        raise ValueError(f"下载图片失败: {str(e)}")


def process_exif_value(value) -> str:
    """
    处理EXIF值，转换为可读的字符串格式

    Args:
        value: EXIF原始值

    Returns:
        处理后的字符串值
    """
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8", errors="ignore").strip()
        except UnicodeDecodeError:
            return f"<binary data: {len(value)} bytes>"
    elif isinstance(value, tuple | list):
        # 处理分数值（如曝光时间）
        if len(value) == 2 and all(isinstance(x, int | float) for x in value) and abs(value[1]) > 1e-10:
            return f"{value[0]}/{value[1]}"
        return str(value)
    elif isinstance(value, float):
        # 保留合理的小数位数
        return f"{value:.3f}".rstrip("0").rstrip(".")
    else:
        return str(value)


def get_exif_data(image_path: str) -> dict:
    """
    提取图片的EXIF元数据，包括详细的拍摄参数

    Args:
        image_path: 图片文件路径

    Returns:
        包含EXIF数据的字典，键为英文标签名

    Raises:
        ValueError: 当读取EXIF数据失败时抛出
    """
    try:
        with Image.open(image_path) as img:
            # 获取基本EXIF数据
            exif_data = img.getexif()

            if not exif_data:
                return {}

            exif_dict = {}

            # 处理基本EXIF数据
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, f"Unknown_{tag_id}")
                processed_value = process_exif_value(value)
                exif_dict[tag_name] = processed_value

            # 尝试获取更详细的EXIF信息（包括拍摄参数）
            try:
                if hasattr(img, "_getexif") and img._getexif():
                    detailed_exif = img._getexif()
                    for tag_id, value in detailed_exif.items():
                        tag_name = TAGS.get(tag_id, f"Unknown_{tag_id}")
                        # 避免重复添加已有的键
                        if tag_name not in exif_dict:
                            processed_value = process_exif_value(value)
                            exif_dict[tag_name] = processed_value
            except (KeyError, ValueError, AttributeError):
                # 如果详细EXIF读取失败，继续使用基本数据
                pass

            return exif_dict

    except Exception as e:
        raise ValueError(f"读取EXIF数据失败：{str(e)}")


def read_and_encode_image(image_path: str, _max_quality: int = 85) -> tuple[str, str]:
    """
    读取图片并转换为base64编码

    Args:
        image_path: 图片文件路径
        _max_quality: JPEG压缩质量，范围1-100（当前未使用，保留以兼容现有代码）

    Returns:
        元组(base64编码的图片数据, mime_type)

    Raises:
        ValueError: 当图片处理出错时抛出
    """
    try:
        # 直接读取文件并转换为base64，类似Desktop Commander的方法
        with open(image_path, "rb") as f:
            image_data = f.read()

        # 获取MIME类型
        mime_type = get_image_mimetype(image_path)

        # 转换为base64
        encoded_image = base64.b64encode(image_data).decode("utf-8")

        return encoded_image, mime_type

    except Exception as e:
        raise ValueError(f"处理图片时出错：{str(e)}")


def get_image_details(image_path: str) -> dict:
    """
    获取图片的详细信息

    Args:
        image_path: 图片文件路径

    Returns:
        包含图片详细信息的字典

    Raises:
        ValueError: 当获取图片信息失败时抛出
    """
    try:
        with Image.open(image_path) as img:
            # 获取基本信息
            width, height = img.size
            mode = img.mode
            format_name = img.format

            # 获取文件大小
            file_size = os.path.getsize(image_path)

            # 计算像素数
            total_pixels = width * height

            # 获取EXIF数据
            exif_data = get_exif_data(image_path)

            result = {
                "文件路径": image_path,
                "文件大小": f"{file_size:,} 字节",
                "图片格式": format_name,
                "颜色模式": mode,
                "尺寸": f"{width} x {height}",
                "总像素数": f"{total_pixels:,}",
                "宽度": width,
                "高度": height,
            }

            # 如果有EXIF数据，添加到结果中
            if exif_data:
                result["EXIF数据"] = exif_data

            return result

    except Exception as e:
        raise ValueError(f"获取图片信息失败：{str(e)}")
