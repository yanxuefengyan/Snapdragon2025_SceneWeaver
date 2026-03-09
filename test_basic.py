#!/usr/bin/env python3
"""
Basic Test - 基础功能测试
验证SceneWeaver核心组件是否正常工作
"""

import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

import logging
from utils.logger import setup_logger
from utils.config_manager import ConfigManager
from utils.performance_monitor import PerformanceMonitor


def test_config_manager():
    """测试配置管理器"""
    print("🧪 测试配置管理器...")
    try:
        config_manager = ConfigManager("config.yaml")
        config = config_manager.get_config()
        
        # 测试配置获取
        graphics_width = config_manager.get('graphics.width', 1280)
        ai_device = config_manager.get('ai.device', 'auto')
        
        print(f"   ✓ 图形宽度: {graphics_width}")
        print(f"   ✓ AI设备: {ai_device}")
        print("   ✅ 配置管理器测试通过")
        return True
    except Exception as e:
        print(f"   ❌ 配置管理器测试失败: {e}")
        return False


def test_logger():
    """测试日志系统"""
    print("🧪 测试日志系统...")
    try:
        setup_logger({'console_output': True}, logging.INFO)
        logger = logging.getLogger(__name__)
        
        logger.info("这是一个测试日志消息")
        logger.warning("这是一个警告消息")
        logger.error("这是一个错误消息")
        
        print("   ✅ 日志系统测试通过")
        return True
    except Exception as e:
        print(f"   ❌ 日志系统测试失败: {e}")
        return False


def test_performance_monitor():
    """测试性能监控器"""
    print("🧪 测试性能监控器...")
    try:
        perf_monitor = PerformanceMonitor({'enable_profiling': True})
        
        # 模拟一些性能数据
        import time
        for i in range(10):
            start_time = time.time()
            time.sleep(0.01)  # 模拟10ms的工作
            frame_time = time.time() - start_time
            perf_monitor.update(frame_time)
        
        metrics = perf_monitor.get_current_metrics()
        print(f"   ✓ 当前FPS: {metrics.fps:.2f}")
        print(f"   ✓ 当前帧时间: {metrics.frame_time*1000:.2f}ms")
        print("   ✅ 性能监控器测试通过")
        return True
    except Exception as e:
        print(f"   ❌ 性能监控器测试失败: {e}")
        return False


def test_imports():
    """测试模块导入"""
    print("🧪 测试模块导入...")
    try:
        # 测试核心模块导入
        from core.engine import CoreEngine
        from graphics.renderer import Renderer
        from ai.ai_system import AISystem
        from input.input_handler import InputHandler
        
        print("   ✓ 核心引擎模块导入成功")
        print("   ✓ 图形渲染模块导入成功")
        print("   ✓ AI系统模块导入成功")
        print("   ✓ 输入处理模块导入成功")
        print("   ✅ 模块导入测试通过")
        return True
    except Exception as e:
        print(f"   ❌ 模块导入测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 50)
    print("SceneWeaver 基础功能测试")
    print("=" * 50)
    print()
    
    tests = [
        test_imports,
        test_config_manager,
        test_logger,
        test_performance_monitor
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"测试结果: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有基础测试通过！SceneWeaver核心组件工作正常。")
        print("\n下一步建议:")
        print("1. 运行完整示例: python examples/simple_demo.py")
        print("2. 查看开发文档: docs/development_guide.md")
        print("3. 运行单元测试: python -m pytest tests/")
    else:
        print("⚠️  部分测试失败，请检查相关组件。")


if __name__ == "__main__":
    main()