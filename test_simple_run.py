#!/usr/bin/env python3
"""
简化版主程序 - 用于测试和调试
"""

import sys
import os
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """主函数"""
    print("=" * 60)
    print("SceneWeaver 测试程序")
    print("=" * 60)
    
    # 简单配置
    config = {
        'graphics': {
            'width': 1280,
            'height': 720,
            'fullscreen': False,
            'effects_enabled': True,
            'lighting_enabled': True,
            'show_fps': True
        },
        'ui': {
            'enabled': False  # 暂时禁用 UI 以简化测试
        }
    }
    
    print("\n1. 导入核心引擎...")
    try:
        from core.engine import CoreEngine
        print("   ✓ CoreEngine 导入成功")
    except Exception as e:
        print(f"   ✗ CoreEngine 导入失败：{e}")
        return
    
    print("\n2. 初始化引擎...")
    try:
        engine = CoreEngine(config)
        print("   ✓ 引擎初始化成功")
    except Exception as e:
        print(f"   ✗ 引擎初始化失败：{e}")
        return
    
    print("\n3. 启动引擎...")
    print("   提示：按 ESC 键退出，按 1-5 键触发特效，点击鼠标左键触发火花效果")
    try:
        engine.run()
        print("   ✓ 引擎运行正常")
    except KeyboardInterrupt:
        print("   ✓ 用户中断")
    except Exception as e:
        print(f"   ✗ 引擎运行失败：{e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
