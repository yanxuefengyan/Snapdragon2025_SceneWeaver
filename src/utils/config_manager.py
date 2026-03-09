"""
Config Manager - 配置管理器
处理YAML配置文件的读取和管理
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Union


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.config = {}
        self.logger = logging.getLogger(__name__)
        
        self.load_config()
    
    def load_config(self) -> bool:
        """
        加载配置文件
        
        Returns:
            bool: 加载是否成功
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f)
                self.logger.info(f"配置文件加载成功: {self.config_path}")
                return True
            else:
                self.logger.warning(f"配置文件不存在: {self.config_path}")
                self._create_default_config()
                return False
                
        except Exception as e:
            self.logger.error(f"配置文件加载失败: {e}")
            self._create_default_config()
            return False
    
    def _create_default_config(self):
        """创建默认配置"""
        default_config = {
            'graphics': {
                'width': 1280,
                'height': 720,
                'fullscreen': False,
                'vsync': True
            },
            'input': {
                'mouse_sensitivity': 0.1,
                'movement_speed': 2.5
            },
            'ai': {
                'model_path': './models',
                'device': 'auto'
            },
            'performance': {
                'target_fps': 60,
                'max_memory_mb': 2048
            }
        }
        
        self.config = default_config
        self.save_config()
        self.logger.info("已创建默认配置文件")
    
    def save_config(self) -> bool:
        """
        保存配置到文件
        
        Returns:
            bool: 保存是否成功
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            self.logger.info(f"配置文件保存成功: {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"配置文件保存失败: {e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """
        获取完整配置
        
        Returns:
            Dict: 配置字典
        """
        return self.config
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置项（支持嵌套路径）
        
        Args:
            key_path: 配置项路径，如 'graphics.width'
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> bool:
        """
        设置配置项
        
        Args:
            key_path: 配置项路径
            value: 配置值
            
        Returns:
            bool: 设置是否成功
        """
        keys = key_path.split('.')
        config = self.config
        
        try:
            # 导航到倒数第二层
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            
            # 设置最后一层的值
            config[keys[-1]] = value
            return True
            
        except Exception as e:
            self.logger.error(f"设置配置项失败 {key_path}: {e}")
            return False
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """
        批量更新配置
        
        Args:
            updates: 更新字典
            
        Returns:
            bool: 更新是否成功
        """
        try:
            self.config.update(updates)
            return True
        except Exception as e:
            self.logger.error(f"批量更新配置失败: {e}")
            return False
    
    def validate_config(self) -> bool:
        """
        验证配置的有效性
        
        Returns:
            bool: 配置是否有效
        """
        required_sections = ['graphics', 'input', 'ai']
        
        for section in required_sections:
            if section not in self.config:
                self.logger.error(f"缺少必要配置段: {section}")
                return False
        
        # 验证图形配置
        graphics = self.config.get('graphics', {})
        if not isinstance(graphics.get('width', 0), int) or graphics.get('width', 0) <= 0:
            self.logger.error("无效的图形宽度配置")
            return False
            
        if not isinstance(graphics.get('height', 0), int) or graphics.get('height', 0) <= 0:
            self.logger.error("无效的图形高度配置")
            return False
        
        # 验证AI配置
        ai = self.config.get('ai', {})
        if not isinstance(ai.get('device', ''), str):
            self.logger.error("无效的AI设备配置")
            return False
        
        return True