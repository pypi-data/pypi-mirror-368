"""
BFL图片生成器

基于Black Forest Labs API的图片生成功能。
"""

import asyncio
import sys
import uuid
from datetime import datetime, timedelta

import aiofiles
import mcp.types as types

from ...common.errors import BFLError
from .client import FluxClient
from .config import (
    DEFAULT_MODEL,
    DEFAULT_SIZE,
    PRESET_SIZES,
    FluxModel,
    generate_image_filename,
    get_api_key,
    get_image_save_directory,
    get_preset_size,
    get_preset_sizes_description,
    is_debug_mode,
    is_ultra_model,
    validate_and_adjust_size,
)


def send_log(level: str, message: str):
    """发送日志，通过 stderr 输出，包含时间戳

    只有在以下情况下输出日志：
    - debug 级别日志仅在调试模式下输出
    - info 及以上级别的日志始终输出

    Args:
        level: 日志级别 (debug/info/warning/error)
        message: 日志消息
    """
    # 如果是 debug 级别的日志，且不是调试模式，则不输出
    if level == "debug" and not is_debug_mode():
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [{level}] {message}", file=sys.stderr, flush=True)


class ImageResource:
    """临时图片资源"""

    def __init__(self, image_data: bytes, url: str):
        self.data = image_data
        self.url = url
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.ttl = timedelta(minutes=10)  # 与 BFL API 图片 URL 有效期一致

    @property
    def is_expired(self) -> bool:
        """检查资源是否过期"""
        return datetime.now() - self.created_at > self.ttl


# 存储临时图片资源
# key: resource_id, value: ImageResource
resources: dict[str, ImageResource] = {}


def cleanup_expired_resources():
    """清理过期的资源"""
    expired = [rid for rid, r in resources.items() if r.is_expired]
    for rid in expired:
        del resources[rid]
    if expired:
        send_log("debug", f"已清理 {len(expired)} 个过期资源")


async def save_prompt_to_txt(image_path: str, prompt: str, model: str, size: tuple[int, int], image_url: str) -> str:
    """
    保存提示词和生成信息到txt文件

    Args:
        image_path: 图片文件路径
        prompt: 图片提示词
        model: 使用的模型
        size: 图片尺寸
        image_url: BFL返回的图片URL

    Returns:
        str: txt文件路径
    """
    from datetime import datetime

    # 生成txt文件路径（与图片同名，扩展名为.txt）
    txt_path = image_path.rsplit('.', 1)[0] + '.txt'

    # 从URL提取ID
    url_parts = image_url.split('/')
    bfl_id = ""
    for part in url_parts:
        if len(part) == 32 and all(c in '0123456789abcdef' for c in part):
            bfl_id = part[:8]
            break

    # 生成txt内容
    content = f"""Prompt: {prompt}
Model: {model}
Size: {size[0]}x{size[1]}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
BFL_ID: {bfl_id}
Download_URL: {image_url}
"""

    # 保存txt文件
    async with aiofiles.open(txt_path, 'w', encoding='utf-8') as f:
        await f.write(content)

    send_log("info", f"提示词信息已保存到: {txt_path}")
    return txt_path


async def download_image_to_local(
    image_url: str,
    prompt: str,
    model: str,
    size: tuple[int, int],
    custom_download_path: str = None
) -> tuple[str, str]:
    """
    下载图片到本地目录并保存提示词信息

    Args:
        image_url: BFL返回的图片URL
        prompt: 图片提示词
        model: 使用的模型
        size: 图片尺寸
        custom_download_path: 可选的自定义下载路径

    Returns:
        tuple[str, str]: (图片文件路径, txt文件路径)

    Raises:
        Exception: 下载失败时抛出异常
    """
    import os

    import httpx

    # 获取保存目录（支持自定义路径）
    save_dir = get_image_save_directory(custom_download_path)

    # 确保目录存在
    os.makedirs(save_dir, exist_ok=True)

    # 生成文件名
    filename = generate_image_filename(prompt, model, size, image_url)
    local_path = os.path.join(save_dir, filename)

    # 下载图片
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(image_url)
        response.raise_for_status()

        # 保存到本地
        async with aiofiles.open(local_path, 'wb') as f:
            await f.write(response.content)

    send_log("info", f"图片已保存到: {local_path}")

    # 保存提示词信息到txt文件
    txt_path = await save_prompt_to_txt(local_path, prompt, model, size, image_url)

    return local_path, txt_path


def _validate_tool_call(name: str, arguments: dict | None) -> str:
    """验证工具调用参数"""
    if name != "generate_image_bfl":
        raise ValueError(f"未知工具：{name}")

    if not arguments:
        send_log("error", "缺少参数")
        raise ValueError("Missing arguments")

    prompt = arguments.get("prompt")
    if not prompt:
        send_log("error", "缺少图片描述")
        raise ValueError("Missing prompt")

    return prompt


def _parse_model_parameter(arguments: dict) -> FluxModel:
    """解析模型参数"""
    model_name = arguments.get("model", DEFAULT_MODEL.value)
    try:
        model = FluxModel(model_name)
        send_log("info", f"使用模型: {model.value}")
        return model
    except ValueError:
        send_log("error", f"无效的模型: {model_name}")
        raise ValueError(f"Invalid model: {model_name}")


def _parse_size_parameters(arguments: dict) -> tuple[int, int]:
    """解析尺寸参数"""
    preset_size = arguments.get("preset_size")

    if preset_size:
        # 使用预设尺寸
        try:
            width, height = get_preset_size(preset_size)
            send_log("info", f"使用预设尺寸 {preset_size}: {width}x{height}")
            return width, height
        except ValueError as e:
            send_log("error", f"无效的预设尺寸: {str(e)}")
            raise
    else:
        # 使用自定义尺寸
        width = int(arguments.get("width", DEFAULT_SIZE[0]))
        height = int(arguments.get("height", DEFAULT_SIZE[1]))
        send_log("info", f"使用自定义尺寸: {width}x{height}")
        return width, height


def _validate_and_adjust_size(width: int, height: int, model: FluxModel) -> tuple[int, int]:
    """验证并调整尺寸"""
    original_width, original_height = width, height

    if not is_ultra_model(model):
        width, height, adjustment_msg = validate_and_adjust_size(width, height, model)

        if width != original_width or height != original_height:
            send_log(
                "info",
                f"尺寸调整: {original_width}x{original_height} → {width}x{height} ({adjustment_msg})",
            )
    else:
        send_log("info", f"Ultra模型将使用宽高比参数，原始尺寸: {width}x{height}")

    return width, height


async def _generate_and_download_image(
    prompt: str,
    model: FluxModel,
    width: int,
    height: int,
    download_path: str = None
) -> tuple[str, str]:
    """生成并下载图片"""
    # 从环境变量获取 API key
    try:
        api_key = get_api_key(send_log)
    except ValueError as e:
        send_log("error", "BFL API密钥未配置")
        raise ValueError(str(e))
    except Exception as e:
        error_msg = f"API密钥获取失败: {str(e)}"
        send_log("error", error_msg)
        raise ValueError(error_msg)

    # 使用上下文管理器确保资源正确释放
    async with FluxClient(api_key, send_log) as client:
        # 生成图片，获取图片URL（不下载图片数据以节省带宽）
        _, image_url = await client.generate_image(
            prompt=prompt, model=model, size=(width, height)
        )

        send_log("info", "图片生成成功，开始下载到本地")

        # 下载图片到本地并保存提示词信息
        return await download_image_to_local(image_url, prompt, model.value, (width, height), download_path)


async def generate_image_bfl(
    name: str, arguments: dict | None = None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    使用BFL API生成图片

    Args:
        name: 工具名称
        arguments: 工具参数

    Returns:
        执行结果

    Raises:
        ValueError: 无效的工具名或参数
    """
    send_log("debug", f"BFL工具调用: {name}, 参数: {arguments}")

    try:
        # 验证工具调用
        prompt = _validate_tool_call(name, arguments)

        # 解析参数
        model = _parse_model_parameter(arguments)
        width, height = _parse_size_parameters(arguments)
        download_path = arguments.get("download_path") if arguments else None

        # 验证并调整尺寸
        width, height = _validate_and_adjust_size(width, height, model)

        send_log("info", f"开始生成图片: model={model.value}, size={width}x{height}, prompt={prompt}")
        if download_path:
            send_log("info", f"使用自定义下载路径: {download_path}")

        # 生成并下载图片
        local_path, txt_path = await _generate_and_download_image(prompt, model, width, height, download_path)

        # 构造返回内容
        return [
            types.TextContent(
                type="text",
                text=f"✅ 图片生成成功！\n\n"
                     f"🎨 使用模型: {model.value}\n"
                     f"📐 图片尺寸: {width}x{height}\n"
                     f"📝 提示词已保存到: {txt_path}\n\n"
                     f"LOCAL_PATH::本地路径::请使用 view_image 工具查看这张生成的图片::{local_path}"
            ),
        ]

    except ValueError as e:
        # 输入验证错误
        error_msg = f"参数验证失败: {str(e)}"
        send_log("error", error_msg)
        return [types.TextContent(type="text", text=error_msg)]
    except BFLError as e:
        # BFL API错误
        error_msg = f"图片生成失败: {str(e)}"
        send_log("error", error_msg)
        return [types.TextContent(type="text", text=error_msg)]
    except OSError as e:
        # 文件系统错误（磁盘空间、权限等）
        error_msg = f"文件操作失败: {str(e)}\n请检查磁盘空间和目录权限"
        send_log("error", error_msg)
        return [types.TextContent(type="text", text=error_msg)]
    except asyncio.CancelledError:
        # 任务被取消
        send_log("warning", "图片生成任务被取消")
        raise
    except Exception as e:
        # 其他未预期的错误
        error_msg = f"图片生成异常: {str(e)}"
        send_log("error", error_msg)
        import traceback
        send_log("debug", f"错误堆栈: {traceback.format_exc()}")
        return [types.TextContent(type="text", text=error_msg)]

    # 不需要finally块，因为我们使用了async with上下文管理器


def get_bfl_tool_definition() -> types.Tool:
    """获取BFL工具的MCP定义"""
    preset_sizes_desc = get_preset_sizes_description()

    return types.Tool(
        name="generate_image_bfl",
        description=f"""使用BFL FLUX模型生成图片。图片将自动下载到本地目录，避免大文件传输问题。

⚠️ **配置要求**: 需要配置BFL_API_KEY环境变量。如未配置，工具会提供详细的设置指导。

⚠️ **语言支持**: BFL FLUX模型主要支持英文提示词，中文提示词可能效果不佳。建议使用英文描述以获得最佳生成效果。

📁 **本地保存**: 图片自动保存到本地目录（可通过BFL_IMAGE_SAVE_DIR环境变量自定义）。
   • Windows/macOS: ~/Pictures/BFL_Generated/
   • Linux: ~/Pictures/BFL_Generated/ 或 ~/BFL_Generated/

💡 **智能默认**: 默认使用1920x1080 (Full HD 16:9)，适合现代屏幕。
   用户可以描述用途（如"桌面壁纸"、"Instagram帖子"），LLM会自动选择最佳预设。

💡 **自动化流程**: 生成完成后，工具会指导LLM自动调用view_image工具显示生成的图片，
   用户无需手动操作即可查看结果。

{preset_sizes_desc}

尺寸要求：
• 宽度和高度必须是32的倍数（系统会自动调整）
• 尺寸范围：256-1440像素（宽度和高度）
• 不同模型的特殊说明：
  - flux-pro-1.1-ultra: 使用宽高比参数，支持更大尺寸
  - flux-pro-1.1/flux-pro/flux-dev: 最大 1440x1440

使用建议：
• 优先使用预设尺寸（preset_size参数）获得最佳效果
• 自定义尺寸会自动调整到符合要求的最接近尺寸
• 建议根据用途选择合适的预设：桌面壁纸用desktop_*，手机用mobile_*，社交媒体用对应预设
• 使用英文提示词以获得最佳生成质量""",
        inputSchema={
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "图片描述"},
                "model": {
                    "type": "string",
                    "description": "FLUX 模型选择",
                    "enum": ["flux-pro-1.1", "flux-pro-1.1-ultra", "flux-pro", "flux-dev"],
                    "default": DEFAULT_MODEL.value,
                },
                "preset_size": {
                    "type": "string",
                    "description": f"预设尺寸（推荐使用）。可选值: {', '.join(PRESET_SIZES.keys())}",
                    "enum": list(PRESET_SIZES.keys()),
                },
                "width": {
                    "type": "integer",
                    "description": "自定义图片宽度（如果不使用preset_size）。会自动调整到32的倍数",
                    "minimum": 32,
                    "maximum": 2048,
                    "default": DEFAULT_SIZE[0],
                },
                "height": {
                    "type": "integer",
                    "description": "自定义图片高度（如果不使用preset_size）。会自动调整到32的倍数",
                    "minimum": 32,
                    "maximum": 2048,
                    "default": DEFAULT_SIZE[1],
                },
                "download_path": {
                    "type": "string",
                    "description": "可选：临时指定图片下载保存目录。如果不指定，使用环境变量 BFL_IMAGE_SAVE_DIR 或系统默认目录"
                },
            },
            "required": ["prompt"],
        },
    )
