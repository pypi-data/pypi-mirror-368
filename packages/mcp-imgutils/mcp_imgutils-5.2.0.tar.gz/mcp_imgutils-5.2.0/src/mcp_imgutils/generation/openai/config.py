import os
import platform
from enum import Enum


class OpenAIImageModel(Enum):
    """OpenAI 图像生成模型枚举"""
    DALLE_3 = "dall-e-3"
    DALLE_2 = "dall-e-2"
    # GPT_IMAGE_1 = "gpt-image-1"  # TODO: 待调研官方文档后添加


class ModelConfig:
    """模型配置类"""
    def __init__(self, supported_sizes: list[str], supports_quality: bool, supports_style: bool, max_n: int, price_per_image: float):
        self.supported_sizes = supported_sizes
        self.supports_quality = supports_quality
        self.supports_style = supports_style
        self.max_n = max_n
        self.price_per_image = price_per_image


# 模型配置 (基于 OpenAI 官方文档)
MODEL_CONFIGS: dict[OpenAIImageModel, ModelConfig] = {
    OpenAIImageModel.DALLE_2: ModelConfig(
        supported_sizes=["256x256", "512x512", "1024x1024"],
        supports_quality=False,
        supports_style=False,
        max_n=10,
        price_per_image=0.02  # $0.016-$0.02
    ),
    OpenAIImageModel.DALLE_3: ModelConfig(
        supported_sizes=["1024x1024", "1792x1024", "1024x1792"],
        supports_quality=True,
        supports_style=True,
        max_n=1,  # 固定为 1
        price_per_image=0.04  # $0.04-$0.12
    ),
}

# API配置
API_BASE_URL = "https://api.openai.com/v1"
DEFAULT_TIMEOUT = 60  # 秒
DEFAULT_MODEL = OpenAIImageModel.DALLE_3
DEFAULT_SIZE = "1024x1024"  # 平衡质量和成本# 默认参数
DEFAULT_QUALITY = "standard"  # "standard" | "hd" (仅 DALL-E 3)
DEFAULT_STYLE = "vivid"      # "vivid" | "natural" (仅 DALL-E 3)
DEFAULT_N = 1                # 生成图片数量
DEFAULT_RESPONSE_FORMAT = "url"  # "url" | "b64_json"

# 预设尺寸 (基于 OpenAI 支持的尺寸)
PRESET_SIZES = {
    # 通用尺寸 (所有模型支持)
    "square": ("1024x1024", "正方形 - 通用尺寸，平衡质量和成本"),
    
    # DALL-E 3 专用
    "landscape": ("1792x1024", "横向长方形 - 适合宽屏内容 (仅 DALL-E 3)"),
    "portrait": ("1024x1792", "纵向长方形 - 适合手机屏幕 (仅 DALL-E 3)"),
    
    # DALL-E 2 专用 (向后兼容)
    "medium": ("512x512", "中等尺寸 - 经济选择 (仅 DALL-E 2)"),
    "small": ("256x256", "小尺寸 - 最经济 (仅 DALL-E 2)"),
    
    # 默认选项
    "default": ("1024x1024", "默认尺寸 - 正方形，平衡质量和成本")
}

# OpenAI API Key 环境变量
OPENAI_API_KEY_ENV = "OPENAI_API_KEY"


def _is_safe_path(path: str) -> bool:
    """
    检查路径是否安全，防止路径遍历攻击
    
    Args:
        path: 要检查的路径
        
    Returns:
        bool: 如果路径安全返回 True，否则返回 False
    """
    # 检查是否包含空字节（可能的注入攻击）
    if '\x00' in path:
        return False
    
    # 检查原始路径是否包含路径遍历字符
    if '..' in path:
        return False
        
    # 规范化路径后再次检查
    normalized_path = os.path.normpath(path)
    
    # 检查规范化后是否包含路径遍历字符
    if '..' in normalized_path:
        return False
        
    # 不允许以 .. 开头的相对路径
    return not normalized_path.startswith('..')


def get_image_save_directory(custom_path: str = None) -> str:
    """
    获取图片保存目录

    Args:
        custom_path: 可选的自定义路径，优先级最高

    Returns:
        str: 图片保存目录路径
        
    Raises:
        ValueError: 如果自定义路径包含不安全的路径遍历字符
    """
    # 1. 优先使用传入的自定义路径
    if custom_path:
        # 安全检查：防止路径遍历攻击
        if _is_safe_path(custom_path):
            return os.path.expanduser(custom_path)
        else:
            raise ValueError(f"不安全的路径: {custom_path}。路径不能包含 '..' 或其他不安全字符")
    
    # 2. 使用环境变量 OPENAI_IMAGE_SAVE_DIR
    env_path = os.getenv("OPENAI_IMAGE_SAVE_DIR")
    if env_path:
        return os.path.expanduser(env_path)
    
    # 3. 使用通用环境变量 IMAGE_SAVE_DIR
    general_env_path = os.getenv("IMAGE_SAVE_DIR")
    if general_env_path:
        return os.path.expanduser(general_env_path)
    
    # 4. 使用系统默认目录
    home = os.path.expanduser("~")
    
    # 根据操作系统选择合适的默认目录
    system = platform.system().lower()
    
    if system == "darwin" or system == "windows":  # macOS
        default_dir = os.path.join(home, "Pictures", "OpenAI_Generated")
    else:  # Linux 和其他 Unix-like 系统
        # 优先使用 Pictures 目录，如果不存在则使用 home 目录
        pictures_dir = os.path.join(home, "Pictures")
        if os.path.exists(pictures_dir):
            default_dir = os.path.join(pictures_dir, "OpenAI_Generated")
        else:
            default_dir = os.path.join(home, "OpenAI_Generated")
    
    return default_dir


def validate_model_parameters(model: OpenAIImageModel, size: str, quality: str = None, style: str = None, n: int = 1) -> dict:
    """
    验证模型参数的有效性

    Args:
        model: OpenAI 模型
        size: 图片尺寸
        quality: 图片质量 (可选)
        style: 图片风格 (可选)
        n: 生成图片数量

    Returns:
        dict: 验证后的参数字典

    Raises:
        ValueError: 如果参数无效
    """
    config = MODEL_CONFIGS[model]
    validated_params = {"model": model.value, "size": size, "n": n}

    # 验证尺寸
    if size not in config.supported_sizes:
        raise ValueError(f"模型 {model.value} 不支持尺寸 {size}。支持的尺寸: {config.supported_sizes}")

    # 验证生成数量
    if n < 1 or n > config.max_n:
        raise ValueError(f"模型 {model.value} 支持的生成数量范围: 1-{config.max_n}，当前: {n}")

    # 验证质量参数 (仅 DALL-E 3 支持)
    if quality:
        if not config.supports_quality:
            raise ValueError(f"模型 {model.value} 不支持 quality 参数")
        if quality not in ["standard", "hd"]:
            raise ValueError(f"quality 参数必须是 'standard' 或 'hd'，当前: {quality}")
        validated_params["quality"] = quality

    # 验证风格参数 (仅 DALL-E 3 支持)
    if style:
        if not config.supports_style:
            raise ValueError(f"模型 {model.value} 不支持 style 参数")
        if style not in ["vivid", "natural"]:
            raise ValueError(f"style 参数必须是 'vivid' 或 'natural'，当前: {style}")
        validated_params["style"] = style

    return validated_params


def get_openai_api_key() -> str:
    """
    获取 OpenAI API Key
    
    Returns:
        str: API Key
        
    Raises:
        ValueError: 如果未找到 API Key
    """
    api_key = os.getenv(OPENAI_API_KEY_ENV)
    if not api_key:
        raise ValueError(f"未找到 OpenAI API Key。请设置环境变量 {OPENAI_API_KEY_ENV}")
    return api_key