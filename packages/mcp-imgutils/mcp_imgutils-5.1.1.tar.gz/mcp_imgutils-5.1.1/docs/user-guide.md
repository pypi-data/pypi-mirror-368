# 用户使用指南

## 🎯 新架构带来的用户体验提升

Phase 2 完成后，MCP ImageUtils 为用户带来了革命性的体验提升：

## 🚀 主要改进

### 1. 统一的使用体验
**之前**: 只能使用 BFL FLUX，配置复杂
**现在**: 支持多个 AI 模型，统一的调用方式

```python
# 所有模型都使用相同的调用方式
await generate_image_bfl("beautiful sunset")      # BFL FLUX
await generate_image_openai("beautiful sunset")   # OpenAI DALL-E (即将支持)
await generate_image_stability("beautiful sunset") # Stability AI (即将支持)
```

### 2. 智能缓存系统
**之前**: 每次都要重新生成，浪费时间和费用
**现在**: 相同请求直接返回缓存结果

```python
# 第一次调用 - 正常生成时间 (30-60秒)
result1 = await generate_image_bfl("beautiful sunset")

# 第二次调用 - 毫秒级响应！
result2 = await generate_image_bfl("beautiful sunset")  # 从缓存返回
```

### 3. 友好的错误处理
**之前**: 英文错误信息，难以理解
**现在**: 中文错误信息 + 具体解决建议

```
❌ 配置错误: API密钥无效

💡 解决建议:
  1. 请检查API密钥是否正确
  2. 确认API密钥是否已过期
  3. 重新生成API密钥并更新配置

🔧 相关服务: BFL
```

### 4. 简化的配置管理
**之前**: 只能通过环境变量配置
**现在**: 多种配置方式，智能诊断

## 📋 配置方式

### 方式 1: 配置文件 (推荐)
```bash
# 创建配置文件
mcp-imgutils create-example-config

# 编辑 mcp-imgutils.json
{
  "bfl": {
    "api_key": "your-bfl-api-key"
  }
}
```

### 方式 2: 环境变量
```bash
export MCP_IMGUTILS_BFL_API_KEY=your-bfl-api-key
export MCP_IMGUTILS_DEBUG=true
```

### 方式 3: 命令行
```bash
mcp-imgutils set-config bfl.api_key your-bfl-api-key
```

## 🔧 配置诊断工具

### 检查配置状态
```bash
# 显示当前配置
mcp-imgutils config

# 诊断配置问题
mcp-imgutils diagnose

# 验证特定生成器
mcp-imgutils validate --generator bfl
```

### 示例输出
```
=== Configuration Diagnosis ===

BFL Generator:
  ✅ Configuration is valid

OPENAI Generator:
  ❌ Configuration issues found:
    - Missing required configuration: openai.api_key
  
  💡 Suggestions:
    To configure OPENAI API key, you can:
      1. Set environment variable: export MCP_IMGUTILS_OPENAI_API_KEY=your-api-key
      2. Add to config file: {"openai": {"api_key": "your-api-key"}}
      3. Get your OpenAI API key from: https://platform.openai.com/api-keys
```

## 📊 性能监控

### 查看使用统计
```bash
# 获取资源统计
mcp-imgutils get-stats

# 示例输出
{
  "cache_efficiency": {
    "hit_rate": "85.5%",
    "memory_usage": "45.2 MB",
    "disk_usage": "1.2 GB"
  },
  "total_resources": 156,
  "generators": {
    "bfl": 142,
    "openai": 14
  }
}
```

## 🧹 资源管理

### 自动清理
系统会自动清理过期资源，但你也可以手动管理：

```bash
# 清理过期资源
mcp-imgutils cleanup --max-age-hours 24

# 清理特定生成器的资源
mcp-imgutils cleanup --generator bfl

# 限制磁盘使用
mcp-imgutils cleanup --max-disk-size-mb 1000
```

## 🎨 实际使用场景

### 场景 1: 日常图片生成
```python
# Claude 中使用
"请生成一张美丽的日落图片"

# 系统会：
# 1. 检查缓存 (如果之前生成过类似图片)
# 2. 如果缓存未命中，调用 BFL API
# 3. 自动存储到缓存
# 4. 返回图片路径和预览
```

### 场景 2: 批量生成
```python
# 生成多张相关图片
prompts = [
    "beautiful sunset over mountains",
    "beautiful sunset over ocean", 
    "beautiful sunset over city"
]

# 每个 prompt 都会被缓存
# 重复请求会直接返回缓存结果
```

### 场景 3: 错误恢复
```python
# 网络不稳定时
"生成一张图片" 
# -> 网络错误 -> 自动重试 -> 成功

# API 限制时
"生成图片"
# -> 速率限制 -> 智能等待 -> 重试成功

# 配置错误时
"生成图片"
# -> 友好的中文错误提示和解决建议
```

## 📈 性能对比

| 功能 | Phase 1 | Phase 2 | 改进 |
|------|---------|---------|------|
| 重复请求响应时间 | 30-60秒 | 毫秒级 | 🚀 1000x+ |
| 错误理解难度 | 高 | 低 | 😊 用户友好 |
| 配置复杂度 | 高 | 低 | 🔧 多种方式 |
| 磁盘空间管理 | 手动 | 自动 | 🧹 智能清理 |
| 支持模型数量 | 1个 | 无限 | 🎯 可扩展 |
| 错误恢复能力 | 无 | 智能 | 🛡️ 自动重试 |

## 🎯 使用建议

### 1. 首次使用
1. 运行 `mcp-imgutils create-example-config` 创建配置
2. 编辑配置文件添加 API 密钥
3. 运行 `mcp-imgutils diagnose` 验证配置
4. 开始使用！

### 2. 日常使用
- 相同或相似的 prompt 会自动使用缓存
- 系统会自动管理磁盘空间
- 遇到错误时查看具体的解决建议

### 3. 性能优化
- 使用具体的 prompt 以提高缓存命中率
- 定期运行 `mcp-imgutils cleanup` 清理旧文件
- 监控缓存命中率优化使用模式

### 4. 故障排除
- 使用 `mcp-imgutils diagnose` 诊断问题
- 查看 `mcp-imgutils config` 确认配置
- 检查 `mcp-imgutils validate` 验证设置

## 🔮 即将到来的功能

### 更多 AI 模型
- **OpenAI DALL-E 3**: 高质量图片生成
- **Stability AI**: 开源 Stable Diffusion
- **Midjourney**: 艺术风格图片生成

### 高级功能
- **批量生成**: 一次生成多张图片
- **风格控制**: 指定图片风格和参数
- **图片编辑**: 基于 AI 的图片修改

## 💡 小贴士

1. **缓存优化**: 使用清晰、具体的 prompt 可以提高缓存命中率
2. **成本节省**: 缓存系统可以显著减少 API 调用费用
3. **错误处理**: 遇到错误时，仔细阅读解决建议
4. **配置管理**: 使用配置文件比环境变量更方便管理
5. **监控使用**: 定期查看统计信息了解使用情况

通过 Phase 2 的升级，MCP ImageUtils 现在提供了真正的企业级用户体验！
