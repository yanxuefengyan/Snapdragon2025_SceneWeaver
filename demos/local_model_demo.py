#!/usr/bin/env python3
"""
本地模型使用演示
展示如何下载和使用本地AI模型文件
"""

import sys
from pathlib import Path
import time
import logging

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.logger import setup_logger
from utils.config_manager import ConfigManager
from ai.ai_system import AISystem
from download_models import ModelDownloader


def demonstrate_model_download():
    """演示模型下载功能"""
    print("=== 模型下载演示 ===")
    
    downloader = ModelDownloader("models")
    
    # 列出可用模型
    print("1. 可用模型列表:")
    available_models = downloader.list_available_models()
    for model_name in available_models:
        info = downloader.get_model_info(model_name)
        print(f"   - {model_name}: {info['name']} ({info['size']})")
    
    # 检查本地模型
    print("\n2. 检查本地模型状态:")
    for model_name in available_models:
        local_path = downloader.get_local_model_path(model_name)
        if local_path:
            verified = downloader.verify_model(model_name)
            status = "✓ 已下载(校验通过)" if verified else "⚠ 已下载(校验失败)"
            print(f"   {model_name}: {status}")
        else:
            print(f"   {model_name}: ✗ 未下载")
    
    return downloader


def demonstrate_local_model_usage():
    """演示本地模型使用"""
    print("\n=== 本地模型使用演示 ===")
    
    # 设置日志
    setup_logger({'console_output': True}, logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # 加载配置
        config_manager = ConfigManager("config.yaml")
        config = config_manager.get_config()
        
        # 启用本地模型
        config['ai']['use_local_models'] = True
        config['ai']['object_detection']['use_local_model'] = True
        
        print("1. 配置本地模型使用:")
        print(f"   使用本地模型: {config['ai']['use_local_models']}")
        print(f"   本地模型目录: {config['ai']['local_models_dir']}")
        print(f"   目标检测使用本地模型: {config['ai']['object_detection']['use_local_model']}")
        
        # 创建AI系统
        print("\n2. 初始化AI系统:")
        ai_system = AISystem(config)
        
        if ai_system.initialize():
            print("   ✓ AI系统初始化成功")
            
            # 获取模型状态
            model_status = ai_system.get_model_status()
            print(f"   当前设备: {model_status['device']}")
            print(f"   使用本地模型: {model_status['use_local_models']}")
            
            # 模拟图像处理
            print("\n3. 模拟目标检测:")
            import numpy as np
            dummy_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            
            start_time = time.time()
            detections = ai_system.process_frame(dummy_image)
            end_time = time.time()
            
            print(f"   处理时间: {(end_time - start_time)*1000:.2f} ms")
            print(f"   检测到 {len(detections['detections'])} 个目标")
            
            # 显示检测结果
            for detection in detections['detections']:
                print(f"   - {detection.label}: {detection.confidence:.2f}")
            
        else:
            print("   ✗ AI系统初始化失败")
            
    except Exception as e:
        print(f"   ✗ 演示过程中出错: {e}")


def main():
    """主函数"""
    print("🚀 SceneWeaver 本地模型使用演示")
    print("=" * 50)
    
    # 演示模型下载功能
    downloader = demonstrate_model_download()
    
    # 演示本地模型使用
    demonstrate_local_model_usage()
    
    print("\n" + "=" * 50)
    print("💡 使用建议:")
    print("1. 首次使用前运行: python download_models.py download --model yolov5s")
    print("2. 修改 config.yaml 启用本地模型")
    print("3. 运行主程序享受更快的模型加载速度")
    print("\n🎯 完成!")


if __name__ == "__main__":
    main()