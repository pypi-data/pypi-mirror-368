"""
OpenAI DALL-E 图像生成器

基于 OpenAI API 的图像生成功能，支持 DALL-E 2/3 模型。
"""

import os
from datetime import datetime

import mcp.types as types
import requests
from openai import OpenAI
from PIL import Image

from .config import (
    DEFAULT_MODEL,
    DEFAULT_N,
    DEFAULT_QUALITY,
    DEFAULT_RESPONSE_FORMAT,
    DEFAULT_SIZE,
    DEFAULT_STYLE,
    OpenAIImageModel,
    get_image_save_directory,
    get_openai_api_key,
    validate_model_parameters,
)


def _convert_png_to_jpeg(image_path: str, quality: int = 85, keep_original: bool = True) -> tuple[str, str]:
    """
    将 PNG 图片转换为 JPEG 格式以减小文件大小

    Args:
        image_path: PNG 图片路径
        quality: JPEG 质量 (1-100)
        keep_original: 是否保留原始 PNG 文件

    Returns:
        tuple[str, str]: (JPEG文件路径, mimeType)
    """
    try:
        # 检查是否是 PNG 文件
        if not image_path.lower().endswith('.png'):
            # 如果不是 PNG，返回原文件
            if image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
                return image_path, "image/jpeg"
            else:
                return image_path, "image/png"  # 默认假设是 PNG

        # 生成 JPEG 文件路径
        jpeg_path = image_path.rsplit('.', 1)[0] + '.jpg'

        # 打开 PNG 图片
        with Image.open(image_path) as img:
            # 如果图片有透明通道，转换为 RGB
            if img.mode in ('RGBA', 'LA', 'P'):
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # 保存为 JPEG
            img.save(jpeg_path, 'JPEG', quality=quality, optimize=True)

        # 根据 keep_original 参数决定是否删除原 PNG 文件
        if not keep_original:
            import contextlib
            with contextlib.suppress(Exception):
                os.remove(image_path)
            print(f"🔄 已转换 PNG -> JPEG: {os.path.basename(jpeg_path)} (质量: {quality})")
        else:
            print(f"🔄 已创建 JPEG 副本: {os.path.basename(jpeg_path)} (质量: {quality}，保留原 PNG)")

        return jpeg_path, "image/jpeg"

    except Exception as e:
        print(f"⚠️ PNG转JPEG失败，使用原文件: {str(e)}")
        return image_path, "image/png"


def _generate_image_openai_sync(
    prompt: str,
    download_path: str | None = None,
    model: str = DEFAULT_MODEL.value,
    size: str = DEFAULT_SIZE,
    quality: str | None = DEFAULT_QUALITY,
    style: str | None = DEFAULT_STYLE,
    n: int = DEFAULT_N,
    response_format: str = DEFAULT_RESPONSE_FORMAT,
) -> dict:
    """
    使用 OpenAI DALL-E 生成图像
    
    Args:
        prompt: 图像描述文本
        download_path: 可选的自定义下载路径
        model: 模型名称 ("dall-e-2" | "dall-e-3")
        size: 图像尺寸
        quality: 图像质量 ("standard" | "hd", 仅 DALL-E 3)
        style: 图像风格 ("vivid" | "natural", 仅 DALL-E 3)
        n: 生成图像数量 (DALL-E 2: 1-10, DALL-E 3: 1)
        response_format: 响应格式 ("url" | "b64_json")
        
    Returns:
        dict: 包含生成结果的字典
        
    Raises:
        ValueError: 参数验证失败
        Exception: API 调用失败
    """
    try:
        # 1. 参数验证
        model_enum = OpenAIImageModel(model)
        from .config import MODEL_CONFIGS
        model_config = MODEL_CONFIGS[model_enum]

        validated_params = validate_model_parameters(
            model=model_enum,
            size=size,
            quality=quality if model_config.supports_quality else None,
            style=style if model_config.supports_style else None,
            n=n
        )
        
        # 2. 获取 API Key 和初始化客户端
        api_key = get_openai_api_key()
        client = OpenAI(api_key=api_key)
        
        # 3. 构建 API 请求参数
        api_params = {
            "model": validated_params["model"],
            "prompt": prompt,
            "size": validated_params["size"],
            "n": validated_params["n"],
            "response_format": response_format,
        }
        
        # 添加可选参数
        if "quality" in validated_params:
            api_params["quality"] = validated_params["quality"]
        if "style" in validated_params:
            api_params["style"] = validated_params["style"]
        
        # 4. 调用 OpenAI API
        print(f"🎨 正在使用 {model} 生成图像...")
        print(f"📝 提示词: {prompt}")
        print(f"📐 尺寸: {size}")
        if "quality" in api_params:
            print(f"🎯 质量: {api_params['quality']}")
        if "style" in api_params:
            print(f"🎭 风格: {api_params['style']}")
        print(f"🔢 数量: {n}")
        
        response = client.images.generate(**api_params)
        
        # 5. 处理响应
        result = {
            "success": True,
            "model": model,
            "prompt": prompt,
            "revised_prompt": None,
            "images": [],
            "created": response.created,
            "total_images": len(response.data)
        }
        
        # 6. 获取保存目录
        save_dir = get_image_save_directory(download_path)
        os.makedirs(save_dir, exist_ok=True)
        
        # 7. 处理每张图片
        for i, image_data in enumerate(response.data):
            image_info = {
                "index": i,
                "url": image_data.url if response_format == "url" else None,
                "b64_json": image_data.b64_json if response_format == "b64_json" else None,
                "revised_prompt": image_data.revised_prompt,  # DALL-E 3 可能有修订的提示词
            }
            
            # 保存修订的提示词 (仅第一张图片，因为通常都相同)
            if i == 0 and image_data.revised_prompt:
                result["revised_prompt"] = image_data.revised_prompt
            
            # 8. 下载并保存图片
            if response_format == "url" and image_data.url:
                # 从 URL 下载图片
                image_filename = _download_image_from_url(
                    url=image_data.url,
                    save_dir=save_dir,
                    prompt=prompt,
                    index=i,
                    created=response.created
                )
                image_info["local_path"] = image_filename
                
            elif response_format == "b64_json" and image_data.b64_json:
                # 保存 base64 图片
                image_filename = _save_base64_image(
                    b64_data=image_data.b64_json,
                    save_dir=save_dir,
                    prompt=prompt,
                    index=i,
                    created=response.created
                )
                image_info["local_path"] = image_filename
            
            result["images"].append(image_info)
        
        # 9. 保存提示词文件 (如果有修订的提示词)
        if result["revised_prompt"]:
            _save_prompt_file(
                original_prompt=prompt,
                revised_prompt=result["revised_prompt"],
                save_dir=save_dir,
                created=response.created
            )
        
        print(f"✅ 成功生成 {len(result['images'])} 张图片")
        print(f"📁 保存位置: {save_dir}")
        
        return result
        
    except Exception as e:
        print(f"❌ 图像生成失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "model": model,
            "prompt": prompt,
        }

def _download_image_from_url(url: str, save_dir: str, prompt: str, index: int, created: int) -> str:
    """
    从 URL 下载图片并保存到本地
    
    Args:
        url: 图片 URL
        save_dir: 保存目录
        prompt: 原始提示词
        index: 图片索引
        created: 创建时间戳
        
    Returns:
        str: 保存的文件路径
    """
    try:
        # 生成文件名
        timestamp = datetime.fromtimestamp(created).strftime("%Y%m%d_%H%M%S")
        safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_prompt = safe_prompt.replace(' ', '_')
        
        if len(safe_prompt) == 0:
            safe_prompt = "openai_image"
        
        filename = f"openai_{timestamp}_{safe_prompt}_{index}.png"
        filepath = os.path.join(save_dir, filename)
        
        # 下载图片
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # 保存图片
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"📥 已下载: {filename}")
        return filepath
        
    except Exception as e:
        print(f"❌ 下载图片失败: {str(e)}")
        raise


def _save_base64_image(b64_data: str, save_dir: str, prompt: str, index: int, created: int) -> str:
    """
    保存 base64 编码的图片
    
    Args:
        b64_data: base64 编码的图片数据
        save_dir: 保存目录
        prompt: 原始提示词
        index: 图片索引
        created: 创建时间戳
        
    Returns:
        str: 保存的文件路径
    """
    try:
        import base64
        
        # 生成文件名
        timestamp = datetime.fromtimestamp(created).strftime("%Y%m%d_%H%M%S")
        safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_prompt = safe_prompt.replace(' ', '_')
        
        if len(safe_prompt) == 0:
            safe_prompt = "openai_image"
        
        filename = f"openai_{timestamp}_{safe_prompt}_{index}.png"
        filepath = os.path.join(save_dir, filename)
        
        # 解码并保存图片
        image_data = base64.b64decode(b64_data)
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        print(f"💾 已保存: {filename}")
        return filepath
        
    except Exception as e:
        print(f"❌ 保存图片失败: {str(e)}")
        raise


def _save_prompt_file(original_prompt: str, revised_prompt: str, save_dir: str, created: int) -> str:
    """
    保存提示词文件 (原始和修订版本)
    
    Args:
        original_prompt: 原始提示词
        revised_prompt: 修订后的提示词
        save_dir: 保存目录
        created: 创建时间戳
        
    Returns:
        str: 保存的文件路径
    """
    try:
        # 生成文件名
        timestamp = datetime.fromtimestamp(created).strftime("%Y%m%d_%H%M%S")
        filename = f"openai_{timestamp}_prompts.txt"
        filepath = os.path.join(save_dir, filename)
        
        # 保存提示词
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("OpenAI DALL-E 图像生成提示词\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"生成时间: {datetime.fromtimestamp(created).strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("原始提示词:\n")
            f.write("-" * 20 + "\n")
            f.write(f"{original_prompt}\n\n")
            f.write("修订后提示词 (DALL-E 3 自动优化):\n")
            f.write("-" * 35 + "\n")
            f.write(f"{revised_prompt}\n")
        
        print(f"📝 已保存提示词: {filename}")
        return filepath
        
    except Exception as e:
        print(f"❌ 保存提示词失败: {str(e)}")
        # 不抛出异常，因为这不是关键功能
        return ""


# 预设尺寸的便捷函数
def generate_image_openai_preset(
    prompt: str,
    preset_size: str = "default",
    download_path: str | None = None,
    model: str = DEFAULT_MODEL.value,
    **kwargs
) -> dict:
    """
    使用预设尺寸生成图像的便捷函数
    
    Args:
        prompt: 图像描述文本
        preset_size: 预设尺寸名称 (default, square, landscape, portrait, medium, small)
        download_path: 可选的自定义下载路径
        model: 模型名称
        **kwargs: 其他参数
        
    Returns:
        dict: 生成结果
    """
    from .config import PRESET_SIZES
    
    if preset_size not in PRESET_SIZES:
        available_presets = list(PRESET_SIZES.keys())
        raise ValueError(f"未知的预设尺寸: {preset_size}。可用预设: {available_presets}")
    
    size, description = PRESET_SIZES[preset_size]
    print(f"📐 使用预设尺寸: {preset_size} ({description})")
    
    return _generate_image_openai_sync(
        prompt=prompt,
        download_path=download_path,
        model=model,
        size=size,
        **kwargs
    )

async def generate_image_openai(
    name: str, arguments: dict | None = None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    使用 OpenAI DALL-E 生成图片 (MCP 异步包装函数)
    
    Args:
        name: 工具名称
        arguments: 工具参数
        
    Returns:
        list: MCP 响应内容列表
    """
    if arguments is None:
        arguments = {}
    
    try:
        # 提取参数
        prompt = arguments.get("prompt")
        if not prompt:
            raise ValueError("缺少必需参数: prompt")
        
        download_path = arguments.get("download_path")
        model = arguments.get("model", DEFAULT_MODEL.value)
        size = arguments.get("size", DEFAULT_SIZE)
        quality = arguments.get("quality", DEFAULT_QUALITY)
        style = arguments.get("style", DEFAULT_STYLE)
        n = arguments.get("n", DEFAULT_N)
        preset_size = arguments.get("preset_size")
        
        # 如果指定了预设尺寸，使用预设尺寸函数
        if preset_size:
            result = generate_image_openai_preset(
                prompt=prompt,
                preset_size=preset_size,
                download_path=download_path,
                model=model,
                quality=quality,
                style=style,
                n=n
            )
        else:
            # 使用标准生成函数
            result = _generate_image_openai_sync(
                prompt=prompt,
                download_path=download_path,
                model=model,
                size=size,
                quality=quality,
                style=style,
                n=n
            )
        
        # 构建响应
        response_content = []
        
        if result["success"]:
            # 成功响应
            success_message = f"✅ 成功使用 {result['model']} 生成了 {result['total_images']} 张图片"
            
            # 添加修订提示词信息 (DALL-E 3)
            if result.get("revised_prompt"):
                success_message += f"\n\n📝 **原始提示词**: {result['prompt']}"
                success_message += f"\n🔄 **优化后提示词**: {result['revised_prompt']}"
            
            # 添加图片信息
            success_message += f"\n\n📁 **保存位置**: {os.path.dirname(result['images'][0]['local_path']) if result['images'] else '未知'}"
            
            for i, image_info in enumerate(result["images"]):
                success_message += f"\n🖼️ **图片 {i+1}**: {os.path.basename(image_info.get('local_path', '未知'))}"
            
            response_content.append(types.TextContent(type="text", text=success_message))
            
            # 添加生成的图片
            for image_info in result["images"]:
                if image_info.get("local_path") and os.path.exists(image_info["local_path"]):
                    try:
                        import base64

                        import aiofiles

                        # 转换 PNG 为 JPEG 以减小文件大小（保留原始 PNG 用于存储）
                        converted_path, mime_type = _convert_png_to_jpeg(image_info["local_path"], keep_original=True)

                        # 使用异步文件操作读取转换后的图片
                        async with aiofiles.open(converted_path, "rb") as f:
                            image_data = await f.read()

                        # 将图片数据编码为 base64 字符串
                        image_base64 = base64.b64encode(image_data).decode('utf-8')

                        response_content.append(
                            types.ImageContent(
                                type="image",
                                data=image_base64,
                                mimeType=mime_type
                            )
                        )

                        # 更新 image_info 中的路径
                        image_info["local_path"] = converted_path

                    except Exception as e:
                        print(f"⚠️ 无法读取图片文件 {image_info['local_path']}: {str(e)}")
        else:
            # 错误响应
            error_message = f"❌ OpenAI DALL-E 图片生成失败: {result.get('error', '未知错误')}"
            response_content.append(types.TextContent(type="text", text=error_message))
        
        return response_content
        
    except Exception as e:
        error_message = f"❌ OpenAI DALL-E 图片生成异常: {str(e)}"
        return [types.TextContent(type="text", text=error_message)]