# 开发者指南

## 🚀 快速开始

### 添加新的 AI 图片生成模型

Phase 2 框架让添加新模型变得非常简单。以下是完整的步骤：

## 📝 步骤 1: 创建生成器类

```python
# src/mcp_imgutils/generation/openai/generator.py
from typing import Any, Dict, Optional
from mcp import types

from ..base import ImageGenerator, GeneratorConfig, GenerationResult
from ...common.errors import APIError, ValidationError
from ...common.retry import RetryConfig
from ...common.rate_limiter import RateLimit

class OpenAIConfig(GeneratorConfig):
    """OpenAI 配置"""
    
    def get_config_prefix(self) -> str:
        return "openai"
    
    def get_required_keys(self) -> List[str]:
        return ["openai.api_key"]

class OpenAIGenerator(ImageGenerator):
    """OpenAI DALL-E 生成器"""
    
    @property
    def name(self) -> str:
        return "openai"
    
    @property
    def display_name(self) -> str:
        return "OpenAI DALL-E"
    
    @property
    def description(self) -> str:
        return "OpenAI DALL-E 3 高质量图片生成"
    
    def get_retry_config(self) -> RetryConfig:
        """OpenAI 特定的重试配置"""
        return RetryConfig(
            max_attempts=3,
            base_delay=2.0,
            max_delay=60.0
        )
    
    def get_rate_limit(self) -> RateLimit:
        """OpenAI 特定的速率限制"""
        return RateLimit(
            requests_per_second=0.5,  # OpenAI 限制较严格
            requests_per_minute=30.0,
            burst_size=2
        )
    
    async def generate(self, prompt: str, **kwargs) -> GenerationResult:
        """生成图片"""
        # 1. 检查缓存
        cached_path = await self._get_cached_image(prompt, kwargs)
        if cached_path:
            return self._create_success_result(local_path=cached_path)
        
        # 2. 使用错误处理包装器执行生成
        return await self._execute_with_error_handling(
            "generate",
            self._do_generate,
            prompt,
            **kwargs
        )
    
    async def _do_generate(self, prompt: str, **kwargs) -> GenerationResult:
        """实际的生成逻辑"""
        try:
            # 调用 OpenAI API
            response = await self._call_openai_api(prompt, **kwargs)
            
            # 下载图片
            image_data = await self._download_image(response['url'])
            
            # 存储到资源管理器
            local_path = await self._store_generated_image(
                image_data=image_data,
                prompt=prompt,
                model=kwargs.get('model', 'dall-e-3'),
                parameters=kwargs
            )
            
            return self._create_success_result(local_path=local_path)
            
        except Exception as e:
            # 框架会自动处理错误包装
            raise e
    
    def get_tool_definition(self) -> types.Tool:
        """MCP 工具定义"""
        return types.Tool(
            name="generate_image_openai",
            description="使用 OpenAI DALL-E 生成图片",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "图片描述"
                    },
                    "model": {
                        "type": "string",
                        "enum": ["dall-e-2", "dall-e-3"],
                        "default": "dall-e-3"
                    },
                    "size": {
                        "type": "string",
                        "enum": ["256x256", "512x512", "1024x1024"],
                        "default": "1024x1024"
                    }
                },
                "required": ["prompt"]
            }
        )
```

## 📝 步骤 2: 注册生成器

```python
# src/mcp_imgutils/generation/__init__.py
from .openai.generator import OpenAIGenerator, OpenAIConfig

def initialize_generators():
    """初始化所有生成器"""
    registry = get_registry()
    
    # 注册现有的 BFL 生成器
    register_generator("bfl", BFLFrameworkGenerator)
    
    # 注册新的 OpenAI 生成器
    register_generator("openai", OpenAIGenerator)
    
    # 尝试创建实例
    try:
        openai_config = OpenAIConfig()
        if openai_config.is_valid():
            registry.create_generator("openai", openai_config)
    except Exception:
        pass  # 配置无效时静默失败
```

## 📝 步骤 3: 配置支持

```json
// mcp-imgutils.json
{
  "openai": {
    "api_key": "your-openai-api-key",
    "base_url": "https://api.openai.com/v1",
    "default_model": "dall-e-3",
    "timeout": 60
  }
}
```

## 📝 步骤 4: 测试

```python
# tests/test_openai_generator.py
import pytest
from src.mcp_imgutils.generation.openai.generator import OpenAIGenerator, OpenAIConfig

class TestOpenAIGenerator:
    def test_generator_properties(self):
        config = OpenAIConfig(api_key="test-key")
        generator = OpenAIGenerator(config)
        
        assert generator.name == "openai"
        assert generator.display_name == "OpenAI DALL-E"
    
    @pytest.mark.asyncio
    async def test_generate_with_mock(self):
        # 使用 mock 测试生成逻辑
        pass
```

## 🛠️ 框架提供的功能

### 1. 自动错误处理
```python
# 框架自动处理这些错误：
try:
    result = await generator.generate("test prompt")
except APIError as e:
    print(e.get_user_message("zh"))  # 中文错误消息
except RateLimitError as e:
    print(f"需要等待 {e.retry_after} 秒")
```

### 2. 自动缓存管理
```python
# 第一次调用 - 实际生成
result1 = await generator.generate("beautiful sunset")

# 第二次调用 - 从缓存返回
result2 = await generator.generate("beautiful sunset")  # 毫秒级响应
```

### 3. 配置管理
```python
# 多种配置方式自动支持：
# 1. 环境变量: MCP_IMGUTILS_OPENAI_API_KEY
# 2. 配置文件: {"openai": {"api_key": "..."}}
# 3. 命令行: mcp-imgutils set-config openai.api_key your-key
```

### 4. 统计监控
```python
# 获取使用统计
stats = await get_resource_stats()
print(f"缓存命中率: {stats['cache_efficiency']['hit_rate']:.2%}")
```

## 🔧 高级功能

### 自定义重试策略
```python
def get_retry_config(self) -> RetryConfig:
    return RetryConfig(
        max_attempts=5,
        base_delay=1.0,
        exponential_base=1.5,
        retryable_errors=[NetworkError, APIError]
    )
```

### 自定义速率限制
```python
def get_rate_limit(self) -> RateLimit:
    return RateLimit(
        requests_per_second=2.0,
        requests_per_minute=100.0,
        daily_quota=1000
    )
```

### 自定义错误处理
```python
async def _do_generate(self, prompt: str, **kwargs):
    try:
        # API 调用
        pass
    except SpecificAPIError as e:
        # 转换为框架错误
        raise APIError(
            message="OpenAI API 调用失败",
            status_code=e.status_code,
            context=self.create_error_context("generate")
        )
```

## 📊 开发最佳实践

### 1. 错误处理
- 使用框架提供的错误类型
- 提供有用的错误上下文
- 区分可重试和不可重试的错误

### 2. 配置管理
- 使用 `get_config_prefix()` 定义配置命名空间
- 实现 `get_required_keys()` 用于配置验证
- 支持合理的默认值

### 3. 资源管理
- 使用 `_store_generated_image()` 存储图片
- 使用 `_get_cached_image()` 检查缓存
- 让框架处理资源清理

### 4. 测试
- 为每个生成器编写单元测试
- 使用 mock 避免实际 API 调用
- 测试错误情况和边界条件

## 🎯 框架优势总结

1. **开发效率**: 只需关注 API 调用逻辑，框架处理其他一切
2. **用户体验**: 统一的接口和错误处理
3. **性能优化**: 自动缓存和资源管理
4. **企业级**: 完整的配置、监控、错误处理
5. **可维护性**: 标准化的代码结构和测试

通过这个框架，添加新的 AI 模型变得非常简单，只需要几十行核心代码就能享受完整的企业级功能！
