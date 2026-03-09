#!/usr/bin/env python3
"""
Simple Demo - 简化演示程序
展示SceneWeaver的基本功能，适配当前环境
"""

import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

import logging
import time
from utils.logger import setup_logger
from utils.config_manager import ConfigManager
from core.engine import CoreEngine


def main():
    """主函数"""
    print("🚀 启动SceneWeaver简化演示...")
    print("环境信息:")
    print(f"  Python版本: {sys.version}")
    print(f"  平台: {sys.platform}")
    print()
    
    # 设置日志
    setup_logger({'console_output': True}, logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # 加载配置
        config_manager = ConfigManager("config.yaml")
        config = config_manager.get_config()
        
        # 修改配置为小窗口便于演示
        config['graphics']['width'] = 800
        config['graphics']['height'] = 600
        config['graphics']['fullscreen'] = False
        
        logger.info("配置加载完成")
        
        # 创建引擎
        logger.info("初始化核心引擎...")
        engine = CoreEngine(config)
        
        # 初始化渲染器（关键修复：避免屏幕未初始化警告）
        if not engine.renderer.initialize():
            logger.warning("渲染器初始化失败，将在无窗口模式下运行")
        
        # 运行10秒演示
        logger.info("开始10秒演示...")
        start_time = time.time()
        
        # 简化的运行循环
        while time.time() - start_time < 10:
            engine.handle_events()
            engine.handle_input()
            engine.update(1/60)
            engine.render()
            
            # 显示进度
            elapsed = time.time() - start_time
            progress = (elapsed / 10) * 100
            print(f"\r演示进度: {progress:.1f}%", end="", flush=True)
            
            time.sleep(1/60)  # 60FPS
        
        print("\n✅ 演示完成！")
        logger.info("演示成功结束")
        
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        logger.error(f"程序运行出错: {e}")
        raise
    finally:
        print("🔚 SceneWeaver演示已退出")


if __name__ == "__main__":
    main()