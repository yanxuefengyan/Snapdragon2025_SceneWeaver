#!/usr/bin/env python3
"""
File Input Demo - 文件输入功能演示
展示SceneWeaver的文件选择和处理功能
"""

import sys
import os
import logging
from pathlib import Path

# 添加src目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from input.file_input import FileInputSystem, FileType
from utils.logger import setup_logger


def demo_file_selection():
    """演示文件选择功能"""
    print("=== 文件选择功能演示 ===")
    
    # 初始化文件输入系统
    config = {
        'max_recent_files': 5
    }
    file_input = FileInputSystem(config)
    
    print("1. 单文件选择演示")
    print("   将弹出文件选择对话框...")
    
    # 选择图像文件
    image_file = file_input.select_file(FileType.IMAGE, "选择图像文件")
    if image_file:
        print(f"   ✓ 选择了图像文件: {image_file.name}")
        print(f"   文件大小: {image_file.size} bytes")
        print(f"   文件类型: {image_file.type.value}")
    else:
        print("   ✗ 未选择图像文件")
    
    print("\n2. 多文件选择演示")
    print("   将弹出多文件选择对话框...")
    
    # 选择多个配置文件
    config_files = file_input.select_multiple_files(FileType.CONFIG, "选择配置文件")
    if config_files:
        print(f"   ✓ 选择了 {len(config_files)} 个配置文件:")
        for file_info in config_files:
            print(f"     - {file_info.name}")
    else:
        print("   ✗ 未选择配置文件")
    
    print("\n3. 目录选择演示")
    print("   将弹出目录选择对话框...")
    
    # 选择目录
    directory = file_input.select_directory("选择工作目录")
    if directory:
        print(f"   ✓ 选择了目录: {directory}")
    else:
        print("   ✗ 未选择目录")


def demo_file_processing():
    """演示文件处理功能"""
    print("\n=== 文件处理功能演示 ===")
    
    # 初始化文件输入系统
    config = {
        'max_recent_files': 5
    }
    file_input = FileInputSystem(config)
    
    # 添加处理回调
    def on_file_processed(data):
        file_info = data['file_info']
        result = data['result']
        print(f"   处理文件: {file_info.name}")
        print(f"   状态: {result['status']}")
        if 'message' in result:
            print(f"   消息: {result['message']}")
        if 'metadata' in result:
            print(f"   元数据: {result['metadata']}")
    
    file_input.add_callback('file_processed', on_file_processed)
    
    print("1. 文本文件处理演示")
    text_file = file_input.select_file(FileType.TEXT, "选择文本文件进行处理")
    if text_file:
        result = file_input.process_file(text_file)
        print(f"   处理结果: {result['status']}")
    
    print("\n2. 配置文件处理演示")
    config_file = file_input.select_file(FileType.CONFIG, "选择配置文件进行处理")
    if config_file:
        result = file_input.process_file(config_file)
        print(f"   处理结果: {result['status']}")


def demo_recent_files():
    """演示最近文件功能"""
    print("\n=== 最近文件功能演示 ===")
    
    # 初始化文件输入系统
    config = {
        'max_recent_files': 3
    }
    file_input = FileInputSystem(config)
    
    print("选择几个文件来填充最近文件列表...")
    
    # 选择一些文件
    files_to_select = [
        (FileType.IMAGE, "选择测试图像"),
        (FileType.CONFIG, "选择测试配置"),
        (FileType.TEXT, "选择测试文本")
    ]
    
    for file_type, title in files_to_select:
        file_info = file_input.select_file(file_type, title)
        if file_info:
            file_input.process_file(file_info)
    
    # 显示最近文件
    recent_files = file_input.get_recent_files()
    print(f"\n最近使用的 {len(recent_files)} 个文件:")
    for i, file_info in enumerate(recent_files, 1):
        print(f"  {i}. {file_info.name} ({file_info.type.value})")
    
    # 清空最近文件
    print("\n清空最近文件列表...")
    file_input.clear_recent_files()
    recent_files = file_input.get_recent_files()
    print(f"清空后最近文件数量: {len(recent_files)}")


def demo_file_types():
    """演示不同文件类型的支持"""
    print("\n=== 文件类型支持演示 ===")
    
    file_types = [
        (FileType.IMAGE, "图像文件", [".png", ".jpg", ".jpeg"]),
        (FileType.VIDEO, "视频文件", [".mp4", ".avi"]),
        (FileType.AUDIO, "音频文件", [".mp3", ".wav"]),
        (FileType.MODEL, "模型文件", [".pt", ".onnx"]),
        (FileType.CONFIG, "配置文件", [".yaml", ".json"]),
        (FileType.TEXT, "文本文件", [".txt", ".md"])
    ]
    
    print("支持的文件类型:")
    for file_type, description, extensions in file_types:
        ext_str = ", ".join(extensions)
        print(f"  {file_type.value:8} - {description:10} ({ext_str})")


def main():
    """主函数"""
    print("🚀 SceneWeaver 文件输入功能演示")
    print("=" * 50)
    
    # 设置日志
    setup_logger({'console_output': True}, logging.INFO)
    
    try:
        # 演示各个功能
        demo_file_types()
        demo_file_selection()
        demo_file_processing()
        demo_recent_files()
        
        print("\n🎉 文件输入功能演示完成!")
        print("\n主要特性:")
        print("• 支持多种文件类型选择")
        print("• 提供文件处理和元数据提取")
        print("• 维护最近文件历史记录")
        print("• 支持单文件和多文件选择")
        print("• 集成到GUI系统中")
        
    except KeyboardInterrupt:
        print("\n\n👋 用户中断演示")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()