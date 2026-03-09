"""
Android Main Entry - Android平台主入口
SceneWeaver Android平台的主程序入口点
"""

import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.logger import setup_logger
from utils.config_manager import ConfigManager
from core.engine import CoreEngine
from platform.android import AndroidPlatform, create_android_platform
from platform.android.touch_input import AndroidTouchHandler
from platform.android.renderer_adapter import AndroidRendererAdapter


class AndroidSceneWeaver:
    """Android平台SceneWeaver主类"""
    
    def __init__(self):
        self.logger = None
        self.config_manager = None
        self.android_platform = None
        self.touch_handler = None
        self.renderer_adapter = None
        self.core_engine = None
        
    def initialize(self) -> bool:
        """初始化Android平台应用"""
        try:
            # 设置日志系统
            self._setup_logging()
            
            # 加载配置
            if not self._load_configuration():
                return False
            
            # 初始化Android平台
            if not self._init_android_platform():
                return False
            
            # 初始化触摸输入
            if not self._init_touch_input():
                return False
            
            # 初始化渲染适配器
            if not self._init_renderer_adapter():
                return False
            
            # 初始化核心引擎
            if not self._init_core_engine():
                return False
            
            self.logger.info("Android SceneWeaver初始化成功")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Android应用初始化失败: {e}")
            else:
                print(f"Android应用初始化失败: {e}")
            return False
    
    def _setup_logging(self):
        """设置日志系统"""
        log_config = {
            'console_output': True,
            'log_to_file': True,
            'log_file': '/sdcard/SceneWeaver/android.log',  # Android存储路径
            'max_file_size': '5MB',
            'backup_count': 3
        }
        
        setup_logger(log_config, logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Android日志系统初始化完成")
    
    def _load_configuration(self) -> bool:
        """加载Android特定配置"""
        try:
            # 尝试加载Android配置文件
            config_path = 'config_android.yaml'
            if not os.path.exists(config_path):
                config_path = 'config.yaml'  # 使用默认配置
            
            self.config_manager = ConfigManager(config_path)
            self.config = self.config_manager.get_config()
            
            # 应用Android特定的默认配置
            self._apply_android_defaults()
            
            self.logger.info(f"配置加载成功: {config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"配置加载失败: {e}")
            return False
    
    def _apply_android_defaults(self):
        """应用Android平台默认配置"""
        # 图形设置
        graphics_config = self.config.setdefault('graphics', {})
        graphics_config.setdefault('width', 1080)
        graphics_config.setdefault('height', 1920)
        graphics_config.setdefault('fullscreen', True)
        graphics_config.setdefault('vsync', True)
        graphics_config.setdefault('effects_quality', 'balanced')
        
        # 输入设置
        input_config = self.config.setdefault('input', {})
        input_config.setdefault('touch_sensitivity', 1.0)
        input_config.setdefault('gesture_recognition', True)
        
        # 性能设置
        perf_config = self.config.setdefault('performance', {})
        perf_config.setdefault('target_fps', 60)
        perf_config.setdefault('power_save_mode', False)
        perf_config.setdefault('adaptive_quality', True)
        
        # Android特定设置
        android_config = self.config.setdefault('android', {})
        android_config.setdefault('immersive_mode', True)
        android_config.setdefault('keep_screen_on', True)
        android_config.setdefault('orientation', 'sensor')
    
    def _init_android_platform(self) -> bool:
        """初始化Android平台支持"""
        try:
            self.android_platform = create_android_platform(self.config)
            if not self.android_platform:
                self.logger.error("无法创建Android平台实例")
                return False
            
            if not self.android_platform.initialize():
                self.logger.error("Android平台初始化失败")
                return False
            
            # 获取屏幕信息并更新配置
            screen_info = self.android_platform.get_screen_info()
            if screen_info:
                self.config['graphics']['width'] = screen_info.get('width', 1080)
                self.config['graphics']['height'] = screen_info.get('height', 1920)
                self.logger.info(f"屏幕信息: {screen_info}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Android平台初始化失败: {e}")
            return False
    
    def _init_touch_input(self) -> bool:
        """初始化触摸输入处理"""
        try:
            touch_config = self.config.get('input', {})
            self.touch_handler = AndroidTouchHandler(touch_config)
            
            if not self.touch_handler.initialize():
                self.logger.error("触摸输入初始化失败")
                return False
            
            # 注册触摸事件回调
            self._register_touch_callbacks()
            
            self.logger.info("触摸输入系统初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"触摸输入初始化失败: {e}")
            return False
    
    def _register_touch_callbacks(self):
        """注册触摸事件回调"""
        def touch_callback(event_type, touch_point):
            # 将触摸事件转换为标准输入事件
            self._handle_touch_event(event_type, touch_point)
        
        def gesture_callback(gesture):
            # 处理手势事件
            self._handle_gesture_event(gesture)
        
        self.touch_handler.add_touch_callback(touch_callback)
        self.touch_handler.add_gesture_callback(gesture_callback)
    
    def _handle_touch_event(self, event_type, touch_point):
        """处理触摸事件"""
        if self.core_engine and self.core_engine.input_handler:
            # 转换为标准输入事件格式
            standardized_event = {
                'type': event_type.value,
                'x': touch_point.x,
                'y': touch_point.y,
                'pressure': touch_point.pressure,
                'timestamp': touch_point.timestamp
            }
            self.core_engine.input_handler.process_event(standardized_event)
    
    def _handle_gesture_event(self, gesture):
        """处理手势事件"""
        self.logger.info(f"处理手势: {gesture.gesture_type.value}")
        
        # 根据手势类型执行相应操作
        if gesture.gesture_type == 'swipe':
            self._handle_swipe_gesture(gesture)
        elif gesture.gesture_type == 'tap':
            self._handle_tap_gesture(gesture)
        elif gesture.gesture_type == 'double_tap':
            self._handle_double_tap_gesture(gesture)
        elif gesture.gesture_type == 'pinch':
            self._handle_pinch_gesture(gesture)
    
    def _handle_swipe_gesture(self, gesture):
        """处理滑动手势"""
        if len(gesture.points) >= 2:
            dx = gesture.points[-1].x - gesture.points[0].x
            dy = gesture.points[-1].y - gesture.points[0].y
            
            # 根据滑动方向执行操作
            if abs(dx) > abs(dy):
                # 水平滑动
                if dx > 0:
                    self.logger.info("向右滑动")
                else:
                    self.logger.info("向左滑动")
            else:
                # 垂直滑动
                if dy > 0:
                    self.logger.info("向下滑动")
                else:
                    self.logger.info("向上滑动")
    
    def _handle_tap_gesture(self, gesture):
        """处理点击手势"""
        self.logger.info("单击手势")
        # 可以在这里添加点击操作逻辑
    
    def _handle_double_tap_gesture(self, gesture):
        """处理双击手势"""
        self.logger.info("双击手势")
        # 可以在这里添加双击操作逻辑
    
    def _handle_pinch_gesture(self, gesture):
        """处理捏合手势"""
        self.logger.info(f"捏合手势，缩放比例: {gesture.scale}")
        # 可以在这里添加缩放操作逻辑
    
    def _init_renderer_adapter(self) -> bool:
        """初始化渲染适配器"""
        try:
            # 注意：这里需要访问核心引擎的渲染器
            # 由于初始化顺序问题，暂时创建占位符
            self.renderer_adapter = AndroidRendererAdapter(None, self.config)
            
            if not self.renderer_adapter.initialize():
                self.logger.error("渲染适配器初始化失败")
                return False
            
            self.logger.info("渲染适配器初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"渲染适配器初始化失败: {e}")
            return False
    
    def _init_core_engine(self) -> bool:
        """初始化核心引擎"""
        try:
            self.core_engine = CoreEngine(self.config)
            
            if not self.core_engine.initialize():
                self.logger.error("核心引擎初始化失败")
                return False
            
            # 将渲染适配器连接到核心引擎
            if self.renderer_adapter and self.core_engine.renderer:
                self.renderer_adapter.base_renderer = self.core_engine.renderer
            
            self.logger.info("核心引擎初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"核心引擎初始化失败: {e}")
            return False
    
    def run(self):
        """运行Android应用主循环"""
        if not self.initialize():
            self.logger.error("应用初始化失败，无法启动")
            return
        
        try:
            self.logger.info("启动Android SceneWeaver主循环")
            
            # 启动核心引擎主循环
            self.core_engine.run()
            
        except KeyboardInterrupt:
            self.logger.info("收到中断信号，正在退出...")
        except Exception as e:
            self.logger.error(f"应用运行出错: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理应用资源"""
        self.logger.info("开始清理应用资源...")
        
        if self.core_engine:
            self.core_engine.cleanup()
        
        if self.renderer_adapter:
            self.renderer_adapter.cleanup()
        
        if self.touch_handler:
            self.touch_handler.cleanup()
        
        if self.android_platform:
            self.android_platform.cleanup()
        
        self.logger.info("应用资源清理完成")


def main():
    """Android应用主函数"""
    app = AndroidSceneWeaver()
    app.run()


if __name__ == '__main__':
    main()