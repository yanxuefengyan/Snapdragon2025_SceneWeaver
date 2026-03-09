"""
Web Main Entry - Web平台主入口
SceneWeaver Web平台的主程序入口点
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
from platform.web import WebPlatform, create_web_platform
from platform.web.webgl_renderer import WebGLRendererAdapter
from platform.web.input_handler import WebInputHandler


class WebSceneWeaver:
    """Web平台SceneWeaver主类"""
    
    def __init__(self):
        self.logger = None
        self.config_manager = None
        self.web_platform = None
        self.webgl_renderer = None
        self.input_handler = None
        self.core_engine = None
        
        # Web特定组件
        self.canvas = None
        self.window = None
        self.document = None
        
    def initialize(self) -> bool:
        """初始化Web平台应用"""
        try:
            # 设置日志系统
            self._setup_logging()
            
            # 加载配置
            if not self._load_configuration():
                return False
            
            # 初始化Web平台
            if not self._init_web_platform():
                return False
            
            # 初始化WebGL渲染器
            if not self._init_webgl_renderer():
                return False
            
            # 初始化输入处理器
            if not self._init_input_handler():
                return False
            
            # 初始化核心引擎
            if not self._init_core_engine():
                return False
            
            self.logger.info("Web SceneWeaver初始化成功")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Web应用初始化失败: {e}")
            else:
                print(f"Web应用初始化失败: {e}")
            return False
    
    def _setup_logging(self):
        """设置日志系统"""
        try:
            from js import console
            # Web环境使用console输出
            class WebConsoleHandler(logging.Handler):
                def emit(self, record):
                    msg = self.format(record)
                    if record.levelno >= logging.ERROR:
                        console.error(msg)
                    elif record.levelno >= logging.WARNING:
                        console.warn(msg)
                    else:
                        console.log(msg)
            
            # 配置日志
            log_config = {
                'console_output': False,  # 使用自定义handler
                'log_to_file': False,     # Web环境不写文件
            }
            
            setup_logger(log_config, logging.INFO)
            
            # 添加Web控制台handler
            web_handler = WebConsoleHandler()
            web_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            
            root_logger = logging.getLogger()
            root_logger.addHandler(web_handler)
            
            self.logger = logging.getLogger(__name__)
            self.logger.info("Web日志系统初始化完成")
            
        except Exception as e:
            # 降级到基本打印
            print(f"日志初始化失败: {e}")
            self.logger = logging.getLogger(__name__)
    
    def _load_configuration(self) -> bool:
        """加载Web特定配置"""
        try:
            # 尝试加载Web配置文件
            config_path = 'config_web.yaml'
            if not os.path.exists(config_path):
                config_path = 'config.yaml'  # 使用默认配置
            
            self.config_manager = ConfigManager(config_path)
            self.config = self.config_manager.get_config()
            
            # 应用Web特定的默认配置
            self._apply_web_defaults()
            
            self.logger.info(f"配置加载成功: {config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"配置加载失败: {e}")
            return False
    
    def _apply_web_defaults(self):
        """应用Web平台默认配置"""
        # 图形设置
        graphics_config = self.config.setdefault('graphics', {})
        graphics_config.setdefault('width', 1280)
        graphics_config.setdefault('height', 720)
        graphics_config.setdefault('fullscreen', False)
        graphics_config.setdefault('vsync', True)
        graphics_config.setdefault('webgl_version', 2)
        graphics_config.setdefault('use_instancing', True)
        
        # 输入设置
        input_config = self.config.setdefault('input', {})
        input_config.setdefault('pointer_lock', True)
        input_config.setdefault('touch_emulation', True)
        input_config.setdefault('prevent_default', True)
        
        # 性能设置
        perf_config = self.config.setdefault('performance', {})
        perf_config.setdefault('target_fps', 60)
        perf_config.setdefault('frame_timing', True)
        perf_config.setdefault('web_workers', True)
        
        # Web特定设置
        web_config = self.config.setdefault('web', {})
        web_config.setdefault('canvas_id', 'scene-weaver-canvas')
        web_config.setdefault('responsive', True)
        web_config.setdefault('service_worker', True)
        web_config.setdefault('webgpu_fallback', True)
    
    def _init_web_platform(self) -> bool:
        """初始化Web平台支持"""
        try:
            # 尝试导入Web API
            try:
                from js import window, document
                self.window = window
                self.document = document
            except ImportError:
                # 模拟环境用于测试
                self._create_mock_web_apis()
            
            # 创建Web平台实例
            self.web_platform = create_web_platform(self.config)
            if not self.web_platform:
                self.logger.error("无法创建Web平台实例")
                return False
            
            if not self.web_platform.initialize():
                self.logger.error("Web平台初始化失败")
                return False
            
            # 获取Canvas元素
            canvas_id = self.config['web']['canvas_id']
            self.canvas = self.document.getElementById(canvas_id)
            if not self.canvas:
                self.canvas = self.document.createElement('canvas')
                self.canvas.id = canvas_id
                self.canvas.width = self.config['graphics']['width']
                self.canvas.height = self.config['graphics']['height']
                self.document.body.appendChild(self.canvas)
            
            # 设置响应式设计
            if self.config['web']['responsive']:
                self.web_platform.setup_responsive_design()
            
            # 注册Service Worker
            if self.config['web']['service_worker']:
                self.web_platform.register_service_worker()
            
            # 获取屏幕信息并更新配置
            screen_info = self.web_platform.get_screen_info()
            if screen_info:
                self.config['graphics']['width'] = screen_info.get('width', 1280)
                self.config['graphics']['height'] = screen_info.get('height', 720)
                self.logger.info(f"屏幕信息: {screen_info}")
            
            browser_info = self.web_platform.get_browser_info()
            self.logger.info(f"浏览器信息: {browser_info}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Web平台初始化失败: {e}")
            return False
    
    def _create_mock_web_apis(self):
        """创建模拟的Web API用于测试"""
        class MockWindow:
            def __init__(self):
                self.innerWidth = 1280
                self.innerHeight = 720
                self.devicePixelRatio = 1
                self.screen = MockScreen()
                self.navigator = MockNavigator()
        
        class MockDocument:
            def __init__(self):
                self.elements = {}
            
            def getElementById(self, id):
                return self.elements.get(id)
            
            def createElement(self, tag):
                element = MockElement(tag)
                return element
            
            def getElementsByTagName(self, tag):
                return [MockElement(tag)]
        
        class MockScreen:
            def __init__(self):
                self.availWidth = 1280
                self.availHeight = 720
                self.colorDepth = 24
        
        class MockNavigator:
            def __init__(self):
                self.userAgent = "Mozilla/5.0 (Mock; Brython)"
                self.platform = "mock"
                self.serviceWorker = MockServiceWorker()
        
        class MockElement:
            def __init__(self, tag):
                self.tag = tag
                self.id = ""
                self.width = 1280
                self.height = 720
                self.style = {}
                self.children = []
            
            def appendChild(self, child):
                self.children.append(child)
            
            def addEventListener(self, event, handler):
                pass
        
        class MockServiceWorker:
            def register(self, path):
                class MockPromise:
                    def then(self, success_cb):
                        return self
                    def catch(self, error_cb):
                        return self
                return MockPromise()
        
        self.window = MockWindow()
        self.document = MockDocument()
        self.logger.info("创建模拟Web API环境")
    
    def _init_webgl_renderer(self) -> bool:
        """初始化WebGL渲染器"""
        try:
            self.webgl_renderer = WebGLRendererAdapter(None, self.config)
            
            if not self.webgl_renderer.initialize():
                self.logger.error("WebGL渲染器初始化失败")
                return False
            
            # 设置Canvas引用
            self.webgl_renderer.canvas = self.canvas
            
            self.logger.info("WebGL渲染器初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"WebGL渲染器初始化失败: {e}")
            return False
    
    def _init_input_handler(self) -> bool:
        """初始化输入处理器"""
        try:
            input_config = self.config.get('input', {})
            self.input_handler = WebInputHandler(input_config)
            
            if not self.input_handler.initialize(self.canvas, self.window, self.document):
                self.logger.error("输入处理器初始化失败")
                return False
            
            # 注册输入事件回调
            self._register_input_callbacks()
            
            self.logger.info("输入处理器初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"输入处理器初始化失败: {e}")
            return False
    
    def _register_input_callbacks(self):
        """注册输入事件回调"""
        def general_callback(event):
            # 将Web输入事件转换为标准输入事件
            self._handle_input_event(event)
        
        def mouse_callback(event):
            self._handle_mouse_event(event)
        
        def keyboard_callback(event):
            self._handle_keyboard_event(event)
        
        def touch_callback(event):
            self._handle_touch_event(event)
        
        self.input_handler.add_event_callback(general_callback)
        self.input_handler.add_mouse_callback(mouse_callback)
        self.input_handler.add_keyboard_callback(keyboard_callback)
        self.input_handler.add_touch_callback(touch_callback)
    
    def _handle_input_event(self, event):
        """处理通用输入事件"""
        if self.core_engine and self.core_engine.input_handler:
            # 转换为标准输入事件格式
            standardized_event = {
                'type': event.event_type.value,
                'x': event.x,
                'y': event.y,
                'button': event.button,
                'buttons': event.buttons,
                'key': event.key,
                'keyCode': event.keyCode,
                'delta_x': event.delta_x,
                'delta_y': event.delta_y,
                'timestamp': event.timestamp
            }
            self.core_engine.input_handler.process_event(standardized_event)
    
    def _handle_mouse_event(self, event):
        """处理鼠标事件"""
        self.logger.debug(f"鼠标事件: {event.event_type.value} at ({event.x}, {event.y})")
        # 可以在这里添加特定的鼠标处理逻辑
    
    def _handle_keyboard_event(self, event):
        """处理键盘事件"""
        self.logger.debug(f"键盘事件: {event.event_type.value} key={event.key}")
        # 可以在这里添加特定的键盘处理逻辑
    
    def _handle_touch_event(self, event):
        """处理触摸事件"""
        self.logger.debug(f"触摸事件: {event.event_type.value} touches={len(event.touches or [])}")
        # 可以在这里添加特定的触摸处理逻辑
    
    def _init_core_engine(self) -> bool:
        """初始化核心引擎"""
        try:
            self.core_engine = CoreEngine(self.config)
            
            if not self.core_engine.initialize():
                self.logger.error("核心引擎初始化失败")
                return False
            
            # 将WebGL渲染器连接到核心引擎
            if self.webgl_renderer and self.core_engine.renderer:
                # 这里需要适配WebGL渲染器到核心渲染系统
                self.logger.info("WebGL渲染器已准备好")
            
            self.logger.info("核心引擎初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"核心引擎初始化失败: {e}")
            return False
    
    def run(self):
        """运行Web应用主循环"""
        if not self.initialize():
            self.logger.error("应用初始化失败，无法启动")
            return
        
        try:
            self.logger.info("启动Web SceneWeaver主循环")
            
            # 启动渲染循环
            self._start_render_loop()
            
        except Exception as e:
            self.logger.error(f"应用运行出错: {e}")
        finally:
            self.cleanup()
    
    def _start_render_loop(self):
        """启动渲染循环"""
        try:
            def render_frame(timestamp):
                try:
                    # 更新核心引擎
                    if self.core_engine:
                        # 这里应该传入实际的帧时间
                        self.core_engine.update(1/60)
                        self.core_engine.render()
                    
                    # 继续下一帧
                    if self.window:
                        self.window.requestAnimationFrame(render_frame)
                        
                except Exception as e:
                    self.logger.error(f"渲染帧处理失败: {e}")
            
            # 启动渲染循环
            if self.window:
                self.window.requestAnimationFrame(render_frame)
                self.logger.info("Web渲染循环已启动")
            else:
                self.logger.warning("无法启动渲染循环：window对象不可用")
                
        except Exception as e:
            self.logger.error(f"启动渲染循环失败: {e}")
    
    def cleanup(self):
        """清理应用资源"""
        self.logger.info("开始清理应用资源...")
        
        if self.core_engine:
            self.core_engine.cleanup()
        
        if self.webgl_renderer:
            self.webgl_renderer.cleanup()
        
        if self.input_handler:
            self.input_handler.cleanup()
        
        if self.web_platform:
            self.web_platform.cleanup()
        
        self.logger.info("应用资源清理完成")


def main():
    """Web应用主函数"""
    app = WebSceneWeaver()
    app.run()


# Web导出函数
def create_web_app(config=None):
    """创建Web应用实例（供JavaScript调用）"""
    app = WebSceneWeaver()
    if config:
        app.config = config
    return app


def init_web_app():
    """初始化Web应用（供JavaScript调用）"""
    try:
        app = WebSceneWeaver()
        success = app.initialize()
        if success:
            app._start_render_loop()
        return success
    except Exception as e:
        print(f"Web应用初始化失败: {e}")
        return False


if __name__ == '__main__':
    main()