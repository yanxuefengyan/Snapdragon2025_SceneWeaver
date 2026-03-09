"""
iOS Platform Support - iOS平台支持
SceneWeaver iOS平台适配模块
"""

import sys
import os
import logging
from typing import Dict, Any, Optional

# iOS特定的导入
try:
    import objc
    from Foundation import NSBundle
    from UIKit import UIScreen, UIDevice
    IOS_AVAILABLE = True
except ImportError:
    IOS_AVAILABLE = False

logger = logging.getLogger(__name__)


class IOSPlatform:
    """iOS平台适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # iOS特定组件
        self.screen = None
        self.device = None
        self.bundle = None
        
        # 平台状态
        self.initialized = False
        self.touch_supported = True
        self.metal_available = False
        self.ar_kit_available = False
        
    def initialize(self) -> bool:
        """初始化iOS平台支持"""
        if not IOS_AVAILABLE:
            self.logger.warning("iOS环境不可用")
            return False
            
        try:
            # 获取设备和屏幕信息
            self.device = UIDevice.currentDevice()
            self.screen = UIScreen.mainScreen()
            self.bundle = NSBundle.mainBundle()
            
            # 检查Metal支持
            self._check_metal_support()
            
            # 检查ARKit支持
            self._check_ar_kit_support()
            
            self.initialized = True
            self.logger.info("iOS平台初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"iOS平台初始化失败: {e}")
            return False
    
    def _check_metal_support(self):
        """检查Metal支持"""
        try:
            # 检查设备是否支持Metal
            from Metal import MTLCreateSystemDefaultDevice
            device = MTLCreateSystemDefaultDevice()
            self.metal_available = device is not None
            
            self.logger.info(f"Metal支持: {self.metal_available}")
            
        except Exception as e:
            self.logger.warning(f"Metal支持检查失败: {e}")
            self.metal_available = False
    
    def _check_ar_kit_support(self):
        """检查ARKit支持"""
        try:
            # 检查ARKit可用性
            import ARKit
            self.ar_kit_available = hasattr(ARKit, 'ARWorldTrackingConfiguration')
            
            self.logger.info(f"ARKit支持: {self.ar_kit_available}")
            
        except Exception as e:
            self.logger.warning(f"ARKit支持检查失败: {e}")
            self.ar_kit_available = False
    
    def get_screen_info(self) -> Dict[str, Any]:
        """获取屏幕信息"""
        if not self.screen:
            return {}
            
        bounds = self.screen.bounds()
        scale = self.screen.scale()
        
        return {
            'width': bounds.size.width,
            'height': bounds.size.height,
            'scale': scale,
            'native_scale': self.screen.nativeScale(),
            'brightness': self.screen.brightness(),
            'orientation': str(self.screen.coordinateSpace())
        }
    
    def get_device_info(self) -> Dict[str, Any]:
        """获取设备信息"""
        if not self.device:
            return {}
            
        return {
            'name': self.device.name(),
            'system_name': self.device.systemName(),
            'system_version': self.device.systemVersion(),
            'model': self.device.model(),
            'localized_model': self.device.localizedModel(),
            'identifier_for_vendor': str(self.device.identifierForVendor())
        }
    
    def get_bundle_info(self) -> Dict[str, Any]:
        """获取应用包信息"""
        if not self.bundle:
            return {}
            
        return {
            'bundle_id': self.bundle.bundleIdentifier(),
            'version': self.bundle.objectForInfoDictionaryKey_('CFBundleShortVersionString'),
            'build': self.bundle.objectForInfoDictionaryKey_('CFBundleVersion'),
            'name': self.bundle.objectForInfoDictionaryKey_('CFBundleDisplayName')
        }
    
    def is_mobile_device(self) -> bool:
        """检查是否为移动设备"""
        return True
    
    def get_platform_name(self) -> str:
        """获取平台名称"""
        return "iOS"
    
    def enable_immersive_mode(self):
        """启用沉浸式模式"""
        try:
            from UIKit import UIApplication
            app = UIApplication.sharedApplication()
            if app.respondsToSelector_('setStatusBarHidden:'):
                app.setStatusBarHidden_(True)
            self.logger.info("沉浸式模式已启用")
        except Exception as e:
            self.logger.warning(f"启用沉浸式模式失败: {e}")
    
    def disable_idle_timer(self):
        """禁用屏幕休眠"""
        try:
            from UIKit import UIApplication
            app = UIApplication.sharedApplication()
            app.setIdleTimerDisabled_(True)
            self.logger.info("屏幕休眠已禁用")
        except Exception as e:
            self.logger.warning(f"禁用屏幕休眠失败: {e}")
    
    def cleanup(self):
        """清理平台资源"""
        self.initialized = False
        self.logger.info("iOS平台资源清理完成")


# 平台检测函数
def is_ios() -> bool:
    """检测是否在iOS平台上运行"""
    return sys.platform == 'darwin' and 'iPhone' in os.uname().machine


def get_ios_version() -> Optional[str]:
    """获取iOS版本"""
    if IOS_AVAILABLE and hasattr(UIDevice, 'currentDevice'):
        try:
            device = UIDevice.currentDevice()
            return device.systemVersion()
        except:
            pass
    return None


# 创建平台实例的工厂函数
def create_ios_platform(config: Dict[str, Any]) -> Optional[IOSPlatform]:
    """创建iOS平台实例"""
    if is_ios():
        return IOSPlatform(config)
    return None