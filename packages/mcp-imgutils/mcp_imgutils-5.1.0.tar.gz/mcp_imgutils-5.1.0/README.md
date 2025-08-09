# MCP图片工具服务

这是一个基于Model Context Protocol (MCP)的全方位图片工具服务，提供图片分析和AI图片生成功能。

## 功能特性

### 📊 图片分析功能
- **🖼️ 图片查看与分析**: 将本地图片和网络图片转换为LLM可分析的格式
- **🌐 URL图片支持**: 直接支持HTTP/HTTPS图片URL，无需下载到本地
- **📊 完整图片信息**: 获取分辨率、大小、格式、颜色模式等技术参数
- **📷 EXIF元数据提取**: 提取拍摄参数、设备信息、GPS数据等完整EXIF信息
- **🔄 智能格式处理**: 自动处理各种图片格式和大小调整
- **🔒 安全验证**: URL格式验证、Content-Type检查、超时控制
- **🧹 自动清理**: 临时文件自动管理，无磁盘泄漏
- **📝 专业术语支持**: 保持英文EXIF键名，便于LLM理解专业摄影术语

### 🎨 AI图片生成功能
- **🚀 BFL FLUX模型**: 支持Black Forest Labs的FLUX系列模型
- **🎯 多模型选择**: flux-pro-1.1, flux-pro-1.1-ultra, flux-pro, flux-dev
- **📐 智能尺寸**: 预设尺寸和自定义尺寸，自动调整到最佳参数
- **⚡ 高质量生成**: 业界领先的文本生成图片质量
- **📁 本地保存**: 图片自动下载到本地目录，避免大文件传输问题
- **🛡️ 完整错误处理**: API限制、网络错误、参数验证等全面处理
- **🔄 智能工作流**: 生成后可直接使用view_image工具查看分析

## 安装

确保已安装必要的依赖：

```bash
uv install
# 或者
pip install -e .
```

## 使用方法

### Claude Desktop配置

这是一个MCP服务器，需要通过Claude Desktop配置使用。

**配置文件位置**:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**配置内容**:

在Claude Desktop的配置文件中添加以下配置：

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

### 🔑 API密钥配置

#### BFL (Black Forest Labs) API密钥

要使用AI图片生成功能，需要配置BFL API密钥：

1. **获取API密钥**: 访问 [BFL API Portal](https://api.bfl.ai/) 注册并获取API密钥
2. **配置方式**:
   - **方式1 (推荐)**: 在Claude Desktop配置中添加环境变量（如上所示）
   - **方式2**: 设置系统环境变量 `export BFL_API_KEY=your-api-key`

#### 图片保存目录配置（可选）

默认情况下，生成的图片保存到：
- **Windows/macOS**: `~/Pictures/BFL_Generated/`
- **Linux**: `~/Pictures/BFL_Generated/` 或 `~/BFL_Generated/`

自定义保存目录：
```json
{
  "mcpServers": {
    "mcp-imgutils": {
      "command": "uvx",
      "args": ["mcp-imgutils"],
      "env": {
        "BFL_API_KEY": "your-bfl-api-key-here",
        "BFL_IMAGE_SAVE_DIR": "~/MyImages/AI_Generated"
      }
    }
  }
}
```

**注意**:

- 必须使用绝对路径，不能使用相对路径
- 配置完成后需要重启Claude Desktop
- 没有API密钥时，图片生成功能将不可用，但图片分析功能正常工作

## 工具使用示例

一旦服务运行起来，你可以在Claude中使用以下工具：

### 📊 view_image - 图片查看与分析

查看并分析本地图片或网络图片，获取完整的图片信息和EXIF元数据。

### 🎨 generate_image_bfl - AI图片生成

使用BFL FLUX模型生成高质量图片。

**view_image参数:**

- `image_path` - 图片文件的完整路径或HTTP/HTTPS URL
- `max_file_size` (可选) - 允许的最大文件大小（字节，默认5MB，仅适用于本地文件）

**generate_image_bfl参数:**

- `prompt` (必需) - 图片描述文本
  - ⚠️ **语言支持**: BFL FLUX模型主要支持英文提示词，建议使用英文以获得最佳效果
- `model` (可选) - FLUX模型选择：
  - `flux-dev` (默认) - 开发版本，免费使用
  - `flux-pro` - 专业版本，更高质量
  - `flux-pro-1.1` - 最新专业版本
  - `flux-pro-1.1-ultra` - 超高质量版本
- `preset_size` (可选) - 预设尺寸，如：
  - `desktop_fhd` - 桌面壁纸 Full HD
  - `mobile_portrait` - 手机竖屏
  - `instagram_square` - Instagram正方形
  - `default` - 默认尺寸 (1920x1080 Full HD)
- `width`, `height` (可选) - 自定义尺寸（如果不使用preset_size）

**💡 智能默认**: 不指定尺寸时使用1920x1080 (Full HD)，适合现代屏幕。
**🎯 用户友好**: 用户可描述用途（如"桌面壁纸"、"手机壁纸"），LLM自动选择最佳设置。

**支持的图片来源:**

- **本地文件**: `/Users/john/Photos/sunset.jpg`
- **网络图片**: `https://example.com/image.jpg`
- **各种域名**: 支持任何可访问的HTTP/HTTPS图片URL

**返回内容:**

1. **详细的图片信息文本**，包括：
   - 文件名、路径、大小
   - 图片格式、分辨率、颜色模式
   - 总像素数等技术参数

2. **EXIF元数据**（如果有），包括：
   - 拍摄设备信息（Make, Model, Software）
   - 拍摄参数（ExposureTime, FNumber, ISOSpeedRatings, FocalLength）
   - 拍摄时间（DateTime, DateTimeOriginal）
   - 技术参数（ColorSpace, Flash, MeteringMode）
   - 所有其他可用的EXIF字段

3. **图片的视觉内容**，供LLM进行图像分析

### 使用示例

配置完成后，在Claude Desktop中：

#### 📊 本地图片分析

```text
用户: 请分析这张照片 /Users/john/Photos/sunset.jpg

Claude: [调用 view_image 工具]
```

#### 🌐 网络图片分析

```text
用户: 请分析这张网络图片 https://example.com/photo.jpg

Claude: [调用 view_image 工具]
```

#### 🎨 AI图片生成

```text
用户: 请用BFL生成一张中国女孩的图片

Claude: [调用 generate_image_bfl 工具]
       ✅ 图片生成成功！
       📁 本地路径: ~/Pictures/BFL_Generated/20250803_131535_flux-dev_1024x768_Chinese_girl_abc123.jpg

       [自动调用 view_image 工具显示生成的图片]
```

#### 🎯 指定模型和尺寸生成

```text
用户: 用flux-pro模型生成一张1280x720的科幻城市图片

Claude: [调用 generate_image_bfl 工具，参数：
- prompt: "科幻城市"
- model: "flux-pro"
- width: 1280
- height: 720]
```

#### 📐 使用预设尺寸

```text
用户: 生成一张适合Instagram的正方形图片，内容是可爱的小猫

Claude: [调用 generate_image_bfl 工具，参数：
- prompt: "可爱的小猫"
- preset_size: "instagram_square"]
```
FNumber: 1.8
ISOSpeedRatings: 64
FocalLength: 5.7
Flash: 16
ColorSpace: 1
...

[同时显示图片内容供分析]
```

#### 网络图片分析

```text
用户: 请分析这张网络图片 https://img.youtube.com/vi/iv-5mZ_9CPY/maxresdefault.jpg

Claude: [调用 view_image 工具]

返回结果:
图片详细信息:
文件名: URL: https://img.youtube.com/vi/iv-5mZ_9CPY/maxresdefault.jpg
文件路径: /tmp/tmp9rizrzqv.jpg
文件大小: 290,434 字节 (283.63 KB, 0.28 MB)
图片格式: JPEG
分辨率: 1280 x 720
颜色模式: RGB
总像素数: 921,600

[同时显示图片内容供分析]
```

## 🌐 URL图片支持

### 支持的URL类型

- **HTTP/HTTPS协议**: `http://` 和 `https://` 开头的URL
- **各种域名**: 支持任何可公开访问的图片URL
- **常见图片网站**:
  - YouTube缩略图: `https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg`
  - 社交媒体图片: Twitter、Instagram、Facebook等
  - 图片托管服务: Imgur、Flickr、Google Photos等
  - CDN图片: 各种内容分发网络的图片

### 安全特性

- **协议限制**: 仅允许HTTP和HTTPS协议，拒绝其他协议
- **Content-Type验证**: 确保URL返回的是图片内容
- **超时控制**: 30秒下载超时，避免长时间等待
- **自动重定向**: 支持最多5次重定向跟踪
- **临时文件管理**: 下载的图片存储在系统临时目录，处理完自动清理

### 使用注意事项

- **网络连接**: 需要稳定的网络连接访问外部URL
- **访问权限**: 某些网站可能有防爬虫机制，可能无法访问
- **文件大小**: URL图片不受本地文件大小限制，遵循MCP协议处理
- **隐私考虑**: 访问URL时会暴露您的IP地址给目标服务器

## 支持的图片格式

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- WebP (.webp)

### 图片处理

- 默认最大文件大小限制为5MB
- 所有非JPEG格式的图片会被转换为JPEG以减小大小
- 对于包含透明通道的图片（如PNG），会在转换时添加白色背景
- 使用优化的JPEG压缩算法减小输出文件大小

### 错误处理

服务包含全面的错误处理机制：

**本地文件错误:**

- 图片路径验证（文件是否存在）
- 文件大小检查
- 图片格式验证
- 文件权限检查

**网络图片错误:**

- URL格式验证
- 网络连接错误（超时、DNS失败等）
- HTTP状态错误（404、403、500等）
- Content-Type验证（确保是图片内容）
- 下载失败处理

**通用错误:**

- 异常捕获和友好错误消息
- 临时文件清理（即使出错也会清理）

## EXIF元数据支持

该服务提供完整的EXIF元数据提取功能：

### 支持的EXIF信息类型

- **设备信息**: 相机品牌、型号、软件版本
- **拍摄参数**: 曝光时间、光圈值、ISO感光度、焦距
- **拍摄时间**: 拍摄时间、数字化时间、原始时间
- **技术参数**: 色彩空间、闪光灯设置、测光模式、曝光程序
- **图片属性**: EXIF图片尺寸、方向信息
- **GPS信息**: 地理位置数据（如果有）
- **其他元数据**: 所有可用的EXIF标签

### EXIF数据处理特性

- **智能类型处理**: 自动处理字节数据、分数值、浮点数等不同数据类型
- **英文键名**: 保持原始EXIF标签名，便于LLM理解专业术语
- **优雅降级**: 没有EXIF数据的图片不会显示空白部分
- **完整提取**: 提取所有可用的EXIF字段，不预设限制

## 扩展性

该服务设计为可扩展的，未来可以添加更多功能：

- **更多图片格式**: 支持RAW格式、HEIC等
- **图片预处理**: 裁剪、缩放、旋转等操作
- **高级分析**: 颜色分布、直方图、对象检测
- **批量处理**: 同时处理多个图片文件或URL
- **AI增强**: 图片质量评估、场景识别等
- **缓存机制**: URL图片智能缓存，提高重复访问性能
- **代理支持**: 支持HTTP代理访问受限网络中的图片
- **认证支持**: 支持需要认证的私有图片URL

## 注意事项

### 文件路径

- 图片路径必须是完整的绝对路径
- 支持跨平台路径格式（Windows、macOS、Linux）

### 隐私与安全

- 服务不会修改原始图片文件
- 图片数据不会被永久存储，仅在处理过程中临时使用
- EXIF数据可能包含敏感信息（如GPS位置），请注意隐私保护

### 性能考虑

- 默认最大文件大小限制为5MB，可通过参数调整
- 大型图片会自动进行质量优化以减小传输大小
- EXIF提取对性能影响很小，适合实时使用

### 兼容性

- 支持所有主流图片格式的EXIF数据
- 某些格式（如PNG、GIF）可能不包含EXIF信息
- AI生成的图片通常不包含传统的拍摄参数EXIF数据
