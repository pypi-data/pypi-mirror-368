import os
import re
from enum import Enum
from urllib.parse import urlparse


class FluxModel(Enum):
    """FLUX 模型枚举"""
    FLUX_11_ULTRA = "flux-pro-1.1-ultra"
    FLUX_11 = "flux-pro-1.1"
    FLUX_1_PRO = "flux-pro"
    FLUX_1_DEV = "flux-dev"

class FluxTool(Enum):
    """FLUX 工具枚举"""
    FILL = "flux-pro-1.0-fill"
    CANNY = "flux-pro-1.0-canny"
    DEPTH = "flux-pro-1.0-depth"

class ModelConfig:
    """模型配置类"""
    def __init__(self, max_size: tuple[int, int], price: float):
        self.max_size = max_size
        self.price = price

# 模型配置 (基于 BFL 官方文档)
MODEL_CONFIGS: dict[FluxModel, ModelConfig] = {
    # flux-pro-1.1-ultra 使用 aspect_ratio 参数，不支持自定义 width/height
    FluxModel.FLUX_11_ULTRA: ModelConfig((2048, 2048), 0.06),  # 特殊处理
    # 其他模型都支持 256-1440 范围的 width/height
    FluxModel.FLUX_11: ModelConfig((1440, 1440), 0.04),
    FluxModel.FLUX_1_PRO: ModelConfig((1440, 1440), 0.05),
    FluxModel.FLUX_1_DEV: ModelConfig((1440, 1440), 0.025),
}

# API配置
API_BASE_URL = "https://api.bfl.ai/v1"
MAX_CONCURRENT_TASKS = 24
DEFAULT_TIMEOUT = 60  # 秒
DEFAULT_MODEL = FluxModel.FLUX_1_DEV
DEFAULT_SIZE = (1920, 1080)  # 默认图片尺寸 - Full HD 16:9，现代屏幕标准

# 预设尺寸 (所有尺寸都是32的倍数且在模型限制内: 256-1440)
PRESET_SIZES = {
    # 桌面壁纸 (调整到1440限制内)
    "desktop_fhd": (1440, 832, "桌面壁纸 Full HD (调整到模型限制内)"),
    "desktop_2k": (1440, 960, "桌面壁纸 2K"),
    "desktop_wide": (1280, 736, "桌面壁纸 宽屏 (接近1280x720)"),

    # 手机屏幕 (调整到1440限制内)
    "mobile_portrait": (832, 1440, "手机竖屏 (调整到模型限制内)"),
    "mobile_square": (1024, 1024, "手机正方形"),

    # 社交媒体
    "instagram_square": (1024, 1024, "Instagram 正方形"),
    "facebook_cover": (1184, 640, "Facebook 封面 (接近1200x630)"),
    "twitter_banner": (1024, 512, "Twitter 横幅"),

    # 电影/视频
    "cinema_wide": (1408, 576, "电影宽屏 21:9"),
    "video_hd": (1280, 736, "视频 HD 16:9"),

    # 艺术/打印
    "portrait_4_3": (1024, 768, "竖版 4:3"),
    "landscape_4_3": (1280, 960, "横版 4:3"),
    "square_large": (1408, 1408, "大正方形"),

    # 默认选项
    "default": (1920, 1080, "默认尺寸 - Full HD 16:9，现代屏幕标准")
}

# BFL 可信域名模式 (用于验证 polling_url)
# 使用正则表达式模式以支持动态的区域端点

BFL_DOMAIN_PATTERNS = [
    # 全局端点
    r"^api\.bfl\.ai$",
    # 区域端点 (支持多个区域编号)
    r"^api\.(eu|us)\.bfl\.ai$",
    r"^api\.(eu|us)\d+\.bfl\.ai$",  # 支持 eu1, eu2, eu3, eu4, us1, us2 等
    # 交付端点
    r"^delivery-(eu|us)\d+\.bfl\.ai$",
]

# 编译正则表达式以提高性能
COMPILED_BFL_PATTERNS = [re.compile(pattern) for pattern in BFL_DOMAIN_PATTERNS]

def get_image_save_directory(custom_path: str = None) -> str:
    """
    获取图片保存目录

    Args:
        custom_path: 可选的自定义路径，优先级最高

    Returns:
        str: 图片保存目录路径
    """
    # 1. 优先使用传入的自定义路径
    if custom_path:
        return os.path.expanduser(custom_path)

    # 2. 其次使用环境变量
    custom_dir = os.getenv("BFL_IMAGE_SAVE_DIR")
    if custom_dir:
        return os.path.expanduser(custom_dir)

    # 默认目录：用户图片目录
    home = os.path.expanduser("~")

    # 根据操作系统选择默认目录
    import platform
    system = platform.system().lower()

    if system == "windows":
        # Windows: ~/Pictures
        default_dir = os.path.join(home, "Pictures", "BFL_Generated")
    elif system == "darwin":
        # macOS: ~/Pictures
        default_dir = os.path.join(home, "Pictures", "BFL_Generated")
    else:
        # Linux: ~/Pictures 或 ~/
        pictures_dir = os.path.join(home, "Pictures")
        if os.path.exists(pictures_dir):
            default_dir = os.path.join(pictures_dir, "BFL_Generated")
        else:
            default_dir = os.path.join(home, "BFL_Generated")

    return default_dir


def generate_image_filename(prompt: str, model: str, size: tuple[int, int], url: str) -> str:
    """
    生成有意义的图片文件名

    Args:
        prompt: 图片提示词
        model: 使用的模型
        size: 图片尺寸 (width, height)
        url: BFL返回的图片URL

    Returns:
        str: 生成的文件名
    """
    import re
    from datetime import datetime

    # 从URL提取ID信息
    url_parts = url.split('/')
    result_id = ""
    for part in url_parts:
        if len(part) == 32 and all(c in '0123456789abcdef' for c in part):
            result_id = part[:8]  # 取前8位作为ID
            break

    # 清理提示词作为文件名的一部分
    clean_prompt = re.sub(r'[^\w\s-]', '', prompt)  # 移除特殊字符
    clean_prompt = re.sub(r'\s+', '_', clean_prompt)  # 空格替换为下划线
    clean_prompt = clean_prompt[:30]  # 限制长度

    # 生成时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 构建文件名: 时间戳_模型_尺寸_提示词_ID.jpg
    filename = f"{timestamp}_{model}_{size[0]}x{size[1]}_{clean_prompt}"
    if result_id:
        filename += f"_{result_id}"
    filename += ".jpg"

    return filename


def get_api_key(send_log=None) -> str:
    """
    从环境变量获取 API key

    Args:
        send_log: 可选的日志函数

    Returns:
        str: API key

    Raises:
        ValueError: 如果没有找到有效的 API key
    """
    api_key = os.getenv("BFL_API_KEY")

    if not api_key:
        error_msg = (
            "BFL API密钥未配置。请按以下步骤设置：\n\n"
            "1. 获取API密钥：访问 https://api.bfl.ai/ 注册并获取API密钥\n"
            "2. 配置方法：\n"
            "   • 在Claude Desktop配置中添加环境变量：\n"
            "     \"env\": { \"BFL_API_KEY\": \"your-api-key-here\" }\n"
            "   • 或设置系统环境变量：export BFL_API_KEY=your-api-key\n"
            "3. 重启Claude Desktop使配置生效\n\n"
            "详细配置说明请参考项目README文档。"
        )
        if send_log:
            send_log("error", "BFL_API_KEY环境变量未设置")
        raise ValueError(error_msg)

    if send_log:
        send_log("debug", "成功获取 API key")

    return api_key

def is_debug_mode() -> bool:
    """
    检查是否为调试模式

    Returns:
        bool: 如果 LOG_DEBUG 环境变量设置为 "true"/"1" 则返回 True，否则返回 False
    """
    debug = os.getenv("LOG_DEBUG", "false").lower()
    return debug in ("true", "1", "yes")

def validate_bfl_url(url: str) -> bool:
    """
    验证 URL 是否来自可信的 BFL 域名

    Args:
        url: 要验证的 URL

    Returns:
        bool: 如果 URL 来自可信域名则返回 True，否则返回 False
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False

        # 使用正则表达式模式验证域名
        return any(pattern.match(hostname) for pattern in COMPILED_BFL_PATTERNS)
    except (ValueError, AttributeError):
        return False

def adjust_size_to_multiple_of_32(width: int, height: int) -> tuple[int, int]:
    """
    调整尺寸到最接近的32的倍数

    Args:
        width: 原始宽度
        height: 原始高度

    Returns:
        Tuple[int, int]: 调整后的 (宽度, 高度)
    """
    adjusted_width = round(width / 32) * 32
    adjusted_height = round(height / 32) * 32

    # 确保最小尺寸为32
    adjusted_width = max(32, adjusted_width)
    adjusted_height = max(32, adjusted_height)

    return adjusted_width, adjusted_height

def validate_and_adjust_size(width: int, height: int, model: 'FluxModel') -> tuple[int, int, str]:
    """
    验证并调整尺寸以符合模型要求

    Args:
        width: 原始宽度
        height: 原始高度
        model: FLUX 模型

    Returns:
        Tuple[int, int, str]: (调整后宽度, 调整后高度, 调整说明)
    """
    original_size = (width, height)

    # 1. 调整到32的倍数
    adj_width, adj_height = adjust_size_to_multiple_of_32(width, height)

    # 2. 检查模型限制
    model_config = MODEL_CONFIGS[model]
    max_width, max_height = model_config.max_size

    adjustment_notes = []

    if adj_width != width or adj_height != height:
        adjustment_notes.append(f"调整到32的倍数: {original_size} → {(adj_width, adj_height)}")

    if adj_width > max_width or adj_height > max_height:
        # 按比例缩放到限制内
        scale = min(max_width / adj_width, max_height / adj_height)
        adj_width = int(adj_width * scale)
        adj_height = int(adj_height * scale)

        # 再次调整到32的倍数
        adj_width, adj_height = adjust_size_to_multiple_of_32(adj_width, adj_height)

        adjustment_notes.append(f"缩放到模型限制内: 最大{max_width}x{max_height}")

    adjustment_msg = "; ".join(adjustment_notes) if adjustment_notes else "无需调整"

    return adj_width, adj_height, adjustment_msg

def get_preset_size(preset_name: str) -> tuple[int, int]:
    """
    获取预设尺寸

    Args:
        preset_name: 预设名称

    Returns:
        Tuple[int, int]: (宽度, 高度)

    Raises:
        ValueError: 如果预设名称不存在
    """
    if preset_name not in PRESET_SIZES:
        available = ", ".join(PRESET_SIZES.keys())
        raise ValueError(f"未知的预设尺寸: {preset_name}。可用预设: {available}")

    width, height, _ = PRESET_SIZES[preset_name]
    return width, height

def get_preset_sizes_description() -> str:
    """
    获取所有预设尺寸的描述文本

    Returns:
        str: 格式化的预设尺寸描述
    """
    descriptions = []
    for name, (width, height, desc) in PRESET_SIZES.items():
        descriptions.append(f"  • {name}: {width}x{height} - {desc}")

    return "可用预设尺寸:\n" + "\n".join(descriptions)

def size_to_aspect_ratio(width: int, height: int) -> str:
    """
    将尺寸转换为宽高比字符串 (用于 flux-pro-1.1-ultra)

    Args:
        width: 宽度
        height: 高度

    Returns:
        str: 宽高比字符串，如 "16:9"
    """
    from math import gcd

    # 计算最大公约数来简化比例
    common_divisor = gcd(width, height)
    ratio_w = width // common_divisor
    ratio_h = height // common_divisor

    return f"{ratio_w}:{ratio_h}"

def is_ultra_model(model: 'FluxModel') -> bool:
    """
    检查是否为 ultra 模型 (使用 aspect_ratio 而不是 width/height)

    Args:
        model: FLUX 模型

    Returns:
        bool: 如果是 ultra 模型返回 True
    """
    return model == FluxModel.FLUX_11_ULTRA
