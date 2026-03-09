#!/usr/bin/env python3
"""
Simple Demo - 简单演示程序
展示SceneWeaver的基本功能
"""

import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import logging
from core.engine import CoreEngine
from utils.config_manager import ConfigManager
from utils.logger import setup_logger


def main():
    """主函数"""
    # 设置日志
    setup_logger({'console_output': True}, logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 启动SceneWeaver简单演示...")
    
    try:
        # 加载配置
        config_manager = ConfigManager("../config.yaml")
        config = config_manager.get_config()
        
        # 修改配置为小窗口便于演示
        config['graphics']['width'] = 800
        config['graphics']['height'] = 600
        
        # 创建引擎
        engine = CoreEngine(config)
        
        # 运行引擎
        engine.run()
        
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        raise


if __name__ == "__main__":
    main()