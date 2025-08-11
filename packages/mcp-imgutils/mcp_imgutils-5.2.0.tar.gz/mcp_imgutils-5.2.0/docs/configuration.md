# ⚙️ MCP ImageUtils 配置指南

本文档详细说明了 MCP ImageUtils 的所有配置选项、环境变量、默认值和安全注意事项。

## 🔑 API密钥配置

### BFL (Black Forest Labs) API密钥

**环境变量**: `BFL_API_KEY`

**获取方式**:
1. 访问 [BFL API Portal](https://api.bfl.ai/)
2. 注册账户并获取API密钥
3. 配置到环境变量中

**配置示例**:
```json
{
  "mcpServers": {
    "mcp-imgutils": {
      "command": "uvx",
      "args": ["mcp-imgutils"],
      "env": {
        "BFL_API_KEY": "your-bfl-api-key-here"
      }
    }
  }
}
```

**系统环境变量**:
```bash
export BFL_API_KEY="your-bfl-api-key-here"
```

### OpenAI API密钥

**环境变量**: `OPENAI_API_KEY`

**获取方式**:
1. 访问 [OpenAI API Portal](https://platform.openai.com/api-keys)
2. 注册账户并获取API密钥
3. 配置到环境变量中

**配置示例**:
```json
{
  "mcpServers": {
    "mcp-imgutils": {
      "command": "uvx",
      "args": ["mcp-imgutils"],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key-here"
      }
    }
  }
}
```

**系统环境变量**:
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

## 📁 图片保存目录配置

### BFL 图片保存目录

**环境变量**: `BFL_IMAGE_SAVE_DIR`

**默认值**:
- **Windows**: `%USERPROFILE%\Pictures\BFL_Generated\`
- **macOS**: `~/Pictures/BFL_Generated/`
- **Linux**: `~/Pictures/BFL_Generated/` 或 `~/BFL_Generated/`（如果Pictures目录不存在）

**自定义配置**:
```json
{
  "env": {
    "BFL_IMAGE_SAVE_DIR": "~/MyImages/BFL_Generated"
  }
}
```

**系统环境变量**:
```bash
export BFL_IMAGE_SAVE_DIR="~/MyImages/BFL_Generated"
```

### OpenAI 图片保存目录

**环境变量**: `OPENAI_IMAGE_SAVE_DIR`

**默认值**:
- **Windows**: `%USERPROFILE%\Pictures\OpenAI_Generated\`
- **macOS**: `~/Pictures/OpenAI_Generated/`
- **Linux**: `~/Pictures/OpenAI_Generated/` 或 `~/OpenAI_Generated/`（如果Pictures目录不存在）

**自定义配置**:
```json
{
  "env": {
    "OPENAI_IMAGE_SAVE_DIR": "~/MyImages/OpenAI_Generated"
  }
}
```

**系统环境变量**:
```bash
export OPENAI_IMAGE_SAVE_DIR="~/MyImages/OpenAI_Generated"
```

## 🔧 高级配置选项

### 图片文件大小限制

**环境变量**: `MAX_IMAGE_FILE_SIZE`

**默认值**: `5242880` (5MB)

**说明**: 限制本地图片文件的最大大小（字节）

**配置示例**:
```bash
export MAX_IMAGE_FILE_SIZE="10485760"  # 10MB
```

### 网络请求超时

**环境变量**: `HTTP_TIMEOUT`

**默认值**: `30` (秒)

**说明**: 网络图片下载的超时时间

**配置示例**:
```bash
export HTTP_TIMEOUT="60"  # 60秒
```

### 临时文件清理

**环境变量**: `TEMP_FILE_CLEANUP`

**默认值**: `true`

**说明**: 是否自动清理临时文件

**配置示例**:
```bash
export TEMP_FILE_CLEANUP="false"  # 禁用自动清理
```

## 🛡️ 安全注意事项

### API密钥安全

1. **不要在代码中硬编码API密钥**
   ```bash
   # ❌ 错误做法
   BFL_API_KEY="sk-1234567890abcdef"
   
   # ✅ 正确做法
   BFL_API_KEY="${BFL_API_KEY}"
   ```

2. **使用环境变量或配置文件**
   - 将API密钥存储在环境变量中
   - 不要将包含API密钥的配置文件提交到版本控制

3. **定期轮换API密钥**
   - 定期更新API密钥
   - 监控API密钥使用情况

### 文件路径安全

1. **使用绝对路径**
   ```bash
   # ✅ 推荐
   BFL_IMAGE_SAVE_DIR="/Users/john/Images/AI_Generated"
   
   # ⚠️ 避免相对路径
   BFL_IMAGE_SAVE_DIR="./images"
   ```

2. **路径权限检查**
   - 确保指定的目录有写入权限
   - 避免使用系统敏感目录

3. **路径验证**
   - 系统会自动验证路径安全性
   - 拒绝访问系统关键目录

### 网络安全

1. **URL验证**
   - 仅支持HTTP和HTTPS协议
   - 自动拒绝其他协议（如file://、ftp://等）

2. **文件类型验证**
   - 仅处理支持的图片格式
   - 自动检测和拒绝恶意文件

## 📊 默认配置汇总

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| BFL API密钥 | `BFL_API_KEY` | 无 | 必需，用于BFL模型 |
| OpenAI API密钥 | `OPENAI_API_KEY` | 无 | 必需，用于DALL-E模型 |
| BFL保存目录 | `BFL_IMAGE_SAVE_DIR` | `~/Pictures/BFL_Generated/` | BFL图片保存位置 |
| OpenAI保存目录 | `OPENAI_IMAGE_SAVE_DIR` | `~/Pictures/OpenAI_Generated/` | DALL-E图片保存位置 |
| 文件大小限制 | `MAX_IMAGE_FILE_SIZE` | `5242880` (5MB) | 本地图片文件大小限制 |
| 网络超时 | `HTTP_TIMEOUT` | `30` (秒) | 网络请求超时时间 |
| 临时文件清理 | `TEMP_FILE_CLEANUP` | `true` | 是否自动清理临时文件 |

## 🔍 配置验证

### 检查配置状态

使用以下命令检查配置是否正确：

```bash
# 检查环境变量
echo $BFL_API_KEY
echo $OPENAI_API_KEY
echo $BFL_IMAGE_SAVE_DIR
echo $OPENAI_IMAGE_SAVE_DIR

# 检查目录权限
ls -la ~/Pictures/BFL_Generated/
ls -la ~/Pictures/OpenAI_Generated/
```

### 常见配置问题

1. **API密钥无效**
   - 检查密钥格式是否正确
   - 确认密钥是否已激活
   - 检查账户余额是否充足

2. **目录权限问题**
   - 确保目录存在且可写
   - 检查文件系统权限
   - 避免使用受保护的系统目录

3. **路径格式问题**
   - 使用正确的路径分隔符
   - 避免使用特殊字符
   - 确保路径编码正确

## 🚀 性能优化配置

### 并发请求限制

**环境变量**: `MAX_CONCURRENT_REQUESTS`

**默认值**: `3`

**说明**: 同时进行的API请求数量限制

```bash
export MAX_CONCURRENT_REQUESTS="5"
```

### 缓存配置

**环境变量**: `ENABLE_CACHE`

**默认值**: `true`

**说明**: 是否启用结果缓存

```bash
export ENABLE_CACHE="false"  # 禁用缓存
```

### 日志级别

**环境变量**: `LOG_LEVEL`

**默认值**: `INFO`

**可选值**: `DEBUG`, `INFO`, `WARNING`, `ERROR`

```bash
export LOG_LEVEL="DEBUG"  # 启用调试日志
```

---

*💡 配置完成后，请重启Claude Desktop以使配置生效*
