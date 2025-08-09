"""
配置验证和诊断工具

提供配置验证、诊断和友好的错误提示。
"""

import logging

from .config import ConfigManager, get_config_manager

logger = logging.getLogger(__name__)


class ConfigValidator:
    """配置验证器"""
    
    def __init__(self, config_manager: ConfigManager | None = None):
        """
        初始化配置验证器
        
        Args:
            config_manager: 配置管理器实例，如果为None则使用全局实例
        """
        self.config_manager = config_manager or get_config_manager()
    
    def validate_generator_config(self, generator_name: str, required_keys: list[str]) -> tuple[bool, list[str]]:
        """
        验证生成器配置
        
        Args:
            generator_name: 生成器名称
            required_keys: 必需的配置键列表
            
        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息列表)
        """
        errors = []
        
        # 检查必需的配置键
        missing_keys = self.config_manager.validate_required_keys(required_keys)
        for key in missing_keys:
            errors.append(f"Missing required configuration for {generator_name}: {key}")
        
        # 检查API密钥格式（如果存在）
        api_key_pattern = f"{generator_name}.api_key"
        if api_key_pattern in required_keys:
            api_key = self.config_manager.get(api_key_pattern)
            if api_key is not None:  # 检查是否存在，包括空字符串
                validation_error = self._validate_api_key_format(generator_name, api_key)
                if validation_error:
                    errors.append(validation_error)
        
        return len(errors) == 0, errors
    
    def get_configuration_suggestions(self, generator_name: str) -> list[str]:
        """
        获取配置建议
        
        Args:
            generator_name: 生成器名称
            
        Returns:
            配置建议列表
        """
        suggestions = []
        
        # 检查API密钥配置
        api_key = self.config_manager.get(f"{generator_name}.api_key")
        if not api_key:
            suggestions.extend(self._get_api_key_suggestions(generator_name))
        
        # 检查配置文件
        if not self.config_manager._config_files:
            suggestions.append(
                "Consider creating a configuration file (e.g., mcp-imgutils.json) "
                "in your home directory or current working directory"
            )
        
        return suggestions
    
    def generate_config_report(self) -> str:
        """
        生成配置报告
        
        Returns:
            配置报告字符串
        """
        report_lines = []
        report_lines.append("=== MCP ImageUtils Configuration Report ===")
        report_lines.append("")
        
        # 配置文件信息
        config_files = self.config_manager._config_files
        if config_files:
            report_lines.append("Configuration Files:")
            for config_file in config_files:
                report_lines.append(f"  - {config_file}")
        else:
            report_lines.append("Configuration Files: None found")
        report_lines.append("")
        
        # 配置摘要
        summary = self.config_manager.get_config_summary()
        if summary:
            report_lines.append("Current Configuration:")
            for key, info in sorted(summary.items()):
                source_info = f"({info['source']}"
                if info['source_path']:
                    source_info += f": {info['source_path']}"
                source_info += ")"
                
                report_lines.append(f"  {key}: {info['value']} {source_info}")
        else:
            report_lines.append("Current Configuration: Empty")
        report_lines.append("")
        
        # 环境变量建议
        report_lines.append("Environment Variables:")
        report_lines.append("  You can set configuration using environment variables with prefix MCP_IMGUTILS_")
        report_lines.append("  Examples:")
        report_lines.append("    export MCP_IMGUTILS_BFL_API_KEY=your-bfl-api-key")
        report_lines.append("    export MCP_IMGUTILS_DEBUG=true")
        report_lines.append("    export MCP_IMGUTILS_LOG_LEVEL=DEBUG")
        
        return "\n".join(report_lines)
    
    def _validate_api_key_format(self, generator_name: str, api_key: str) -> str | None:
        """
        验证API密钥格式
        
        Args:
            generator_name: 生成器名称
            api_key: API密钥
            
        Returns:
            错误信息，如果验证通过则返回None
        """
        if not api_key or not isinstance(api_key, str):
            return f"Invalid API key format for {generator_name}: must be a non-empty string"
        
        # 生成器特定的验证
        if generator_name == "bfl":
            if not api_key.strip():
                return "BFL API key cannot be empty or whitespace only"
            if len(api_key.strip()) < 10:
                return "BFL API key seems too short (expected at least 10 characters)"
        
        return None
    
    def _get_api_key_suggestions(self, generator_name: str) -> list[str]:
        """
        获取API密钥配置建议
        
        Args:
            generator_name: 生成器名称
            
        Returns:
            建议列表
        """
        suggestions = []
        env_var = f"MCP_IMGUTILS_{generator_name.upper()}_API_KEY"
        
        suggestions.append(f"To configure {generator_name.upper()} API key, you can:")
        suggestions.append(f"  1. Set environment variable: export {env_var}=your-api-key")
        suggestions.append(f"  2. Add to config file: {{\"{generator_name}.api_key\": \"your-api-key\"}}")
        
        # 生成器特定的建议
        if generator_name == "bfl":
            suggestions.append("  3. Get your BFL API key from: https://api.bfl.ai/")
        elif generator_name == "openai":
            suggestions.append("  3. Get your OpenAI API key from: https://platform.openai.com/api-keys")
        
        return suggestions


def validate_all_generators() -> dict[str, tuple[bool, list[str]]]:
    """
    验证所有已注册生成器的配置
    
    Returns:
        Dict[str, Tuple[bool, List[str]]]: 生成器名称到验证结果的映射
    """
    from ..generation import get_registry
    
    validator = ConfigValidator()
    results = {}
    
    registry = get_registry()
    for generator_name in registry.list_registered_classes():
        generator = registry.get_generator(generator_name)
        if generator and hasattr(generator, 'config'):
            required_keys = []
            if hasattr(generator.config, 'get_required_keys'):
                required_keys = generator.config.get_required_keys()
            
            is_valid, errors = validator.validate_generator_config(generator_name, required_keys)
            results[generator_name] = (is_valid, errors)
    
    return results


def print_config_report() -> None:
    """打印配置报告"""
    validator = ConfigValidator()
    report = validator.generate_config_report()
    print(report)


def diagnose_configuration_issues() -> None:
    """诊断配置问题并提供建议"""
    validator = ConfigValidator()
    
    print("=== Configuration Diagnosis ===")
    print()
    
    # 验证所有生成器
    results = validate_all_generators()
    
    if not results:
        print("No generators found to validate.")
        return
    
    all_valid = True
    for generator_name, (is_valid, errors) in results.items():
        print(f"{generator_name.upper()} Generator:")
        if is_valid:
            print("  ✅ Configuration is valid")
        else:
            all_valid = False
            print("  ❌ Configuration issues found:")
            for error in errors:
                print(f"    - {error}")
            
            # 提供建议
            suggestions = validator.get_configuration_suggestions(generator_name)
            if suggestions:
                print("  💡 Suggestions:")
                for suggestion in suggestions:
                    print(f"    {suggestion}")
        print()
    
    if all_valid:
        print("🎉 All generator configurations are valid!")
    else:
        print("⚠️  Some generators have configuration issues. Please check the suggestions above.")
    
    print()
    print("For detailed configuration information, run:")
    print("  python -c \"from src.mcp_imgutils.common.config_validator import print_config_report; print_config_report()\"")


if __name__ == "__main__":
    diagnose_configuration_issues()
