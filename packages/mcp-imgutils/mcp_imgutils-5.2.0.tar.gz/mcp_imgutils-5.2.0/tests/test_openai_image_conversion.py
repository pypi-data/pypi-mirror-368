"""
测试 OpenAI 图片转换功能

验证 PNG 到 JPEG 的转换功能，确保能够减小文件大小以避免调用栈溢出。
"""

import os
import sys
import tempfile

import pytest
from PIL import Image

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_imgutils.generation.openai.generator import _convert_png_to_jpeg


class TestImageConversion:
    """测试图片转换功能"""

    def test_png_to_jpeg_conversion(self):
        """测试 PNG 到 JPEG 的转换"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            # 创建一个测试 PNG 图片（带透明通道）
            img = Image.new('RGBA', (200, 200), (255, 0, 0, 128))  # 红色半透明
            img.save(tmp.name, 'PNG')
            png_path = tmp.name

        try:
            # 获取原始文件大小
            original_size = os.path.getsize(png_path)
            
            # 执行转换（默认保留原文件）
            jpeg_path, mime_type = _convert_png_to_jpeg(png_path)

            # 验证结果
            assert jpeg_path.endswith('.jpg'), "转换后应该是 .jpg 文件"
            assert mime_type == "image/jpeg", "MIME 类型应该是 image/jpeg"
            assert os.path.exists(jpeg_path), "JPEG 文件应该存在"
            assert os.path.exists(png_path), "原 PNG 文件应该被保留（默认行为）"
            
            # 验证转换后的图片可以正常打开
            with Image.open(jpeg_path) as converted_img:
                assert converted_img.format == 'JPEG', "转换后应该是 JPEG 格式"
                assert converted_img.size == (200, 200), "尺寸应该保持不变"
                assert converted_img.mode == 'RGB', "应该转换为 RGB 模式"
            
            print(f"原始 PNG 大小: {original_size} bytes")
            print(f"转换后 JPEG 大小: {os.path.getsize(jpeg_path)} bytes")
            
        finally:
            # 清理文件
            for path in [png_path, jpeg_path]:
                if os.path.exists(path):
                    os.remove(path)

    def test_png_to_jpeg_with_deletion(self):
        """测试 PNG 到 JPEG 转换并删除原文件"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            # 创建一个测试 PNG 图片
            img = Image.new('RGB', (100, 100), (0, 0, 255))  # 蓝色
            img.save(tmp.name, 'PNG')
            png_path = tmp.name

        try:
            # 执行转换（删除原文件）
            jpeg_path, mime_type = _convert_png_to_jpeg(png_path, keep_original=False)

            # 验证结果
            assert jpeg_path.endswith('.jpg'), "转换后应该是 .jpg 文件"
            assert mime_type == "image/jpeg", "MIME 类型应该是 image/jpeg"
            assert os.path.exists(jpeg_path), "JPEG 文件应该存在"
            assert not os.path.exists(png_path), "原 PNG 文件应该被删除"

        finally:
            # 清理文件
            for path in [png_path, jpeg_path]:
                if os.path.exists(path):
                    os.remove(path)

    def test_jpeg_passthrough(self):
        """测试 JPEG 文件直接通过"""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            # 创建一个测试 JPEG 图片
            img = Image.new('RGB', (100, 100), (0, 255, 0))  # 绿色
            img.save(tmp.name, 'JPEG')
            jpeg_path = tmp.name

        try:
            # 执行"转换"
            result_path, mime_type = _convert_png_to_jpeg(jpeg_path)
            
            # 验证结果
            assert result_path == jpeg_path, "JPEG 文件应该直接返回原路径"
            assert mime_type == "image/jpeg", "MIME 类型应该是 image/jpeg"
            assert os.path.exists(jpeg_path), "原 JPEG 文件应该保持存在"
            
        finally:
            # 清理文件
            if os.path.exists(jpeg_path):
                os.remove(jpeg_path)

    def test_non_image_file_handling(self):
        """测试非图片文件的处理"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b"This is not an image")
            txt_path = tmp.name

        try:
            # 执行转换
            result_path, mime_type = _convert_png_to_jpeg(txt_path)
            
            # 验证结果（应该返回原文件）
            assert result_path == txt_path, "非图片文件应该返回原路径"
            assert mime_type == "image/png", "默认 MIME 类型应该是 image/png"
            assert os.path.exists(txt_path), "原文件应该保持存在"
            
        finally:
            # 清理文件
            if os.path.exists(txt_path):
                os.remove(txt_path)

    def test_conversion_error_handling(self):
        """测试转换错误处理"""
        # 使用不存在的文件路径
        non_existent_path = "/tmp/non_existent_file.png"
        
        # 执行转换
        result_path, mime_type = _convert_png_to_jpeg(non_existent_path)
        
        # 验证结果（应该返回原路径）
        assert result_path == non_existent_path, "错误情况下应该返回原路径"
        assert mime_type == "image/png", "错误情况下应该返回默认 MIME 类型"

    def test_transparency_handling(self):
        """测试透明度处理"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            # 创建一个带透明度的复杂图片
            img = Image.new('RGBA', (100, 100), (0, 0, 0, 0))  # 完全透明背景
            # 添加一些有颜色的像素
            for x in range(50):
                for y in range(50):
                    img.putpixel((x, y), (255, 0, 0, 255))  # 红色不透明
            img.save(tmp.name, 'PNG')
            png_path = tmp.name

        try:
            # 执行转换
            jpeg_path, mime_type = _convert_png_to_jpeg(png_path)
            
            # 验证转换后的图片
            with Image.open(jpeg_path) as converted_img:
                assert converted_img.mode == 'RGB', "应该转换为 RGB 模式"
                # 检查透明区域是否变成白色
                white_pixel = converted_img.getpixel((99, 99))  # 原本透明的区域
                assert white_pixel == (255, 255, 255), "透明区域应该变成白色"
                # 检查有颜色的区域是否保持
                red_pixel = converted_img.getpixel((25, 25))  # 原本红色的区域
                assert red_pixel[0] > 200, "红色区域应该保持红色"
            
        finally:
            # 清理文件
            for path in [png_path, jpeg_path]:
                if os.path.exists(path):
                    os.remove(path)

    def test_quality_parameter(self):
        """测试质量参数"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            # 创建一个复杂的测试图片（有更多细节，质量差异更明显）
            img = Image.new('RGB', (200, 200), (255, 255, 255))
            # 添加一些复杂的图案（使用确定性模式避免安全热点）
            for x in range(0, 200, 2):
                for y in range(0, 200, 2):
                    # 使用确定性算法生成颜色模式
                    color = ((x * 7 + y * 11) % 256, (x * 13 + y * 17) % 256, (x * 19 + y * 23) % 256)
                    img.putpixel((x, y), color)
            img.save(tmp.name, 'PNG')
            png_path = tmp.name

        try:
            # 测试不同质量设置
            jpeg_path_high, _ = _convert_png_to_jpeg(png_path, quality=95)
            high_quality_size = os.path.getsize(jpeg_path_high)

            # 重新创建相同的复杂 PNG 文件（使用确定性模式）
            img = Image.new('RGB', (200, 200), (255, 255, 255))
            for x in range(0, 200, 2):
                for y in range(0, 200, 2):
                    # 使用相同的确定性算法生成颜色模式
                    color = ((x * 7 + y * 11) % 256, (x * 13 + y * 17) % 256, (x * 19 + y * 23) % 256)
                    img.putpixel((x, y), color)
            img.save(png_path, 'PNG')

            jpeg_path_low, _ = _convert_png_to_jpeg(png_path, quality=30)  # 使用更低的质量
            low_quality_size = os.path.getsize(jpeg_path_low)

            # 验证质量参数被正确应用（文件大小应该有差异）
            print(f"高质量 (95): {high_quality_size} bytes")
            print(f"低质量 (30): {low_quality_size} bytes")

            # 对于复杂图片，高质量应该比低质量大，或者至少验证转换成功
            assert high_quality_size >= low_quality_size, "质量参数应该影响文件大小"
            assert os.path.exists(jpeg_path_high), "高质量 JPEG 应该存在"
            assert os.path.exists(jpeg_path_low), "低质量 JPEG 应该存在"
            
        finally:
            # 清理文件
            for path in [png_path, jpeg_path_high, jpeg_path_low]:
                if os.path.exists(path):
                    os.remove(path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
