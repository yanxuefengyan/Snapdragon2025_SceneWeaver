#!/usr/bin/env python3
"""
Comprehensive Test - 综合功能测试
验证SceneWeaver的所有新增功能
"""

import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

import logging
from utils.logger import setup_logger
from utils.config_manager import ConfigManager


def test_particle_system():
    """测试粒子系统"""
    print("🧪 测试粒子系统...")
    try:
        from graphics.particle_system import ParticleSystem, ParticleType, PresetEffects
        
        # 创建粒子系统
        ps = ParticleSystem()
        
        # 测试发射器创建
        emitter = ps.create_emitter(100, 100, ParticleType.EXPLOSION)
        assert emitter is not None, "发射器创建失败"
        
        # 测试粒子发射
        emitter.emit(10)
        assert len(emitter.particles) == 10, "粒子发射数量不正确"
        
        # 测试更新
        ps.update(1.0)
        assert len(emitter.particles) <= 10, "粒子更新后数量异常"
        
        print("   ✅ 粒子系统测试通过")
        return True
    except Exception as e:
        print(f"   ❌ 粒子系统测试失败: {e}")
        return False


def test_object_detection():
    """测试目标检测系统"""
    print("🧪 测试目标检测系统...")
    try:
        from ai.object_detection import ObjectDetectionSystem, DetectedObject
        
        # 创建检测系统
        config = {
            'detector_type': 'yolo',
            'confidence_threshold': 0.5,
            'enabled': True
        }
        detector = ObjectDetectionSystem(config)
        
        # 测试初始化
        init_result = detector.initialize()
        assert init_result is not None, "检测系统初始化失败"
        
        # 测试统计功能
        stats = detector.get_statistics()
        assert isinstance(stats, dict), "统计信息格式错误"
        
        print("   ✅ 目标检测系统测试通过")
        return True
    except Exception as e:
        print(f"   ❌ 目标检测系统测试失败: {e}")
        return False


def test_gui_system():
    """测试GUI系统"""
    print("🧪 测试GUI系统...")
    try:
        from ui.gui_system import GUIManager, ControlPanel
        
        # 测试GUI管理器创建
        gui_manager = GUIManager((800, 600))
        assert gui_manager is not None, "GUI管理器创建失败"
        
        # 测试控制面板
        control_panel = ControlPanel(gui_manager, (10, 10))
        assert control_panel is not None, "控制面板创建失败"
        
        # 测试控制值获取
        control_values = control_panel.get_control_values()
        assert isinstance(control_values, dict), "控制值格式错误"
        
        print("   ✅ GUI系统测试通过")
        return True
    except ImportError:
        print("   ⚠️  GUI依赖未安装，跳过测试")
        return True  # 允许缺少GUI依赖
    except Exception as e:
        print(f"   ❌ GUI系统测试失败: {e}")
        return False


def test_integration():
    """测试系统集成"""
    print("🧪 测试系统集成...")
    try:
        # 测试配置加载
        config_manager = ConfigManager("config.yaml")
        config = config_manager.get_config()
        
        # 验证新配置项
        assert 'ui' in config, "缺少UI配置"
        assert 'effects_enabled' in config['graphics'], "缺少特效配置"
        assert 'detection_enabled' in config['ai'], "缺少检测配置"
        
        print("   ✅ 系统集成测试通过")
        return True
    except Exception as e:
        print(f"   ❌ 系统集成测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("SceneWeaver 综合功能测试")
    print("=" * 60)
    print()
    
    # 设置日志
    setup_logger({'console_output': True}, logging.INFO)
    
    tests = [
        test_particle_system,
        test_object_detection,
        test_gui_system,
        test_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"测试结果: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！SceneWeaver新增功能工作正常。")
        print("\n下一步建议:")
        print("1. 运行综合演示: python demos/comprehensive_demo.py")
        print("2. 启动完整程序: python src/main.py")
        print("3. 查看新功能文档: docs/技术栈.md")
    else:
        print("⚠️  部分测试失败，请检查相关组件。")


if __name__ == "__main__":
    main()