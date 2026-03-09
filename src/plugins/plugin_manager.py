"""
Plugin Manager - 插件管理系统
SceneWeaver插件系统的核心管理模块
"""

import os
import sys
import importlib
import importlib.util
import logging
from typing import Dict, List, Any, Optional, Type
from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class PluginType(Enum):
    """插件类型枚举"""
    RENDER_EFFECT = "render_effect"      # 渲染效果插件
    AI_MODEL = "ai_model"               # AI模型插件
    INPUT_HANDLER = "input_handler"     # 输入处理插件
    UI_COMPONENT = "ui_component"       # UI组件插件
    RESOURCE_LOADER = "resource_loader" # 资源加载插件
    EXPORT_FORMAT = "export_format"     # 导出格式插件
    CUSTOM = "custom"                   # 自定义插件


class PluginStatus(Enum):
    """插件状态枚举"""
    LOADED = "loaded"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    UNLOADED = "unloaded"


@dataclass
class PluginInfo:
    """插件信息数据类"""
    name: str
    version: str
    author: str
    description: str
    plugin_type: PluginType
    module_name: str
    file_path: str
    dependencies: List[str] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    status: PluginStatus = PluginStatus.LOADED
    error_message: str = ""


class PluginBase(ABC):
    """插件基类"""
    
    def __init__(self, plugin_manager, config: Dict[str, Any]):
        self.plugin_manager = plugin_manager
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.is_initialized = False
    
    @property
    @abstractmethod
    def plugin_info(self) -> PluginInfo:
        """获取插件信息"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化插件"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """清理插件资源"""
        pass
    
    def on_activate(self):
        """插件激活时调用"""
        pass
    
    def on_deactivate(self):
        """插件停用时调用"""
        pass
    
    def get_config_schema(self) -> Dict[str, Any]:
        """获取配置模式"""
        return self.plugin_info.config_schema


class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, PluginBase] = {}
        self.plugin_infos: Dict[str, PluginInfo] = {}
        self.active_plugins: List[str] = []
        self.logger = logging.getLogger(__name__)
        
        # 创建插件目录
        self.plugins_dir.mkdir(exist_ok=True)
        
        # 添加插件目录到Python路径
        if str(self.plugins_dir.absolute()) not in sys.path:
            sys.path.insert(0, str(self.plugins_dir.absolute()))
    
    def discover_plugins(self) -> List[PluginInfo]:
        """发现可用插件"""
        plugin_infos = []
        
        if not self.plugins_dir.exists():
            self.logger.warning(f"插件目录不存在: {self.plugins_dir}")
            return plugin_infos
        
        # 遍历插件目录
        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir() and not plugin_dir.name.startswith('.'):
                try:
                    plugin_info = self._load_plugin_info(plugin_dir)
                    if plugin_info:
                        plugin_infos.append(plugin_info)
                        self.plugin_infos[plugin_info.name] = plugin_info
                except Exception as e:
                    self.logger.error(f"加载插件信息失败 {plugin_dir.name}: {e}")
        
        self.logger.info(f"发现 {len(plugin_infos)} 个插件")
        return plugin_infos
    
    def _load_plugin_info(self, plugin_dir: Path) -> Optional[PluginInfo]:
        """加载单个插件信息"""
        # 查找插件主模块
        main_module_files = list(plugin_dir.glob("plugin.py")) + list(plugin_dir.glob("*.py"))
        if not main_module_files:
            return None
        
        main_module_file = main_module_files[0]
        module_name = f"{plugin_dir.name}.plugin"
        
        try:
            # 动态导入模块
            spec = importlib.util.spec_from_file_location(module_name, main_module_file)
            if spec is None or spec.loader is None:
                return None
                
            module = importlib.util.module_from_spec(spec)
            
            # 添加到sys.modules以解决导入问题
            sys.modules[module_name] = module
            
            spec.loader.exec_module(module)
            
            # 查找插件类
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, PluginBase) and 
                    attr != PluginBase):
                    plugin_class = attr
                    break
            
            if not plugin_class:
                self.logger.warning(f"插件模块中未找到PluginBase子类: {module_name}")
                return None
            
            # 创建插件实例获取信息
            dummy_config = {}
            plugin_instance = plugin_class(self, dummy_config)
            plugin_info = plugin_instance.plugin_info
            
            # 更新文件路径信息
            plugin_info.file_path = str(main_module_file.absolute())
            plugin_info.module_name = module_name
            
            return plugin_info
            
        except Exception as e:
            self.logger.error(f"加载插件失败 {plugin_dir.name}: {e}")
            return None
    
    def load_plugin(self, plugin_name: str, config: Dict[str, Any] = None) -> bool:
        """加载指定插件"""
        if plugin_name in self.plugins:
            self.logger.info(f"插件已加载: {plugin_name}")
            return True
        
        if plugin_name not in self.plugin_infos:
            self.logger.error(f"插件信息不存在: {plugin_name}")
            return False
        
        plugin_info = self.plugin_infos[plugin_name]
        
        try:
            # 导入插件模块
            module = importlib.import_module(plugin_info.module_name)
            
            # 查找插件类
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, PluginBase) and 
                    attr != PluginBase):
                    plugin_class = attr
                    break
            
            if not plugin_class:
                raise RuntimeError(f"未找到插件类: {plugin_info.module_name}")
            
            # 创建插件实例
            plugin_config = config or {}
            plugin_instance = plugin_class(self, plugin_config)
            
            # 初始化插件
            if not plugin_instance.initialize():
                raise RuntimeError("插件初始化失败")
            
            # 注册插件
            self.plugins[plugin_name] = plugin_instance
            plugin_info.status = PluginStatus.LOADED
            
            self.logger.info(f"插件加载成功: {plugin_name}")
            return True
            
        except Exception as e:
            plugin_info.status = PluginStatus.ERROR
            plugin_info.error_message = str(e)
            self.logger.error(f"插件加载失败 {plugin_name}: {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """卸载指定插件"""
        if plugin_name not in self.plugins:
            self.logger.warning(f"插件未加载: {plugin_name}")
            return False
        
        try:
            plugin = self.plugins[plugin_name]
            
            # 停用插件（如果处于激活状态）
            if plugin_name in self.active_plugins:
                self.deactivate_plugin(plugin_name)
            
            # 清理插件资源
            plugin.cleanup()
            
            # 移除插件引用
            del self.plugins[plugin_name]
            
            # 更新插件状态
            if plugin_name in self.plugin_infos:
                self.plugin_infos[plugin_name].status = PluginStatus.UNLOADED
            
            self.logger.info(f"插件卸载成功: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"插件卸载失败 {plugin_name}: {e}")
            return False
    
    def activate_plugin(self, plugin_name: str) -> bool:
        """激活插件"""
        if plugin_name not in self.plugins:
            self.logger.error(f"插件未加载: {plugin_name}")
            return False
        
        if plugin_name in self.active_plugins:
            self.logger.info(f"插件已激活: {plugin_name}")
            return True
        
        try:
            plugin = self.plugins[plugin_name]
            plugin.on_activate()
            self.active_plugins.append(plugin_name)
            
            if plugin_name in self.plugin_infos:
                self.plugin_infos[plugin_name].status = PluginStatus.ACTIVE
            
            self.logger.info(f"插件激活成功: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"插件激活失败 {plugin_name}: {e}")
            return False
    
    def deactivate_plugin(self, plugin_name: str) -> bool:
        """停用插件"""
        if plugin_name not in self.active_plugins:
            self.logger.warning(f"插件未激活: {plugin_name}")
            return False
        
        try:
            plugin = self.plugins[plugin_name]
            plugin.on_deactivate()
            self.active_plugins.remove(plugin_name)
            
            if plugin_name in self.plugin_infos:
                self.plugin_infos[plugin_name].status = PluginStatus.INACTIVE
            
            self.logger.info(f"插件停用成功: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"插件停用失败 {plugin_name}: {e}")
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """获取插件实例"""
        return self.plugins.get(plugin_name)
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """获取插件信息"""
        return self.plugin_infos.get(plugin_name)
    
    def list_plugins(self, plugin_type: Optional[PluginType] = None) -> List[str]:
        """列出插件"""
        if plugin_type:
            return [name for name, info in self.plugin_infos.items() 
                   if info.plugin_type == plugin_type]
        return list(self.plugin_infos.keys())
    
    def get_active_plugins(self) -> List[str]:
        """获取激活的插件列表"""
        return self.active_plugins.copy()
    
    def validate_dependencies(self, plugin_name: str) -> List[str]:
        """验证插件依赖"""
        if plugin_name not in self.plugin_infos:
            return [f"插件不存在: {plugin_name}"]
        
        plugin_info = self.plugin_infos[plugin_name]
        missing_deps = []
        
        for dep in plugin_info.dependencies:
            if dep not in self.plugin_infos:
                missing_deps.append(dep)
        
        return missing_deps
    
    def install_plugin_from_file(self, plugin_file: str) -> bool:
        """从文件安装插件"""
        try:
            plugin_path = Path(plugin_file)
            if not plugin_path.exists():
                self.logger.error(f"插件文件不存在: {plugin_file}")
                return False
            
            # 创建插件目录
            plugin_name = plugin_path.stem
            plugin_dir = self.plugins_dir / plugin_name
            plugin_dir.mkdir(exist_ok=True)
            
            # 复制插件文件
            import shutil
            if plugin_path.is_dir():
                shutil.copytree(plugin_path, plugin_dir, dirs_exist_ok=True)
            else:
                shutil.copy2(plugin_path, plugin_dir / plugin_path.name)
            
            # 重新发现插件
            self.discover_plugins()
            
            self.logger.info(f"插件安装成功: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"插件安装失败: {e}")
            return False
    
    def remove_plugin(self, plugin_name: str) -> bool:
        """删除插件"""
        try:
            # 先卸载插件
            if plugin_name in self.plugins:
                self.unload_plugin(plugin_name)
            
            # 删除插件目录
            plugin_dir = self.plugins_dir / plugin_name
            if plugin_dir.exists():
                import shutil
                shutil.rmtree(plugin_dir)
            
            # 清理插件信息
            if plugin_name in self.plugin_infos:
                del self.plugin_infos[plugin_name]
            
            self.logger.info(f"插件删除成功: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"插件删除失败 {plugin_name}: {e}")
            return False
    
    def cleanup(self):
        """清理插件管理器"""
        # 停用所有插件
        for plugin_name in self.active_plugins.copy():
            self.deactivate_plugin(plugin_name)
        
        # 卸载所有插件
        for plugin_name in list(self.plugins.keys()):
            self.unload_plugin(plugin_name)
        
        self.logger.info("插件管理器清理完成")