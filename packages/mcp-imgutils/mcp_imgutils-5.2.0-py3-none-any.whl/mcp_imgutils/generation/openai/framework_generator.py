"""
OpenAI DALL-E 框架生成器

基于新框架的 OpenAI DALL-E 生成器实现，包装现有的 OpenAI 功能。
"""

from typing import Any

from ..base import GenerationResult, GeneratorConfig, ImageGenerator
from .config import DEFAULT_MODEL, PRESET_SIZES, OpenAIImageModel
from .generator import generate_image_openai as legacy_generate_image_openai


class OpenAIFrameworkConfig(GeneratorConfig):
    """OpenAI框架配置"""

    def get_config_prefix(self) -> str:
        """获取OpenAI配置前缀"""
        return "openai"

    def __post_init__(self):
        """初始化后处理"""
        super().__post_init__()

        # 设置OpenAI特定的默认值
        if not self.base_url:
            self.base_url = "https://api.openai.com/v1"

        # 从统一配置管理器获取OpenAI特定配置
        from ...common.config import get_config_manager
        config_manager = get_config_manager()

        # 获取图片保存目录
        self.image_save_dir = config_manager.get("openai.image_save_dir") or config_manager.get("image_save_dir")

    def get_required_keys(self) -> list[str]:
        """获取OpenAI必需的配置键"""
        return ["openai.api_key"]


class OpenAIFrameworkGenerator(ImageGenerator):
    """OpenAI DALL-E框架生成器"""
    
    def __init__(self, config: OpenAIFrameworkConfig):
        """初始化OpenAI生成器"""
        super().__init__(config)
        self.default_model = DEFAULT_MODEL
        self.preset_sizes = PRESET_SIZES

    async def generate_image(self, prompt: str, **kwargs) -> GenerationResult:
        """
        生成图像
        
        Args:
            prompt: 图像描述文本
            **kwargs: 其他参数
            
        Returns:
            GenerationResult: 生成结果
        """
        try:
            # 调用底层生成函数
            result = legacy_generate_image_openai(prompt=prompt, **kwargs)
            
            if result["success"]:
                return GenerationResult(
                    success=True,
                    images=result.get("images", []),
                    metadata={
                        "model": result.get("model"),
                        "prompt": result.get("prompt"),
                        "revised_prompt": result.get("revised_prompt"),
                        "created": result.get("created"),
                        "total_images": result.get("total_images", 0),
                    }
                )
            else:
                return GenerationResult(
                    success=False,
                    error=result.get("error", "未知错误"),
                    metadata={
                        "model": result.get("model"),
                        "prompt": result.get("prompt"),
                    }
                )
                
        except Exception as e:
            return GenerationResult(
                success=False,
                error=str(e),
                metadata={"prompt": prompt}
            )

    def get_supported_models(self) -> list[str]:
        """获取支持的模型列表"""
        return [model.value for model in OpenAIImageModel]

    def get_model_info(self, model: str) -> dict[str, Any]:
        """获取模型信息"""
        try:
            model_enum = OpenAIImageModel(model)
            from .config import MODEL_CONFIGS

            config = MODEL_CONFIGS[model_enum]
            
            return {
                "name": model,
                "supported_sizes": config.supported_sizes,
                "supports_quality": config.supports_quality,
                "supports_style": config.supports_style,
                "max_n": config.max_n,
                "price_per_image": config.price_per_image,
            }
        except ValueError:
            return {}

    def validate_parameters(self, **kwargs) -> dict[str, Any]:
        """验证参数"""
        from .config import OpenAIImageModel, validate_model_parameters
        
        model = kwargs.get("model", self.default_model.value)
        size = kwargs.get("size", "1024x1024")
        quality = kwargs.get("quality")
        style = kwargs.get("style")
        n = kwargs.get("n", 1)
        
        try:
            model_enum = OpenAIImageModel(model)
            return validate_model_parameters(
                model=model_enum,
                size=size,
                quality=quality,
                style=style,
                n=n
            )
        except Exception as e:
            raise ValueError(f"参数验证失败: {str(e)}")


def get_openai_tool_definition() -> dict:
    """
    获取 OpenAI DALL-E MCP 工具定义

    Returns:
        dict: MCP 工具定义
    """
    preset_sizes_desc = """
可用预设尺寸:

通用尺寸 (所有模型支持):
  • default: 1024x1024 - 默认尺寸，平衡质量和成本
  • square: 1024x1024 - 正方形，适合头像、图标

DALL-E 3 专用:
  • landscape: 1792x1024 - 横向长方形，适合宽屏内容
  • portrait: 1024x1792 - 纵向长方形，适合手机屏幕

DALL-E 2 专用 (向后兼容):
  • medium: 512x512 - 中等尺寸，经济选择
  • small: 256x256 - 小尺寸，最经济"""

    return {
        "name": "generate_image_openai",
        "description": f"""使用OpenAI DALL-E模型生成图片。图片将自动下载到本地目录，避免大文件传输问题。

⚠️ **配置要求**: 需要配置OPENAI_API_KEY环境变量。如未配置，工具会提供详细的设置指导。

✅ **语言支持**: OpenAI DALL-E模型支持中文和英文提示词，DALL-E 3会自动优化提示词以获得更好的结果。

📁 **本地保存**: 图片自动保存到本地目录（可通过OPENAI_IMAGE_SAVE_DIR环境变量自定义）。
   • Windows/macOS: ~/Pictures/OpenAI_Generated/
   • Linux: ~/Pictures/OpenAI_Generated/ 或 ~/OpenAI_Generated/

💡 **智能默认**: 默认使用1024x1024正方形，适合大多数用途。
   用户可以描述用途（如"桌面壁纸"、"Instagram帖子"），LLM会自动选择最佳预设。

💡 **自动化流程**: 生成完成后，工具会指导LLM自动调用view_image工具显示生成的图片，
   用户无需手动操作即可查看结果。

📝 **提示词保存**: 生成的图片会同时保存对应的提示词文本文件，便于管理和复用。

{preset_sizes_desc}

模型特性：
• DALL-E 3: 最新版本，更高质量，更好的提示词理解，支持高清模式和风格选择
• DALL-E 2: 经典版本，支持多张图片生成(1-10张)，成本更低

质量选项 (仅DALL-E 3):
• standard: 标准质量，更快更便宜
• hd: 高清质量，更慢更贵但质量更高

风格选项 (仅DALL-E 3):
• vivid: 生动风格，色彩鲜艳，对比强烈
• natural: 自然风格，更真实，色彩柔和

使用建议：
• 优先使用预设尺寸（preset_size参数）获得最佳效果
• DALL-E 3适合高质量单张图片，DALL-E 2适合批量生成
• 中文提示词效果良好，无需翻译为英文
• 使用临时路径参数(download_path)可灵活控制保存位置""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "图像描述文本。支持中文和英文，DALL-E 3 会自动优化提示词以获得更好的结果。"
                },
                "model": {
                    "type": "string",
                    "description": "DALL-E 模型选择。dall-e-3: 最新版本，更高质量；dall-e-2: 经典版本，支持多张生成",
                    "enum": ["dall-e-2", "dall-e-3"],
                    "default": "dall-e-3"
                },
                "preset_size": {
                    "type": "string",
                    "description": "预设尺寸（推荐使用，会覆盖size参数）。可选值: default, square, landscape, portrait, medium, small",
                    "enum": ["default", "square", "landscape", "portrait", "medium", "small"]
                },
                "size": {
                    "type": "string",
                    "description": "自定义图像尺寸（如果不使用preset_size）。DALL-E 2: 256x256, 512x512, 1024x1024；DALL-E 3: 1024x1024, 1792x1024, 1024x1792",
                    "default": "1024x1024"
                },
                "quality": {
                    "type": "string",
                    "description": "图像质量（仅DALL-E 3支持）。standard: 标准质量，更快更便宜；hd: 高清质量，更慢更贵但质量更高",
                    "enum": ["standard", "hd"],
                    "default": "standard"
                },
                "style": {
                    "type": "string",
                    "description": "图像风格（仅DALL-E 3支持）。vivid: 生动风格，色彩鲜艳对比强烈；natural: 自然风格，更真实色彩柔和",
                    "enum": ["vivid", "natural"],
                    "default": "vivid"
                },
                "n": {
                    "type": "integer",
                    "description": "生成图像数量。DALL-E 2支持1-10张，DALL-E 3固定为1张",
                    "minimum": 1,
                    "maximum": 10,
                    "default": 1
                },
                "download_path": {
                    "type": "string",
                    "description": "可选：临时指定图片下载保存目录。如果不指定，使用环境变量 OPENAI_IMAGE_SAVE_DIR 或系统默认目录"
                }
            },
            "required": ["prompt"]
        }
    }