"""
Lighting System Tests - 光照系统测试
验证光照计算和渲染功能
"""

import sys
from pathlib import Path
import numpy as np

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import logging
from graphics.lighting import LightingSystem, LightType, Light, Material, LightingPresets


def test_lighting_system_initialization():
    """测试光照系统初始化"""
    print("🧪 测试光照系统初始化...")
    try:
        lighting = LightingSystem()
        assert lighting is not None, "光照系统创建失败"
        assert len(lighting.lights) == 0, "初始光源数量不为0"
        print("   ✅ 光照系统初始化测试通过")
        return True
    except Exception as e:
        print(f"   ❌ 光照系统初始化测试失败: {e}")
        return False


def test_light_creation():
    """测试光源创建"""
    print("🧪 测试光源创建...")
    try:
        lighting = LightingSystem()
        
        # 测试方向光创建
        directional_light = lighting.create_directional_light(
            direction=np.array([0, -1, 0]),
            color=(255, 255, 255),
            intensity=1.0
        )
        assert directional_light is not None, "方向光创建失败"
        assert directional_light.light_type == LightType.DIRECTIONAL, "光源类型错误"
        assert len(lighting.lights) == 1, "光源数量不正确"
        
        # 测试点光源创建
        point_light = lighting.create_point_light(
            position=np.array([0, 0, 0]),
            color=(255, 100, 100),
            intensity=1.5
        )
        assert point_light is not None, "点光源创建失败"
        assert point_light.light_type == LightType.POINT, "光源类型错误"
        assert len(lighting.lights) == 2, "光源数量不正确"
        
        # 测试聚光灯创建
        spot_light = lighting.create_spot_light(
            position=np.array([1, 2, 3]),
            direction=np.array([0, -1, 0]),
            color=(100, 255, 100),
            intensity=1.2,
            angle=45.0
        )
        assert spot_light is not None, "聚光灯创建失败"
        assert spot_light.light_type == LightType.SPOT, "光源类型错误"
        assert len(lighting.lights) == 3, "光源数量不正确"
        
        print("   ✅ 光源创建测试通过")
        return True
    except Exception as e:
        print(f"   ❌ 光源创建测试失败: {e}")
        return False


def test_lighting_calculation():
    """测试光照计算"""
    print("🧪 测试光照计算...")
    try:
        lighting = LightingSystem()
        
        # 创建测试光源
        lighting.create_directional_light(
            direction=np.array([0, -1, 0]),
            color=(255, 255, 255),
            intensity=1.0
        )
        
        # 测试点和法线
        test_point = np.array([0, 0, 0])
        test_normal = np.array([0, 1, 0])
        test_material = Material(
            ambient=(0.1, 0.1, 0.1),
            diffuse=(0.8, 0.8, 0.8),
            specular=(0.5, 0.5, 0.5),
            shininess=32.0
        )
        
        # 计算光照
        color = lighting.calculate_lighting(test_point, test_normal, test_material)
        
        assert isinstance(color, tuple), "返回颜色类型错误"
        assert len(color) == 3, "颜色分量数量错误"
        assert all(0 <= c <= 255 for c in color), "颜色值超出范围"
        
        print(f"   ✅ 光照计算测试通过，计算颜色: {color}")
        return True
    except Exception as e:
        print(f"   ❌ 光照计算测试失败: {e}")
        return False


def test_lighting_presets():
    """测试光照预设"""
    print("🧪 测试光照预设...")
    try:
        lighting = LightingSystem()
        
        # 测试晴天预设
        LightingPresets.sunny_day(lighting)
        sunny_lights = len(lighting.lights)
        assert sunny_lights > 0, "晴天预设光源数量为0"
        print(f"   ✅ 晴天预设: {sunny_lights}个光源")
        
        # 测试室内预设
        LightingPresets.indoor(lighting)
        indoor_lights = len(lighting.lights)
        assert indoor_lights > 0, "室内预设光源数量为0"
        print(f"   ✅ 室内预设: {indoor_lights}个光源")
        
        # 测试戏剧性预设
        LightingPresets.dramatic(lighting)
        dramatic_lights = len(lighting.lights)
        assert dramatic_lights > 0, "戏剧性预设光源数量为0"
        print(f"   ✅ 戏剧性预设: {dramatic_lights}个光源")
        
        print("   ✅ 光照预设测试通过")
        return True
    except Exception as e:
        print(f"   ❌ 光照预设测试失败: {e}")
        return False


def test_material_properties():
    """测试材质属性"""
    print("🧪 测试材质属性...")
    try:
        # 测试默认材质
        default_mat = Material()
        assert default_mat.ambient == (0.1, 0.1, 0.1), "默认环境光错误"
        assert default_mat.diffuse == (0.8, 0.8, 0.8), "默认漫反射错误"
        assert default_mat.specular == (0.5, 0.5, 0.5), "默认镜面反射错误"
        assert default_mat.shininess == 32.0, "默认高光系数错误"
        
        # 测试自定义材质
        custom_mat = Material(
            ambient=(0.2, 0.2, 0.2),
            diffuse=(0.6, 0.7, 0.8),
            specular=(0.9, 0.9, 0.9),
            shininess=64.0
        )
        assert custom_mat.ambient == (0.2, 0.2, 0.2), "自定义环境光错误"
        assert custom_mat.diffuse == (0.6, 0.7, 0.8), "自定义漫反射错误"
        assert custom_mat.specular == (0.9, 0.9, 0.9), "自定义镜面反射错误"
        assert custom_mat.shininess == 64.0, "自定义高光系数错误"
        
        print("   ✅ 材质属性测试通过")
        return True
    except Exception as e:
        print(f"   ❌ 材质属性测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("SceneWeaver 光照系统测试")
    print("=" * 60)
    print()
    
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    tests = [
        test_lighting_system_initialization,
        test_light_creation,
        test_lighting_calculation,
        test_lighting_presets,
        test_material_properties
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
        print("🎉 所有光照系统测试通过！")
        print("\n下一步建议:")
        print("1. 运行完整演示查看光照效果")
        print("2. 测试不同的光照预设")
        print("3. 集成到主渲染系统中")
    else:
        print("⚠️  部分测试失败，请检查相关组件。")


if __name__ == "__main__":
    main()