## [5.1.1](https://github.com/donghao1393/mcp-imgutils/compare/v5.1.0...v5.1.1) (2025-08-08)


### Bug Fixes

* trigger semantic release for security hotfix ([#19](https://github.com/donghao1393/mcp-imgutils/issues/19)) ([8e47870](https://github.com/donghao1393/mcp-imgutils/commit/8e4787056f06c6ef215730a7f49456f876832476))

# [5.1.0](https://github.com/donghao1393/mcp-imgutils/compare/v5.0.0...v5.1.0) (2025-08-08)


### Features

* 为 BFL 生成器添加可选的 download_path 参数 ([#17](https://github.com/donghao1393/mcp-imgutils/issues/17)) ([bdaf423](https://github.com/donghao1393/mcp-imgutils/commit/bdaf423b247e99cc50878445826fe5f24e8e6b57)), closes [#16](https://github.com/donghao1393/mcp-imgutils/issues/16)

# [5.0.0](https://github.com/donghao1393/mcp-imgutils/compare/v4.0.0...v5.0.0) (2025-08-03)


* feat!: implement Phase 2 enterprise multi-model framework ([bafb922](https://github.com/donghao1393/mcp-imgutils/commit/bafb9226ede080749d558f8e9ecc73398e5807d4)), closes [#10](https://github.com/donghao1393/mcp-imgutils/issues/10)


### BREAKING CHANGES

* Major architecture upgrade with new multi-model framework

- Add unified ImageGenerator base class and GeneratorRegistry
- Implement intelligent caching system (Memory + Disk + Cached)
- Add enterprise-grade configuration management
- Implement unified error handling with retry and rate limiting
- Add resource management optimization with auto-cleanup
- Remove CLI interface (MCP is server protocol, not CLI tool)
- Migrate BFL integration to new framework architecture

This release transforms MCP ImageUtils from single BFL support to
enterprise-grade multi-model AI image generation platform.

Performance improvements: 1000x+ faster for repeated requests
Code quality: SonarCloud Quality Gate passed
Test coverage: Complete test suite with 40+ tests
Documentation: 5 comprehensive guides added

# [4.0.0](https://github.com/donghao1393/mcp-imgutils/compare/v3.4.0...v4.0.0) (2025-08-03)


### Reverts

* Revert "feat: add BFL FLUX text-to-image generation support" ([dc0b6f4](https://github.com/donghao1393/mcp-imgutils/commit/dc0b6f44057b7dd2b18f56313805c499d7f57104))
* rollback to Phase 1 stable version ([a0ff5a9](https://github.com/donghao1393/mcp-imgutils/commit/a0ff5a90d6d90c6174058c3c3f000ac62e4f36df))


### BREAKING CHANGES

* Revert all Phase 2 changes to return to stable Phase 1 implementation

# [3.0.0](https://github.com/donghao1393/mcp-imgutils/compare/v2.1.2...v3.0.0) (2025-08-03)


### Reverts

* rollback to Phase 1 stable version ([a0ff5a9](https://github.com/donghao1393/mcp-imgutils/commit/a0ff5a90d6d90c6174058c3c3f000ac62e4f36df))


### BREAKING CHANGES

* Revert all Phase 2 changes to return to stable Phase 1 implementation

# [3.0.0](https://github.com/donghao1393/mcp-imgutils/compare/v2.1.2...v3.0.0) (2025-08-03)


### Reverts

* rollback to Phase 1 stable version ([a0ff5a9](https://github.com/donghao1393/mcp-imgutils/commit/a0ff5a90d6d90c6174058c3c3f000ac62e4f36df))


### BREAKING CHANGES

* Revert all Phase 2 changes to return to stable Phase 1 implementation

## [2.1.2](https://github.com/donghao1393/mcp-imgutils/compare/v2.1.1...v2.1.2) (2025-08-02)


### Bug Fixes

* 完善所有工具描述的URL图片支持说明 ([#8](https://github.com/donghao1393/mcp-imgutils/issues/8)) ([259fa76](https://github.com/donghao1393/mcp-imgutils/commit/259fa76fc25d6fdcc35259902cebabecffa5b1c0)), closes [#7](https://github.com/donghao1393/mcp-imgutils/issues/7)

## [2.1.1](https://github.com/donghao1393/mcp-imgutils/compare/v2.1.0...v2.1.1) (2025-08-02)


### Bug Fixes

* 更新工具描述使LLM能识别URL图片支持 ([9341270](https://github.com/donghao1393/mcp-imgutils/commit/9341270206bde74de4a9d49e2187577792ae58a5))

# [2.1.0](https://github.com/donghao1393/mcp-imgutils/compare/v2.0.1...v2.1.0) (2025-08-02)


### Features

* 支持从URL读取图片 ([#6](https://github.com/donghao1393/mcp-imgutils/issues/6)) ([32d992d](https://github.com/donghao1393/mcp-imgutils/commit/32d992d8ffc372162bd5f4872308726f4783539a)), closes [#5](https://github.com/donghao1393/mcp-imgutils/issues/5)

## [2.0.1](https://github.com/donghao1393/mcp-imgutils/compare/v2.0.0...v2.0.1) (2025-08-02)


### Bug Fixes

* 修复重构后的CI失败问题 ([#4](https://github.com/donghao1393/mcp-imgutils/issues/4)) ([9c90162](https://github.com/donghao1393/mcp-imgutils/commit/9c9016271bea6019a64bd4135f56069ebf73cabf))

# [2.0.0](https://github.com/donghao1393/mcp-imgutils/compare/v1.4.4...v2.0.0) (2025-08-02)


### Code Refactoring

* 完全重构项目结构以对齐dbutils模式 ([01e92ab](https://github.com/donghao1393/mcp-imgutils/commit/01e92ab737c588454cf361375613f1a6f597a3b4))


### BREAKING CHANGES

* 重构包结构和入口点

- 重命名包目录: src/imgutils/ → src/mcp_imgutils/
- 更新入口点: mcp-imgutils = "mcp_imgutils:main"
- 重构主函数: 将__main__.py逻辑移到__init__.py中的main()函数
- 更新构建配置: packages = ["src/mcp_imgutils"]
- 修复所有测试文件中的导入路径

现在完全对齐dbutils的项目结构:
- 包名: mcp-imgutils (PyPI, 连字符)
- 源码: src/mcp_imgutils/ (下划线)
- 可执行文件: mcp-imgutils (连字符)
- 入口点: mcp_imgutils:main (下划线)

这解决了uvx兼容性问题，现在uvx mcp-imgutils可以正常工作

## [1.4.4](https://github.com/donghao1393/mcp-imgutils/compare/v1.4.3...v1.4.4) (2025-08-02)


### Bug Fixes

* 修复可执行文件名称不匹配问题 ([58fb85d](https://github.com/donghao1393/mcp-imgutils/commit/58fb85d8a741b8a40e2fe6daee73fc625ed3f8f6))

## [1.4.3](https://github.com/donghao1393/mcp-imgutils/compare/v1.4.2...v1.4.3) (2025-08-02)


### Bug Fixes

* 修复PyPI构建失败问题 ([2b67ecc](https://github.com/donghao1393/mcp-imgutils/commit/2b67ecc1139b7e99bb1e04986d893f0eb20d3567))

## [1.4.2](https://github.com/donghao1393/mcp-imgutils/compare/v1.4.1...v1.4.2) (2025-08-02)


### Bug Fixes

* 修复PyPI项目名称不匹配问题 ([fb2b57a](https://github.com/donghao1393/mcp-imgutils/commit/fb2b57a401dd67aee0fdc3ff700ed5653c66c438))

## [1.4.1](https://github.com/donghao1393/mcp-imgutils/compare/v1.4.0...v1.4.1) (2025-08-02)


### Bug Fixes

* 修复文档中关于MCP配置的错误 ([204a362](https://github.com/donghao1393/mcp-imgutils/commit/204a362f6eac06b41301ee95f6859b0878e245d1))

# [1.4.0](https://github.com/donghao1393/mcp-imgutils/compare/v1.3.0...v1.4.0) (2025-08-02)


### Features

* 添加EXIF元数据支持 ([#3](https://github.com/donghao1393/mcp-imgutils/issues/3)) ([dae9d09](https://github.com/donghao1393/mcp-imgutils/commit/dae9d09e0f5b73fe446e5bae999b1a105155d04b)), closes [#2](https://github.com/donghao1393/mcp-imgutils/issues/2)

# [1.3.0](https://github.com/donghao1393/mcp-imgutils/compare/v1.2.1...v1.3.0) (2025-08-02)


### Features

* 整合图片信息到view_image并修复get_image_info bug ([#1](https://github.com/donghao1393/mcp-imgutils/issues/1)) ([05908af](https://github.com/donghao1393/mcp-imgutils/commit/05908af0f7125057f4e95fa4ca514813a431be97))

# [1.2.0](https://github.com/donghao1393/mcp-imgutils/compare/v1.1.1...v1.2.0) (2025-08-01)


### Features

* 采用Desktop Commander的图片处理方法 ([0cca373](https://github.com/donghao1393/mcp-imgutils/commit/0cca37377fe2c612497c4cfcb9d2706f34c9b377))

## [1.1.1](https://github.com/donghao1393/mcp-imgutils/compare/v1.1.0...v1.1.1) (2025-08-01)


### Bug Fixes

* 修复代码风格问题 ([52f805f](https://github.com/donghao1393/mcp-imgutils/commit/52f805ff10a92ba6cf112b8e23590b6d65188946))

# [1.1.0](https://github.com/donghao1393/mcp-imgutils/compare/v1.0.3...v1.1.0) (2025-08-01)


### Features

* 实现智能图片压缩以适应MCP响应大小限制 ([142061b](https://github.com/donghao1393/mcp-imgutils/commit/142061bc6cd69521e57a856ec9b1055fbdec1d1e))

## [1.0.3](https://github.com/donghao1393/mcp-imgutils/compare/v1.0.2...v1.0.3) (2025-04-07)


### Bug Fixes

* 修复代码风格和集成测试问题 ([ac6775f](https://github.com/donghao1393/mcp-imgutils/commit/ac6775feac25fc9eed0d21d2405f7bf7cbb05cb1))

## [1.0.2](https://github.com/donghao1393/mcp-imgutils/compare/v1.0.1...v1.0.2) (2025-04-07)


### Bug Fixes

* 修复代码风格和测试问题 ([c530ce9](https://github.com/donghao1393/mcp-imgutils/commit/c530ce9d5f9cb4229dca03689f16138bda774c69))

## [1.0.1](https://github.com/donghao1393/mcp-imgutils/compare/v1.0.0...v1.0.1) (2025-04-07)


### Bug Fixes

* 修复CI/CD工作流问题 ([29f308b](https://github.com/donghao1393/mcp-imgutils/commit/29f308b99e9402cac7aeb6a58cb0ad46316c1d55))

# 1.0.0 (2025-04-07)


### Features

* 添加CI/CD配置和测试框架 ([d8b9576](https://github.com/donghao1393/mcp-imgutils/commit/d8b9576fb82a1ee98486b2e1e4011a02635ebcb2))
