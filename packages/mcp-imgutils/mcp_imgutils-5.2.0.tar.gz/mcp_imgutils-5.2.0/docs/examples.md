# 📚 MCP ImageUtils 使用示例

本文档提供了详细的使用示例，涵盖基本用法、高级配置和错误处理等场景。

## 🎨 图片生成示例

### 基本图片生成

#### 使用 BFL FLUX 模型

```text
用户: 请用BFL生成一张美丽的日落风景图片

Claude: 我来为您使用BFL FLUX模型生成一张美丽的日落风景图片。

[调用 generate_image_bfl 工具]
- prompt: "Beautiful sunset landscape"
- model: "flux-dev"
- preset_size: "default"

✅ 图片生成成功！
📁 本地路径: ~/Pictures/BFL_Generated/20250803_131535_flux-dev_1920x1080_beautiful_sunset_landscape_abc123.jpg
📝 提示词文件: ~/Pictures/BFL_Generated/20250803_131535_flux-dev_1920x1080_beautiful_sunset_landscape_abc123.txt

[自动调用 view_image 工具显示生成的图片]
```

#### 使用 OpenAI DALL-E 模型

```text
用户: 请用OpenAI生成一张美丽的日落风景图片

Claude: 我来为您使用OpenAI DALL-E模型生成一张美丽的日落风景图片。

[调用 generate_image_openai 工具]
- prompt: "美丽的日落风景图片"
- model: "dall-e-3"
- preset_size: "default"

✅ 图片生成成功！
📁 本地路径: ~/Pictures/OpenAI_Generated/20250803_131535_dall-e-3_1024x1024_beautiful_sunset_landscape_abc123.jpg
📝 提示词文件: ~/Pictures/OpenAI_Generated/20250803_131535_dall-e-3_1024x1024_beautiful_sunset_landscape_abc123.txt

[自动调用 view_image 工具显示生成的图片]
```

### 高级配置示例

#### 指定模型和质量

```text
用户: 用DALL-E 3的高清模式生成一张科幻城市的横向图片

Claude: [调用 generate_image_openai 工具]
- prompt: "科幻城市"
- model: "dall-e-3"
- quality: "hd"
- preset_size: "landscape"
- style: "vivid"

✅ 图片生成成功！使用了DALL-E 3的高清模式，生成了1792x1024的横向科幻城市图片。
```

#### 自定义尺寸

```text
用户: 用BFL生成一张1280x720的游戏截图风格图片

Claude: [调用 generate_image_bfl 工具]
- prompt: "Game screenshot style image"
- model: "flux-pro"
- width: 1280
- height: 720

✅ 图片生成成功！生成了指定尺寸的游戏风格图片。
```

#### 临时指定保存路径

```text
用户: 生成一张图片并保存到我的项目文件夹

Claude: [调用 generate_image_openai 工具]
- prompt: "项目相关图片"
- download_path: "/Users/john/Projects/MyProject/images"

✅ 图片已保存到指定的项目文件夹中。
```

## 📊 图片分析示例

### 本地图片分析

```text
用户: 请分析这张照片的拍摄参数 /Users/john/Photos/sunset.jpg

Claude: [调用 view_image 工具]

图片详细信息:
文件名: sunset.jpg
文件路径: /Users/john/Photos/sunset.jpg
文件大小: 2,456,789 字节 (2.34 MB)
图片格式: JPEG
分辨率: 4032 x 3024
颜色模式: RGB
总像素数: 12,192,768

EXIF元数据:
Make: Apple
Model: iPhone 14 Pro
Software: 16.6
DateTime: 2023:08:03 18:45:23
ExposureTime: 1/120
FNumber: 1.78
ISOSpeedRatings: 64
FocalLength: 6.86
Flash: 16 (Flash did not fire)
ColorSpace: 1 (sRGB)

这是一张用iPhone 14 Pro拍摄的日落照片，拍摄参数显示使用了较快的快门速度(1/120秒)和较低的ISO(64)，说明当时光线条件良好。
```

### 网络图片分析

```text
用户: 请分析这张网络图片 https://example.com/photo.jpg

Claude: [调用 view_image 工具]

图片详细信息:
文件名: URL: https://example.com/photo.jpg
文件路径: /tmp/tmp9rizrzqv.jpg
文件大小: 890,234 字节 (869.37 KB)
图片格式: JPEG
分辨率: 1920 x 1080
颜色模式: RGB
总像素数: 2,073,600

这是一张Full HD分辨率的网络图片，文件大小适中，适合网络传输。
```

## ⚠️ 错误处理示例

### API密钥未配置

```text
用户: 生成一张图片

Claude: ❌ 错误：API密钥未配置

请配置相应的API密钥：
- BFL模型需要配置 BFL_API_KEY
- OpenAI模型需要配置 OPENAI_API_KEY

配置方法：
1. 在Claude Desktop配置文件中添加环境变量
2. 或设置系统环境变量

详细配置说明请参考README.md文档。
```

### 文件不存在

```text
用户: 分析这张图片 /path/to/nonexistent.jpg

Claude: [调用 view_image 工具]

❌ 错误：文件不存在
文件路径: /path/to/nonexistent.jpg

请检查：
1. 文件路径是否正确
2. 文件是否存在
3. 是否有访问权限
```

### 网络图片访问失败

```text
用户: 分析这张网络图片 https://invalid-url.com/image.jpg

Claude: [调用 view_image 工具]

❌ 错误：无法访问网络图片
URL: https://invalid-url.com/image.jpg

可能的原因：
1. URL地址错误
2. 网络连接问题
3. 图片已被删除或移动
4. 服务器访问限制

请检查URL是否正确，或尝试其他图片。
```

### 不支持的文件格式

```text
用户: 分析这个文件 /path/to/document.pdf

Claude: [调用 view_image 工具]

❌ 错误：不支持的文件格式
文件类型: PDF

支持的图片格式：
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)
- BMP (.bmp)
- TIFF (.tiff, .tif)

请使用支持的图片格式。
```

## 🔧 高级用法

### 批量处理

```text
用户: 我需要为我的网站生成一套图标，包括不同尺寸

Claude: 我来为您生成一套不同尺寸的网站图标。

[生成多张不同尺寸的图片]
1. 生成 1024x1024 的主图标
2. 生成 512x512 的中等图标  
3. 生成 256x256 的小图标
4. 生成 128x128 的缩略图标

所有图标都已保存到指定目录，并保持一致的设计风格。
```

### 风格一致性

```text
用户: 生成一系列产品展示图片，要求风格一致

Claude: 我来为您生成风格一致的产品展示图片系列。

[使用相同的基础提示词和参数]
- 统一的光照设置
- 一致的背景风格
- 相同的构图角度
- 统一的色彩方案

这样可以确保所有产品图片在视觉上保持一致性。
```

## 💡 最佳实践

### 提示词优化

**好的提示词示例**：
```text
"A professional product photo of a modern smartphone on a clean white background, studio lighting, high resolution, commercial photography style"
```

**避免的提示词**：
```text
"手机图片"  # 太简单，缺乏细节
```

### 尺寸选择建议

- **社交媒体**: 使用对应的预设尺寸（如 instagram_square）
- **网站横幅**: 使用 landscape 或自定义宽屏比例
- **打印用途**: 选择高分辨率，考虑DPI要求
- **移动应用**: 使用 mobile_portrait 或 square

### 模型选择建议

- **艺术创作**: BFL FLUX 模型，特别是 flux-pro 系列
- **商业用途**: OpenAI DALL-E 3，质量稳定可靠
- **快速原型**: BFL flux-dev，免费且速度快
- **高质量需求**: OpenAI DALL-E 3 HD 模式

---

*💡 更多示例和用法请参考 [用户指南](user-guide-image-generation.md)*
