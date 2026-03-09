"""
Web Platform Support - Web平台支持
SceneWeaver Web平台适配模块
"""

import sys
import os
import logging
from typing import Dict, Any, Optional

# Web特定的导入
try:
    # 检查是否在浏览器环境中
    import js  # Brython/Pyodide环境
    WEB_AVAILABLE = True
    BROWSER_ENVIRONMENT = True
except ImportError:
    # 检查是否在Node.js环境
    try:
        import node
        WEB_AVAILABLE = True
        BROWSER_ENVIRONMENT = False
    except ImportError:
        WEB_AVAILABLE = False
        BROWSER_ENVIRONMENT = False

logger = logging.getLogger(__name__)


class WebPlatform:
    """Web平台适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Web特定组件
        self.window = None
        self.document = None
        self.navigator = None
        self.canvas = None
        
        # 平台状态
        self.initialized = False
        self.webgl_available = False
        self.webgl2_available = False
        self.webgpu_available = False
        self.service_worker_available = False
        
        # 浏览器信息
        self.browser_name = ""
        self.browser_version = ""
        self.os_name = ""
        self.device_type = "desktop"  # desktop, mobile, tablet
        
    def initialize(self) -> bool:
        """初始化Web平台支持"""
        if not WEB_AVAILABLE:
            self.logger.warning("Web环境不可用")
            return False
            
        try:
            # 初始化浏览器API
            if BROWSER_ENVIRONMENT:
                self._init_browser_apis()
            else:
                self._init_node_apis()
            
            # 检查WebGL支持
            self._check_webgl_support()
            
            # 检查Service Worker支持
            self._check_service_worker_support()
            
            # 检测设备类型
            self._detect_device_type()
            
            self.initialized = True
            self.logger.info("Web平台初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"Web平台初始化失败: {e}")
            return False
    
    def _init_browser_apis(self):
        """初始化浏览器API"""
        try:
            # 获取全局对象
            self.window = js.window
            self.document = js.document
            self.navigator = js.navigator
            
            # 获取浏览器信息
            self._get_browser_info()
            
            self.logger.info("浏览器API初始化成功")
            
        except Exception as e:
            self.logger.error(f"浏览器API初始化失败: {e}")
    
    def _init_node_apis(self):
        """初始化Node.js API"""
        try:
            # Node.js环境下的模拟实现
            self.window = {
                'innerWidth': 1920,
                'innerHeight': 1080,
                'devicePixelRatio': 1
            }
            self.document = {
                'createElement': lambda tag: f"mock_{tag}_element"
            }
            self.navigator = {
                'userAgent': 'Node.js/18.0.0',
                'platform': 'node'
            }
            
            self.logger.info("Node.js API初始化成功")
            
        except Exception as e:
            self.logger.error(f"Node.js API初始化失败: {e}")
    
    def _get_browser_info(self):
        """获取浏览器信息"""
        try:
            user_agent = self.navigator.userAgent.lower()
            
            # 检测浏览器类型
            if 'chrome' in user_agent and 'edge' not in user_agent:
                self.browser_name = "Chrome"
            elif 'firefox' in user_agent:
                self.browser_name = "Firefox"
            elif 'safari' in user_agent and 'chrome' not in user_agent:
                self.browser_name = "Safari"
            elif 'edge' in user_agent:
                self.browser_name = "Edge"
            else:
                self.browser_name = "Unknown"
            
            # 检测操作系统
            if 'win' in user_agent:
                self.os_name = "Windows"
            elif 'mac' in user_agent:
                self.os_name = "macOS"
            elif 'linux' in user_agent:
                self.os_name = "Linux"
            elif 'android' in user_agent:
                self.os_name = "Android"
            elif 'iphone' in user_agent or 'ipad' in user_agent:
                self.os_name = "iOS"
            else:
                self.os_name = "Unknown"
                
        except Exception as e:
            self.logger.warning(f"浏览器信息检测失败: {e}")
    
    def _check_webgl_support(self):
        """检查WebGL支持"""
        try:
            if not self.document:
                return
                
            # 创建测试canvas
            test_canvas = self.document.createElement('canvas')
            if not test_canvas:
                return
            
            # 检查WebGL 1.0支持
            try:
                webgl_ctx = test_canvas.getContext('webgl') or test_canvas.getContext('experimental-webgl')
                self.webgl_available = webgl_ctx is not None
            except:
                self.webgl_available = False
            
            # 检查WebGL 2.0支持
            try:
                webgl2_ctx = test_canvas.getContext('webgl2')
                self.webgl2_available = webgl2_ctx is not None
            except:
                self.webgl2_available = False
            
            # 检查WebGPU支持（实验性）
            try:
                # WebGPU支持检查
                self.webgpu_available = hasattr(js, 'navigator') and hasattr(js.navigator, 'gpu')
            except:
                self.webgpu_available = False
            
            self.logger.info(f"WebGL支持: {self.webgl_available}, WebGL2: {self.webgl2_available}, WebGPU: {self.webgpu_available}")
            
        except Exception as e:
            self.logger.warning(f"WebGL支持检查失败: {e}")
    
    def _check_service_worker_support(self):
        """检查Service Worker支持"""
        try:
            if hasattr(self.navigator, 'serviceWorker'):
                self.service_worker_available = True
                self.logger.info("Service Worker支持可用")
            else:
                self.service_worker_available = False
                self.logger.info("Service Worker支持不可用")
                
        except Exception as e:
            self.logger.warning(f"Service Worker检查失败: {e}")
    
    def _detect_device_type(self):
        """检测设备类型"""
        try:
            # 基于屏幕尺寸和用户代理检测设备类型
            screen_width = getattr(self.window, 'innerWidth', 1920)
            screen_height = getattr(self.window, 'innerHeight', 1080)
            user_agent = getattr(self.navigator, 'userAgent', '').lower()
            
            # 移动设备检测
            is_mobile = ('mobile' in user_agent or 
                        'android' in user_agent or 
                        'iphone' in user_agent)
            
            # 平板设备检测
            is_tablet = ('tablet' in user_agent or 
                        'ipad' in user_agent)
            
            if is_tablet:
                self.device_type = "tablet"
            elif is_mobile:
                self.device_type = "mobile"
            else:
                self.device_type = "desktop"
            
            self.logger.info(f"检测到设备类型: {self.device_type} ({screen_width}x{screen_height})")
            
        except Exception as e:
            self.logger.warning(f"设备类型检测失败: {e}")
    
    def get_screen_info(self) -> Dict[str, Any]:
        """获取屏幕信息"""
        if not self.window:
            return {}
            
        try:
            return {
                'width': getattr(self.window, 'innerWidth', 1920),
                'height': getattr(self.window, 'innerHeight', 1080),
                'device_pixel_ratio': getattr(self.window, 'devicePixelRatio', 1),
                'avail_width': getattr(self.window, 'screen', {}).get('availWidth', 1920),
                'avail_height': getattr(self.window, 'screen', {}).get('availHeight', 1080),
                'color_depth': getattr(self.window, 'screen', {}).get('colorDepth', 24),
                'device_type': self.device_type
            }
        except Exception as e:
            self.logger.warning(f"屏幕信息获取失败: {e}")
            return {}
    
    def get_browser_info(self) -> Dict[str, Any]:
        """获取浏览器信息"""
        return {
            'name': self.browser_name,
            'version': self.browser_version,
            'os': self.os_name,
            'webgl': self.webgl_available,
            'webgl2': self.webgl2_available,
            'webgpu': self.webgpu_available,
            'service_worker': self.service_worker_available
        }
    
    def is_mobile_device(self) -> bool:
        """检查是否为移动设备"""
        return self.device_type in ['mobile', 'tablet']
    
    def get_platform_name(self) -> str:
        """获取平台名称"""
        return "Web"
    
    def setup_responsive_design(self):
        """设置响应式设计"""
        try:
            if not self.document:
                return
            
            # 添加viewport meta标签
            viewport_meta = self.document.createElement('meta')
            viewport_meta.name = 'viewport'
            viewport_meta.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'
            
            head = self.document.getElementsByTagName('head')[0]
            head.appendChild(viewport_meta)
            
            self.logger.info("响应式设计设置完成")
            
        except Exception as e:
            self.logger.warning(f"响应式设计设置失败: {e}")
    
    def register_service_worker(self, sw_path: str = '/sw.js'):
        """注册Service Worker"""
        try:
            if not self.service_worker_available:
                self.logger.warning("Service Worker不可用")
                return False
            
            # 注册Service Worker
            promise = self.navigator.serviceWorker.register(sw_path)
            
            def on_success(registration):
                self.logger.info(f"Service Worker注册成功: {sw_path}")
                return True
            
            def on_error(error):
                self.logger.error(f"Service Worker注册失败: {error}")
                return False
            
            promise.then(on_success).catch(on_error)
            return True
            
        except Exception as e:
            self.logger.error(f"Service Worker注册异常: {e}")
            return False
    
    def cleanup(self):
        """清理平台资源"""
        self.initialized = False
        self.window = None
        self.document = None
        self.navigator = None
        self.canvas = None
        self.logger.info("Web平台资源清理完成")


# 平台检测函数
def is_web() -> bool:
    """检测是否在Web平台上运行"""
    return WEB_AVAILABLE


def is_browser() -> bool:
    """检测是否在浏览器环境中运行"""
    return BROWSER_ENVIRONMENT


# 创建平台实例的工厂函数
def create_web_platform(config: Dict[str, Any]) -> Optional[WebPlatform]:
    """创建Web平台实例"""
    if is_web():
        return WebPlatform(config)
    return None