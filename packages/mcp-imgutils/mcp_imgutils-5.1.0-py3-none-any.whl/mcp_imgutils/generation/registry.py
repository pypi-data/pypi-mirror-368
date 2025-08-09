"""
生成器注册系统

管理所有图片生成器的注册、发现和调用。
"""

import logging

from mcp import types

from .base import GeneratorConfig, GeneratorError, ImageGenerator

logger = logging.getLogger(__name__)


class GeneratorRegistry:
    """生成器注册表"""
    
    def __init__(self):
        """初始化注册表"""
        self._generators: dict[str, ImageGenerator] = {}
        self._generator_classes: dict[str, type[ImageGenerator]] = {}
        self._enabled_generators: set[str] = set()
    
    def register_class(
        self, 
        name: str, 
        generator_class: type[ImageGenerator]
    ) -> None:
        """
        注册生成器类
        
        Args:
            name: 生成器名称
            generator_class: 生成器类
            
        Raises:
            ValueError: 名称已存在或类无效
        """
        if name in self._generator_classes:
            raise ValueError(f"Generator '{name}' is already registered")
        
        if not issubclass(generator_class, ImageGenerator):
            raise ValueError("Generator class must inherit from ImageGenerator")
        
        self._generator_classes[name] = generator_class
        logger.info(f"Registered generator class: {name}")
    
    def create_generator(
        self, 
        name: str, 
        config: GeneratorConfig
    ) -> ImageGenerator:
        """
        创建生成器实例
        
        Args:
            name: 生成器名称
            config: 生成器配置
            
        Returns:
            ImageGenerator: 生成器实例
            
        Raises:
            ValueError: 生成器不存在
            GeneratorError: 创建失败
        """
        if name not in self._generator_classes:
            raise ValueError(f"Generator '{name}' is not registered")
        
        try:
            generator_class = self._generator_classes[name]
            generator = generator_class(config)
            self._generators[name] = generator
            self._enabled_generators.add(name)
            logger.info(f"Created generator instance: {name}")
            return generator
        except Exception as e:
            raise GeneratorError(f"Failed to create generator '{name}': {str(e)}", name)
    
    def get_generator(self, name: str) -> ImageGenerator | None:
        """
        获取生成器实例
        
        Args:
            name: 生成器名称
            
        Returns:
            Optional[ImageGenerator]: 生成器实例，如果不存在则返回None
        """
        return self._generators.get(name)
    
    def list_registered_classes(self) -> list[str]:
        """
        列出所有已注册的生成器类
        
        Returns:
            List[str]: 生成器名称列表
        """
        return list(self._generator_classes.keys())
    
    def list_enabled_generators(self) -> list[str]:
        """
        列出所有已启用的生成器
        
        Returns:
            List[str]: 已启用的生成器名称列表
        """
        return list(self._enabled_generators)
    
    def enable_generator(self, name: str) -> None:
        """
        启用生成器
        
        Args:
            name: 生成器名称
            
        Raises:
            ValueError: 生成器不存在
        """
        if name not in self._generators:
            raise ValueError(f"Generator '{name}' is not created")
        
        self._enabled_generators.add(name)
        logger.info(f"Enabled generator: {name}")
    
    def disable_generator(self, name: str) -> None:
        """
        禁用生成器
        
        Args:
            name: 生成器名称
        """
        self._enabled_generators.discard(name)
        logger.info(f"Disabled generator: {name}")
    
    def is_enabled(self, name: str) -> bool:
        """
        检查生成器是否启用
        
        Args:
            name: 生成器名称
            
        Returns:
            bool: 是否启用
        """
        return name in self._enabled_generators
    
    def get_tools(self) -> list[types.Tool]:
        """
        获取所有已启用生成器的MCP工具定义
        
        Returns:
            List[types.Tool]: MCP工具定义列表
        """
        tools = []
        for name in self._enabled_generators:
            generator = self._generators.get(name)
            if generator:
                try:
                    tool = generator.get_tool_definition()
                    tools.append(tool)
                except Exception as e:
                    logger.error(f"Failed to get tool definition for {name}: {e}")
        
        return tools
    
    def get_generator_info(self, name: str) -> dict[str, str] | None:
        """
        获取生成器信息
        
        Args:
            name: 生成器名称
            
        Returns:
            Optional[Dict[str, str]]: 生成器信息，如果不存在则返回None
        """
        generator = self._generators.get(name)
        if not generator:
            return None
        
        return {
            "name": generator.name,
            "display_name": generator.display_name,
            "description": generator.description,
            "enabled": self.is_enabled(name),
            "parameters": str(generator.get_supported_parameters())
        }
    
    def clear(self) -> None:
        """清空注册表"""
        self._generators.clear()
        self._generator_classes.clear()
        self._enabled_generators.clear()
        logger.info("Cleared generator registry")


# 全局注册表实例
registry = GeneratorRegistry()


def register_generator(name: str, generator_class: type[ImageGenerator]) -> None:
    """
    注册生成器类的便捷函数
    
    Args:
        name: 生成器名称
        generator_class: 生成器类
    """
    registry.register_class(name, generator_class)


def get_registry() -> GeneratorRegistry:
    """
    获取全局注册表实例
    
    Returns:
        GeneratorRegistry: 注册表实例
    """
    return registry
