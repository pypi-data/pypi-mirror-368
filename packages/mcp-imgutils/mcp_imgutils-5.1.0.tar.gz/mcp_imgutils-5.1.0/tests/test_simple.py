"""
简单测试 - 用于诊断pytest问题
"""

def test_simple():
    """最简单的测试"""
    assert 1 + 1 == 2

def test_imports_basic():
    """测试基础导入"""
    import os
    import sys
    assert sys.version_info.major >= 3
    assert os.path.exists('.')
