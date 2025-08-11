"""
统一配置管理系统

提供配置文件、环境变量、默认值的统一管理和验证。
"""

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


logger = logging.getLogger(__name__)


@dataclass
class ConfigSource:
    """配置源信息"""
    source_type: str  # "file", "env", "default"
    source_path: str | None = None
    priority: int = 0  # 优先级，数字越大优先级越高


@dataclass
class ConfigValue:
    """配置值包装器"""
    value: Any
    source: ConfigSource
    is_sensitive: bool = False  # 是否为敏感信息（如API密钥）
    
    def __str__(self) -> str:
        if self.is_sensitive and self.value:
            # 敏感信息只显示前4位和后4位
            val_str = str(self.value)
            if len(val_str) > 8:
                return f"{val_str[:4]}...{val_str[-4:]}"
            else:
                return "***"
        return str(self.value)


class ConfigManager:
    """统一配置管理器"""
    
    def __init__(self, app_name: str = "mcp-imgutils"):
        """
        初始化配置管理器
        
        Args:
            app_name: 应用名称，用于确定配置文件路径
        """
        self.app_name = app_name
        self._config: dict[str, ConfigValue] = {}
        self._config_files: list[Path] = []
        self._env_prefix = app_name.upper().replace("-", "_")
        
        # 初始化日志
        self._setup_logging()
        
        # 加载配置
        self._load_default_config()
        self._discover_config_files()
        self._load_config_files()
        self._load_environment_variables()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            default: 默认值
            
        Returns:
            配置值
        """
        config_value = self._config.get(key)
        if config_value is not None:
            return config_value.value
        return default
    
    def get_config_value(self, key: str) -> ConfigValue | None:
        """
        获取配置值对象（包含来源信息）
        
        Args:
            key: 配置键
            
        Returns:
            ConfigValue对象或None
        """
        return self._config.get(key)
    
    def set(self, key: str, value: Any, source_type: str = "runtime", is_sensitive: bool = False) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
            source_type: 来源类型
            is_sensitive: 是否为敏感信息
        """
        source = ConfigSource(source_type=source_type, priority=100)
        self._config[key] = ConfigValue(value=value, source=source, is_sensitive=is_sensitive)
        logger.debug(f"Set config {key} from {source_type}")
    
    def has(self, key: str) -> bool:
        """检查配置键是否存在"""
        return key in self._config
    
    def get_all_keys(self) -> list[str]:
        """获取所有配置键"""
        return list(self._config.keys())
    
    def get_config_summary(self) -> dict[str, dict[str, Any]]:
        """
        获取配置摘要（用于调试）
        
        Returns:
            配置摘要字典
        """
        summary = {}
        for key, config_value in self._config.items():
            summary[key] = {
                "value": str(config_value),  # 使用__str__方法，自动处理敏感信息
                "source": config_value.source.source_type,
                "source_path": config_value.source.source_path,
                "is_sensitive": config_value.is_sensitive
            }
        return summary
    
    def validate_required_keys(self, required_keys: list[str]) -> list[str]:
        """
        验证必需的配置键
        
        Args:
            required_keys: 必需的配置键列表
            
        Returns:
            缺失的配置键列表
        """
        missing_keys = []
        for key in required_keys:
            if not self.has(key) or self.get(key) is None:
                missing_keys.append(key)
        return missing_keys
    
    def _setup_logging(self) -> None:
        """设置日志"""
        log_level = os.getenv(f"{self._env_prefix}_LOG_LEVEL", "INFO").upper()
        logging.basicConfig(
            level=getattr(logging, log_level, logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    def _load_default_config(self) -> None:
        """加载默认配置"""
        defaults = {
            "debug": False,
            "log_level": "INFO",
            "timeout": 60,
            "max_retries": 3,
            "image_save_dir": self._get_default_image_dir(),
        }
        
        for key, value in defaults.items():
            source = ConfigSource(source_type="default", priority=1)
            self._config[key] = ConfigValue(value=value, source=source)
        
        logger.debug("Loaded default configuration")
    
    def _discover_config_files(self) -> None:
        """发现配置文件"""
        possible_paths = [
            # 当前目录
            Path.cwd() / f"{self.app_name}.json",
            Path.cwd() / f"{self.app_name}.yaml",
            Path.cwd() / f"{self.app_name}.yml",
            
            # 用户配置目录
            Path.home() / f".{self.app_name}" / "config.json",
            Path.home() / f".{self.app_name}" / "config.yaml",
            Path.home() / f".{self.app_name}" / "config.yml",
            
            # 系统配置目录（Linux/macOS）
            Path("/etc") / self.app_name / "config.json",
            Path("/etc") / self.app_name / "config.yaml",
        ]
        
        for path in possible_paths:
            if path.exists() and path.is_file():
                self._config_files.append(path)
                logger.debug(f"Found config file: {path}")
    
    def _load_config_files(self) -> None:
        """加载配置文件"""
        for config_file in self._config_files:
            try:
                self._load_config_file(config_file)
            except Exception as e:
                logger.warning(f"Failed to load config file {config_file}: {e}")
    
    def _load_config_file(self, config_file: Path) -> None:
        """
        加载单个配置文件
        
        Args:
            config_file: 配置文件路径
        """
        with open(config_file, encoding='utf-8') as f:
            if config_file.suffix.lower() == '.json':
                data = json.load(f)
            elif config_file.suffix.lower() in ['.yaml', '.yml']:
                if not YAML_AVAILABLE:
                    logger.warning(f"YAML not available, skipping {config_file}")
                    return
                data = yaml.safe_load(f)
            else:
                logger.warning(f"Unsupported config file format: {config_file}")
                return
        
        # 扁平化嵌套配置
        flat_data = self._flatten_dict(data)
        
        source = ConfigSource(
            source_type="file",
            source_path=str(config_file),
            priority=50
        )
        
        for key, value in flat_data.items():
            # 检查是否为敏感信息
            is_sensitive = any(sensitive_key in key.lower() 
                             for sensitive_key in ['key', 'token', 'secret', 'password'])
            
            # 如果已存在且优先级更高，则跳过
            existing = self._config.get(key)
            if existing and existing.source.priority >= source.priority:
                continue
            
            self._config[key] = ConfigValue(
                value=value,
                source=source,
                is_sensitive=is_sensitive
            )
        
        logger.info(f"Loaded config from {config_file}")
    
    def _load_environment_variables(self) -> None:
        """加载环境变量"""
        source = ConfigSource(source_type="env", priority=75)
        
        for key, value in os.environ.items():
            if key.startswith(f"{self._env_prefix}_"):
                # 移除前缀并转换为小写
                config_key = key[len(f"{self._env_prefix}_"):].lower()
                
                # 检查是否为敏感信息
                is_sensitive = any(sensitive_key in config_key 
                                 for sensitive_key in ['key', 'token', 'secret', 'password'])
                
                self._config[config_key] = ConfigValue(
                    value=value,
                    source=source,
                    is_sensitive=is_sensitive
                )
                
                logger.debug(f"Loaded env var: {config_key}")
    
    def _flatten_dict(self, d: dict[str, Any], parent_key: str = '', sep: str = '.') -> dict[str, Any]:
        """
        扁平化嵌套字典
        
        Args:
            d: 要扁平化的字典
            parent_key: 父键
            sep: 分隔符
            
        Returns:
            扁平化后的字典
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _get_default_image_dir(self) -> str:
        """获取默认图片保存目录"""
        home = Path.home()
        
        if os.name == "nt":  # Windows
            pictures_dir = home / "Pictures"
        else:  # macOS/Linux
            pictures_dir = home / "Pictures"
            if not pictures_dir.exists():
                pictures_dir = home
        
        return str(pictures_dir / "AI_Generated")


# 全局配置管理器实例
_config_manager: ConfigManager | None = None


def get_config_manager() -> ConfigManager:
    """
    获取全局配置管理器实例
    
    Returns:
        ConfigManager实例
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config(key: str, default: Any = None) -> Any:
    """
    获取配置值的便捷函数
    
    Args:
        key: 配置键
        default: 默认值
        
    Returns:
        配置值
    """
    return get_config_manager().get(key, default)


def set_config(key: str, value: Any, is_sensitive: bool = False) -> None:
    """
    设置配置值的便捷函数
    
    Args:
        key: 配置键
        value: 配置值
        is_sensitive: 是否为敏感信息
    """
    get_config_manager().set(key, value, "runtime", is_sensitive)
