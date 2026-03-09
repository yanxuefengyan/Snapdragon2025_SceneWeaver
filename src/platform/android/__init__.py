"""
Android Platform Support - Android平台支持
SceneWeaver Android平台适配模块
"""

import sys
import os
import logging
from typing import Dict, Any, Optional

# Android特定的导入
try:
    import android
    from jnius import autoclass
    ANDROID_AVAILABLE = True
except ImportError:
    ANDROID_AVAILABLE = False

logger = logging.getLogger(__name__)


class AndroidPlatform:
    """Android平台适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Android特定组件
        self.activity = None
        self.context = None
        self.display_metrics = None
        
        # 平台状态
        self.initialized = False
        self.touch_supported = True
        self.accelerometer_available = False
        
    def initialize(self) -> bool:
        """初始化Android平台支持"""
        if not ANDROID_AVAILABLE:
            self.logger.warning("Android环境不可用")
            return False
            
        try:
            # 获取Activity和Context
            self.activity = autoclass('org.kivy.android.PythonActivity').mActivity
            self.context = self.activity.getApplicationContext()
            
            # 获取显示信息
            self._get_display_metrics()
            
            # 检查传感器支持
            self._check_sensor_support()
            
            self.initialized = True
            self.logger.info("Android平台初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"Android平台初始化失败: {e}")
            return False
    
    def _get_display_metrics(self):
        """获取显示度量信息"""
        try:
            DisplayMetrics = autoclass('android.util.DisplayMetrics')
            self.display_metrics = DisplayMetrics()
            self.activity.getWindowManager().getDefaultDisplay().getMetrics(self.display_metrics)
            
            self.logger.info(f"屏幕密度: {self.display_metrics.density}")
            self.logger.info(f"屏幕分辨率: {self.display_metrics.widthPixels}x{self.display_metrics.heightPixels}")
            
        except Exception as e:
            self.logger.warning(f"获取显示度量失败: {e}")
    
    def _check_sensor_support(self):
        """检查传感器支持"""
        try:
            SensorManager = autoclass('android.hardware.SensorManager')
            sensor_manager = self.context.getSystemService('sensor')
            
            # 检查加速度计
            accelerometer = sensor_manager.getDefaultSensor(SensorManager.SENSOR_ACCELEROMETER)
            self.accelerometer_available = accelerometer is not None
            
            self.logger.info(f"加速度计支持: {self.accelerometer_available}")
            
        except Exception as e:
            self.logger.warning(f"传感器检查失败: {e}")
    
    def get_screen_info(self) -> Dict[str, Any]:
        """获取屏幕信息"""
        if not self.display_metrics:
            return {}
            
        return {
            'width': self.display_metrics.widthPixels,
            'height': self.display_metrics.heightPixels,
            'density': self.display_metrics.density,
            'density_dpi': self.display_metrics.densityDpi,
            'scaled_density': self.display_metrics.scaledDensity
        }
    
    def is_mobile_device(self) -> bool:
        """检查是否为移动设备"""
        return True
    
    def get_platform_name(self) -> str:
        """获取平台名称"""
        return "Android"
    
    def cleanup(self):
        """清理平台资源"""
        self.initialized = False
        self.logger.info("Android平台资源清理完成")


# 平台检测函数
def is_android() -> bool:
    """检测是否在Android平台上运行"""
    return hasattr(sys, 'getandroidapilevel') or 'ANDROID_ARGUMENT' in os.environ


def get_android_api_level() -> Optional[int]:
    """获取Android API级别"""
    if hasattr(sys, 'getandroidapilevel'):
        return sys.getandroidapilevel()
    return None


# 创建平台实例的工厂函数
def create_android_platform(config: Dict[str, Any]) -> Optional[AndroidPlatform]:
    """创建Android平台实例"""
    if is_android():
        return AndroidPlatform(config)
    return None