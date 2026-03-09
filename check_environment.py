#!/usr/bin/env python3
"""
SceneWeaver 环境检查脚本
检查系统环境和依赖包是否满足项目要求
适用于新的Pygame技术栈
"""

import sys
import platform
import subprocess
import importlib.util
from typing import Dict, List, Tuple


def check_python_version() -> Tuple[bool, str]:
    """检查Python版本"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        return True, f"Python {version.major}.{version.minor}.{version.micro} ✓"
    else:
        return False, f"Python版本过低: {version.major}.{version.minor}.{version.micro} (需要 >= 3.8)"


def check_system_info() -> Dict[str, str]:
    """获取系统信息"""
    return {
        "操作系统": platform.system(),
        "系统版本": platform.release(),
        "处理器架构": platform.machine(),
        "Python实现": platform.python_implementation(),
        "Python编译器": platform.python_compiler()
    }


def check_gpu_support() -> Dict[str, str]:
    """检查GPU支持情况"""
    gpu_info = {}
    
    try:
        # 检查CUDA
        import torch
        if torch.cuda.is_available():
            gpu_info["CUDA支持"] = f"✓ (可用GPU数量: {torch.cuda.device_count()})"
            gpu_info["CUDA版本"] = torch.version.cuda
        else:
            gpu_info["CUDA支持"] = "✗ (不可用)"
    except ImportError:
        gpu_info["CUDA支持"] = "✗ (PyTorch未安装)"
    
    try:
        # 检查TensorFlow GPU支持
        import tensorflow as tf
        gpu_devices = len(tf.config.experimental.list_physical_devices('GPU'))
        if gpu_devices > 0:
            gpu_info["TensorFlow GPU"] = f"✓ (可用设备数: {gpu_devices})"
        else:
            gpu_info["TensorFlow GPU"] = "✗ (无GPU设备)"
    except ImportError:
        gpu_info["TensorFlow GPU"] = "✗ (TensorFlow未安装)"
    
    return gpu_info


def check_required_packages() -> List[Tuple[str, bool, str]]:
    """检查必需的Python包"""
    required_packages = [
        ("numpy", "数值计算库"),
        ("pygame", "游戏开发和图形渲染库"),
        ("PIL", "图像处理库"),
        ("cv2", "OpenCV计算机视觉库"),
        ("torch", "PyTorch深度学习框架"),
        ("tensorflow", "TensorFlow机器学习框架"),
        ("yaml", "YAML配置文件解析"),
        ("tqdm", "进度条工具"),
        ("matplotlib", "绘图库"),
        ("scipy", "科学计算库"),
        ("psutil", "系统监控工具")
    ]
    
    results = []
    for package_name, description in required_packages:
        try:
            spec = importlib.util.find_spec(package_name)
            if spec is not None:
                # 尝试导入并获取版本
                module = importlib.import_module(package_name)
                version = getattr(module, '__version__', '未知版本')
                results.append((f"{package_name} ({description})", True, f"✓ 版本: {version}"))
            else:
                results.append((f"{package_name} ({description})", False, "✗ 未安装"))
        except Exception as e:
            results.append((f"{package_name} ({description})", False, f"✗ 导入失败: {str(e)}"))
    
    return results


def check_pygame_support() -> Tuple[bool, str]:
    """检查Pygame支持"""
    try:
        import pygame
        pygame.init()
        
        # 检查显示支持
        info = pygame.display.Info()
        if info.current_w > 0 and info.current_h > 0:
            return True, f"✓ Pygame版本: {pygame.version.ver}, 显示: {info.current_w}x{info.current_h}"
        else:
            return False, "✗ 无法初始化显示系统"
            
    except Exception as e:
        return False, f"✗ Pygame检查失败: {str(e)}"

def main():
    """主函数"""
    print("=" * 60)
    print("SceneWeaver 环境检查 (Pygame技术栈)")
    print("=" * 60)
    print()
    
    # 检查Python版本
    version_ok, version_msg = check_python_version()
    print(f"Python版本: {version_msg}")
    if not version_ok:
        print("错误: Python版本不符合要求!")
        return
    
    print()
    
    # 显示系统信息
    print("系统信息:")
    system_info = check_system_info()
    for key, value in system_info.items():
        print(f"  {key}: {value}")
    
    print()
    
    # 检查GPU支持
    print("AI计算支持:")
    gpu_info = check_gpu_support()
    for key, value in gpu_info.items():
        print(f"  {key}: {value}")
    
    print()
    
    # 检查Pygame支持
    print("图形支持:")
    pygame_ok, pygame_msg = check_pygame_support()
    print(f"  Pygame: {pygame_msg}")
    
    print()
    
    # 检查依赖包
    print("Python包依赖检查:")
    package_results = check_required_packages()
    installed_count = 0
    total_count = len(package_results)
    
    for package_name, is_installed, status in package_results:
        status_icon = "✓" if is_installed else "✗"
        print(f"  {status_icon} {package_name}: {status}")
        if is_installed:
            installed_count += 1
    
    print()
    print("=" * 60)
    print(f"检查完成: {installed_count}/{total_count} 个包已安装")
    
    if installed_count == total_count and version_ok and pygame_ok:
        print("🎉 环境配置完整，可以开始开发!")
        print("\n推荐的下一步:")
        print("1. 运行基础测试: python test_basic.py")
        print("2. 启动演示程序: python demo_simple.py")
        print("3. 查看开发文档: docs/development_guide.md")
    else:
        print("⚠️  环境配置不完整，请安装缺失的依赖包")
        print("运行命令: pip install -r requirements.txt")

if __name__ == "__main__":
    main()