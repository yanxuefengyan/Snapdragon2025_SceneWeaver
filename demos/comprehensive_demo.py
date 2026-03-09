#!/usr/bin/env python3
"""
Comprehensive Demo - 综合演示程序
展示SceneWeaver的所有新功能：粒子系统、目标检测、图形界面
"""

import sys
from pathlib import Path
import time
import logging

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.logger import setup_logger
from utils.config_manager import ConfigManager
from core.engine import CoreEngine


def setup_demo_config():
    """设置演示配置"""
    # 创建演示专用配置
    demo_config = {
        'graphics': {
            'width': 1280,
            'height': 720,
            'fullscreen': False,
            'vsync': True,
            'effects_enabled': True,
            'movement_speed': 2.5
        },
        'ai': {
            'device': 'auto',
            'model_path': './models',
            'detection_enabled': True,
            'detection': {
                'detector_type': 'yolo',
                'confidence_threshold': 0.5,
                'detection_interval': 1
            }
        },
        'input': {
            'mouse_sensitivity': 0.1,
            'enable_gestures': True
        },
        'performance': {
            'target_fps': 60,
            'enable_profiling': False,
            'sample_window': 1.0
        },
        'ui': {
            'enabled': True
        }
    }
    
    return demo_config


def create_demo_instructions():
    """创建演示说明"""
    instructions = """
    🎮 SceneWeaver 综合演示说明
    
    键盘控制:
    - WASD: 移动摄像机
    - ESC: 退出程序
    - F1: 触发爆炸效果
    - F2: 触发闪光效果
    - F3: 切换粒子效果开关
    
    GUI控制面板功能:
    - FPS滑块: 调整目标帧率
    - 粒子效果开关: 启用/禁用粒子系统
    - 粒子密度: 调整粒子数量
    - 爆炸/闪光按钮: 手动触发动效
    - AI检测开关: 启用/禁用目标检测
    - 置信度滑块: 调整检测敏感度
    
    状态栏显示:
    - 当前FPS
    - 内存使用情况
    - AI系统状态
    
    演示将持续60秒，您可以在此期间体验所有功能。
    """
    
    print(instructions)


def main():
    """主演示函数"""
    print("🚀 启动SceneWeaver综合演示...")
    print(f"Python版本: {sys.version}")
    print(f"平台: {sys.platform}")
    print()
    
    # 显示操作说明
    create_demo_instructions()
    
    # 设置日志
    setup_logger({'console_output': True}, logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # 加载配置
        config = setup_demo_config()
        logger.info("演示配置加载完成")
        
        # 创建引擎
        logger.info("初始化核心引擎...")
        engine = CoreEngine(config)
        
        # 运行60秒演示
        logger.info("开始60秒综合演示...")
        start_time = time.time()
        demo_duration = 60  # 60秒演示
        
        # 简化的运行循环
        while time.time() - start_time < demo_duration:
            engine.handle_events()
            engine.handle_input()
            engine.update(1/60)
            engine.render()
            
            # 显示进度
            elapsed = time.time() - start_time
            progress = (elapsed / demo_duration) * 100
            remaining = demo_duration - elapsed
            
            # 每5秒显示一次状态
            if int(elapsed) % 5 == 0:
                metrics = engine.perf_monitor.get_current_metrics()
                print(f"\r进度: {progress:.1f}% | "
                      f"FPS: {metrics.fps:.1f} | "
                      f"剩余: {remaining:.1f}秒", 
                      end="", flush=True)
            
            time.sleep(1/60)  # 60FPS
        
        print("\n✅ 演示完成！")
        logger.info("综合演示成功结束")
        
        # 显示最终统计
        final_metrics = engine.perf_monitor.get_current_metrics()
        print(f"\n📊 演示统计:")
        print(f"  平均FPS: {final_metrics.fps:.1f}")
        print(f"  平均帧时间: {final_metrics.frame_time*1000:.2f}ms")
        
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        logger.error(f"程序运行出错: {e}")
        raise
    finally:
        print("🔚 SceneWeaver综合演示已退出")


if __name__ == "__main__":
    main()