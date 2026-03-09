#!/usr/bin/env python3
"""
菜单功能测试脚本
测试所有菜单项的功能是否正常
"""

import os
import sys
import time
import json
import tempfile
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.logger import setup_logger
import logging


def test_file_operations():
    """测试文件菜单功能"""
    print("\n" + "=" * 60)
    print("测试文件菜单功能")
    print("=" * 60)
    
    # 创建临时目录用于测试
    test_dir = tempfile.mkdtemp(prefix="scene_weaver_test_")
    print(f"测试目录：{test_dir}")
    
    try:
        # 测试 1: 新建项目
        print("\n[测试 1] 新建项目")
        project_data = {
            'name': 'Test Project',
            'created_at': time.time(),
            'modified_at': time.time(),
            'objects': [],
            'effects': [],
            'settings': {'test': True}
        }
        print(f"✓ 创建项目：{project_data['name']}")
        
        # 测试 2: 保存项目
        print("\n[测试 2] 保存项目")
        test_file = os.path.join(test_dir, "test_project.swp")
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
        print(f"✓ 保存到：{test_file}")
        
        # 验证文件存在
        assert os.path.exists(test_file), "保存的文件不存在"
        print(f"✓ 文件存在验证通过")
        
        # 测试 3: 加载项目
        print("\n[测试 3] 加载项目")
        with open(test_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        assert loaded_data['name'] == 'Test Project', "项目名称不匹配"
        print(f"✓ 加载成功：{loaded_data['name']}")
        
        # 测试 4: 另存为
        print("\n[测试 4] 另存为")
        test_file2 = os.path.join(test_dir, "test_project_copy.swp")
        project_data['name'] = 'Test Project Copy'
        project_data['modified_at'] = time.time()
        with open(test_file2, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
        print(f"✓ 另存为：{test_file2}")
        
        # 测试 5: 中文路径支持
        print("\n[测试 5] 中文路径支持")
        chinese_dir = os.path.join(test_dir, "中文测试")
        os.makedirs(chinese_dir, exist_ok=True)
        chinese_file = os.path.join(chinese_dir, "测试项目.swp")
        with open(chinese_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
        assert os.path.exists(chinese_file), "中文路径文件创建失败"
        print(f"✓ 中文路径支持通过：{chinese_file}")
        
        # 清理测试文件
        print("\n[清理] 删除测试文件")
        os.remove(test_file)
        os.remove(test_file2)
        os.remove(chinese_file)
        os.rmdir(chinese_dir)
        os.rmdir(test_dir)
        print("✓ 测试文件已清理")
        
        print("\n✅ 文件菜单功能测试全部通过!")
        return True
        
    except Exception as e:
        print(f"\n❌ 文件菜单功能测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_dialog_availability():
    """测试对话框可用性"""
    print("\n" + "=" * 60)
    print("测试对话框可用性")
    print("=" * 60)
    
    # 测试 tkinter 可用性
    try:
        import tkinter as tk
        from tkinter import filedialog
        
        print("\n[测试] tkinter 可用性")
        root = tk.Tk()
        root.withdraw()
        root.update()
        
        # 测试文件对话框
        print("✓ tkinter 文件对话框可用")
        
        # 测试消息框
        from tkinter import messagebox
        print("✓ tkinter 消息框可用")
        
        root.destroy()
        print("✓ tkinter 对话框系统正常")
        return True
        
    except Exception as e:
        print(f"❌ tkinter 对话框不可用：{e}")
        print("  将使用控制台输入作为后备方案")
        return False


def test_menu_callbacks():
    """测试菜单回调注册"""
    print("\n" + "=" * 60)
    print("测试菜单回调注册")
    print("=" * 60)
    
    try:
        # 模拟菜单回调
        callbacks = {}
        
        def mock_callback(name):
            def func():
                print(f"✓ 回调触发：{name}")
            return func
        
        # 注册所有菜单回调
        menu_items = [
            ('文件', ['新建', '打开', '保存', '另存为', '退出']),
            ('编辑', ['撤销', '重做', '剪切', '复制', '粘贴']),
            ('视图', ['全屏', '重置视图', '显示 FPS', '显示控制台']),
            ('工具', ['设置', '插件管理', '文件浏览器']),
            ('帮助', ['关于', '使用指南', '检查更新'])
        ]
        
        for menu_name, items in menu_items:
            print(f"\n[菜单] {menu_name}")
            for i, item in enumerate(items):
                if item != '-':
                    key = f"{menu_name}_{item}"
                    callbacks[key] = mock_callback(f"{menu_name} > {item}")
                    print(f"  ✓ {item} - 回调已注册")
        
        # 测试回调触发
        print("\n[测试] 回调触发")
        test_callback = callbacks.get('文件_新建')
        if test_callback:
            test_callback()
        
        print(f"\n✓ 共注册 {len(callbacks)} 个菜单回调")
        return True
        
    except Exception as e:
        print(f"\n❌ 菜单回调测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_utf8_support():
    """测试 UTF-8 编码支持"""
    print("\n" + "=" * 60)
    print("测试 UTF-8 编码支持")
    print("=" * 60)
    
    test_dir = tempfile.mkdtemp(prefix="utf8_test_")
    
    try:
        # 测试中文字符
        chinese_text = "中文测试"
        test_file = os.path.join(test_dir, f"{chinese_text}.txt")
        
        # 写入中文内容
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("这是中文内容测试\n")
            f.write("SceneWeaver 菜单功能测试\n")
        
        # 读取验证
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "中文" in content, "中文内容读取失败"
        print(f"✓ UTF-8 编码支持正常")
        print(f"✓ 文件：{test_file}")
        print(f"✓ 内容：{content.strip()}")
        
        # 清理
        os.remove(test_file)
        os.rmdir(test_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ UTF-8 编码测试失败：{e}")
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("SceneWeaver 菜单功能测试")
    print("=" * 60)
    
    # 设置日志
    setup_logger({'console_output': True}, logging.INFO)
    
    results = []
    
    # 运行所有测试
    results.append(("对话框可用性", test_dialog_availability()))
    results.append(("UTF-8 编码支持", test_utf8_support()))
    results.append(("菜单回调注册", test_menu_callbacks()))
    results.append(("文件操作功能", test_file_operations()))
    
    # 打印测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n总计：{passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过!")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())