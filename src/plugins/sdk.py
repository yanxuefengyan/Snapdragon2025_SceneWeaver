"""
Plugin SDK - 插件开发工具包
SceneWeaver插件开发的API和工具集合
"""

import json
import logging
from typing import Dict, Any, List, Callable, Optional
from pathlib import Path
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

# 延迟导入核心模块以避免循环导入
# from ..core.engine import CoreEngine
# from ..graphics.renderer import Renderer
# from ..ai.ai_system import AISystem
# from ..input.input_handler import InputHandler
# from ..utils.config_manager import ConfigManager

logger = logging.getLogger(__name__)


@dataclass
class PluginContext:
    """插件上下文环境"""
    engine: Any = None  # CoreEngine
    renderer: Any = None  # Renderer
    ai_system: Any = None  # AISystem
    input_handler: Any = None  # InputHandler
    config_manager: Any = None  # ConfigManager
    plugin_config: Dict[str, Any] = field(default_factory=dict)


class PluginAPI(ABC):
    """插件API抽象基类"""
    
    def __init__(self, context: PluginContext):
        self.context = context
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def get_api_version(self) -> str:
        """获取API版本"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化API"""
        pass


class RenderEffectAPI(PluginAPI):
    """渲染效果API"""
    
    def get_api_version(self) -> str:
        return "1.0.0"
    
    def initialize(self) -> bool:
        """初始化渲染API"""
        try:
            # 注册渲染回调
            self.context.renderer.add_post_process_callback(self._post_process_callback)
            return True
        except Exception as e:
            self.logger.error(f"渲染API初始化失败: {e}")
            return False
    
    def _post_process_callback(self, surface):
        """后期处理回调"""
        # 子类需要实现具体的后期处理逻辑
        pass
    
    def register_shader(self, shader_name: str, vertex_code: str, fragment_code: str):
        """注册着色器"""
        try:
            shader_program = self.context.renderer.create_shader_program(
                vertex_code, fragment_code
            )
            self.context.renderer.register_custom_shader(shader_name, shader_program)
            self.logger.info(f"着色器注册成功: {shader_name}")
        except Exception as e:
            self.logger.error(f"着色器注册失败 {shader_name}: {e}")
    
    def apply_effect(self, effect_name: str, parameters: Dict[str, Any]):
        """应用渲染效果"""
        try:
            self.context.renderer.apply_post_process_effect(effect_name, parameters)
        except Exception as e:
            self.logger.error(f"应用效果失败 {effect_name}: {e}")


class AIModelAPI(PluginAPI):
    """AI模型API"""
    
    def get_api_version(self) -> str:
        return "1.0.0"
    
    def initialize(self) -> bool:
        """初始化AI API"""
        return True
    
    def register_model(self, model_name: str, model_path: str, 
                      model_type: str = "tensorflow"):
        """注册AI模型"""
        try:
            if model_type.lower() == "tensorflow":
                self.context.ai_system.register_tensorflow_model(model_name, model_path)
            elif model_type.lower() == "pytorch":
                self.context.ai_system.register_pytorch_model(model_name, model_path)
            else:
                raise ValueError(f"不支持的模型类型: {model_type}")
            
            self.logger.info(f"AI模型注册成功: {model_name}")
        except Exception as e:
            self.logger.error(f"AI模型注册失败 {model_name}: {e}")
    
    def run_inference(self, model_name: str, input_data: Any) -> Any:
        """运行模型推理"""
        try:
            return self.context.ai_system.run_inference(model_name, input_data)
        except Exception as e:
            self.logger.error(f"模型推理失败 {model_name}: {e}")
            return None


class InputHandlerAPI(PluginAPI):
    """输入处理API"""
    
    def get_api_version(self) -> str:
        return "1.0.0"
    
    def initialize(self) -> bool:
        """初始化输入API"""
        try:
            # 注册输入回调
            self.context.input_handler.register_callback(self._input_callback)
            return True
        except Exception as e:
            self.logger.error(f"输入API初始化失败: {e}")
            return False
    
    def _input_callback(self, event):
        """输入事件回调"""
        # 子类需要实现具体的输入处理逻辑
        pass
    
    def register_input_handler(self, event_type: str, handler: Callable):
        """注册输入处理器"""
        try:
            self.context.input_handler.register_event_handler(event_type, handler)
        except Exception as e:
            self.logger.error(f"输入处理器注册失败: {e}")


class UIComponentAPI(PluginAPI):
    """UI组件API"""
    
    def get_api_version(self) -> str:
        return "1.0.0"
    
    def initialize(self) -> bool:
        """初始化UI API"""
        return True
    
    def create_panel(self, panel_id: str, title: str, position: tuple, size: tuple):
        """创建UI面板"""
        try:
            # 这里应该调用实际的UI系统
            # 暂时返回模拟对象
            panel = {
                'id': panel_id,
                'title': title,
                'position': position,
                'size': size
            }
            self.logger.info(f"UI面板创建成功: {panel_id}")
            return panel
        except Exception as e:
            self.logger.error(f"UI面板创建失败 {panel_id}: {e}")
            return None
    
    def add_widget(self, panel_id: str, widget_type: str, properties: Dict[str, Any]):
        """添加UI控件"""
        try:
            widget = {
                'type': widget_type,
                'properties': properties
            }
            self.logger.info(f"UI控件添加成功: {widget_type}")
            return widget
        except Exception as e:
            self.logger.error(f"UI控件添加失败: {e}")
            return None


class ResourceManagerAPI(PluginAPI):
    """资源管理API"""
    
    def get_api_version(self) -> str:
        return "1.0.0"
    
    def initialize(self) -> bool:
        """初始化资源管理API"""
        return True
    
    def load_texture(self, texture_path: str) -> Any:
        """加载纹理资源"""
        try:
            return self.context.engine.resource_manager.load_resource(
                texture_path, "texture"
            )
        except Exception as e:
            self.logger.error(f"纹理加载失败 {texture_path}: {e}")
            return None
    
    def load_model(self, model_path: str) -> Any:
        """加载模型资源"""
        try:
            return self.context.engine.resource_manager.load_resource(
                model_path, "model"
            )
        except Exception as e:
            self.logger.error(f"模型加载失败 {model_path}: {e}")
            return None
    
    def register_resource_loader(self, resource_type: str, loader_func: Callable):
        """注册自定义资源加载器"""
        try:
            self.context.engine.resource_manager.register_loader(
                resource_type, loader_func
            )
        except Exception as e:
            self.logger.error(f"资源加载器注册失败: {e}")


class PluginSDK:
    """插件开发工具包主类"""
    
    def __init__(self, context: PluginContext):
        self.context = context
        self.logger = logging.getLogger(__name__)
        
        # 初始化各个API模块
        self.render_api = RenderEffectAPI(context)
        self.ai_api = AIModelAPI(context)
        self.input_api = InputHandlerAPI(context)
        self.ui_api = UIComponentAPI(context)
        self.resource_api = ResourceManagerAPI(context)
        
        self.apis = {
            'render': self.render_api,
            'ai': self.ai_api,
            'input': self.input_api,
            'ui': self.ui_api,
            'resource': self.resource_api
        }
    
    def initialize_all_apis(self) -> bool:
        """初始化所有API"""
        try:
            for api_name, api in self.apis.items():
                if not api.initialize():
                    self.logger.error(f"API初始化失败: {api_name}")
                    return False
            
            self.logger.info("所有API初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"API初始化异常: {e}")
            return False
    
    def get_api(self, api_name: str) -> Optional[PluginAPI]:
        """获取指定API"""
        return self.apis.get(api_name)
    
    def create_manifest(self, plugin_info: Dict[str, Any], output_path: str):
        """创建插件清单文件"""
        try:
            manifest = {
                'name': plugin_info.get('name', 'unnamed_plugin'),
                'version': plugin_info.get('version', '1.0.0'),
                'author': plugin_info.get('author', 'Anonymous'),
                'description': plugin_info.get('description', ''),
                'type': plugin_info.get('type', 'custom'),
                'entry_point': plugin_info.get('entry_point', 'plugin.py'),
                'dependencies': plugin_info.get('dependencies', []),
                'api_version': '1.0.0',
                'compatible_versions': ['>=1.0.0'],
                'license': plugin_info.get('license', 'MIT')
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"清单文件创建成功: {output_path}")
            
        except Exception as e:
            self.logger.error(f"清单文件创建失败: {e}")
    
    def validate_plugin_structure(self, plugin_path: str) -> List[str]:
        """验证插件目录结构"""
        errors = []
        plugin_dir = Path(plugin_path)
        
        # 检查必需文件
        required_files = ['plugin.py', 'manifest.json']
        for file_name in required_files:
            if not (plugin_dir / file_name).exists():
                errors.append(f"缺少必需文件: {file_name}")
        
        # 检查清单文件格式
        try:
            with open(plugin_dir / 'manifest.json', 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            required_fields = ['name', 'version', 'type']
            for field in required_fields:
                if field not in manifest:
                    errors.append(f"清单缺少字段: {field}")
                    
        except Exception as e:
            errors.append(f"清单文件格式错误: {e}")
        
        return errors
    
    def package_plugin(self, plugin_path: str, output_path: str) -> bool:
        """打包插件为分发格式"""
        try:
            import zipfile
            
            plugin_dir = Path(plugin_path)
            output_file = Path(output_path)
            
            # 验证插件结构
            validation_errors = self.validate_plugin_structure(plugin_path)
            if validation_errors:
                self.logger.error("插件验证失败:")
                for error in validation_errors:
                    self.logger.error(f"  - {error}")
                return False
            
            # 创建ZIP包
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in plugin_dir.rglob('*'):
                    if file_path.is_file():
                        arc_name = file_path.relative_to(plugin_dir)
                        zipf.write(file_path, arc_name)
            
            self.logger.info(f"插件打包成功: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"插件打包失败: {e}")
            return False
    
    def get_template_files(self) -> Dict[str, str]:
        """获取插件模板文件"""
        return {
            'plugin.py': '''"""
{{plugin_name}} - {{plugin_description}}
"""

from src.plugins.plugin_manager import PluginBase, PluginInfo, PluginType
from src.plugins.sdk import PluginContext

class {{PluginClass}}(PluginBase):
    """{{plugin_name}}插件主类"""
    
    @property
    def plugin_info(self) -> PluginInfo:
        return PluginInfo(
            name="{{plugin_name}}",
            version="{{version}}",
            author="{{author}}",
            description="{{description}}",
            plugin_type=PluginType.{{plugin_type}},
            module_name="{{module_name}}",
            file_path=__file__,
            dependencies=[]
        )
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            # TODO: 实现插件初始化逻辑
            return True
        except Exception as e:
            self.logger.error(f"插件初始化失败: {{e}}")
            return False
    
    def cleanup(self):
        """清理插件资源"""
        # TODO: 实现资源清理逻辑
        pass

# 插件入口点
def create_plugin(context: PluginContext):
    """创建插件实例"""
    return {{PluginClass}}(context)
''',
            'manifest.json': '''{
  "name": "{{plugin_name}}",
  "version": "{{version}}",
  "author": "{{author}}",
  "description": "{{description}}",
  "type": "{{plugin_type}}",
  "entry_point": "plugin.py",
  "dependencies": [],
  "api_version": "1.0.0",
  "compatible_versions": [">=1.0.0"],
  "license": "MIT"
}'''
        }


# 插件开发助手
class PluginDevelopmentHelper:
    """插件开发助手类"""
    
    @staticmethod
    def create_plugin_scaffold(plugin_name: str, plugin_type: str, 
                             output_dir: str, **kwargs):
        """创建插件脚手架"""
        try:
            from string import Template
            
            # 创建插件目录
            plugin_dir = Path(output_dir) / plugin_name
            plugin_dir.mkdir(parents=True, exist_ok=True)
            
            # 获取模板
            sdk = PluginSDK(PluginContext(None, None, None, None, None))
            templates = sdk.get_template_files()
            
            # 填充模板变量
            template_vars = {
                'plugin_name': plugin_name,
                'plugin_type': plugin_type.upper(),
                'PluginClass': ''.join(word.capitalize() for word in plugin_name.split('_')),
                'module_name': f"{plugin_name}.plugin",
                'version': kwargs.get('version', '1.0.0'),
                'author': kwargs.get('author', 'Developer'),
                'description': kwargs.get('description', f'{plugin_name} plugin for SceneWeaver')
            }
            
            # 生成文件
            for filename, template_content in templates.items():
                template = Template(template_content)
                content = template.substitute(template_vars)
                
                with open(plugin_dir / filename, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            logger.info(f"插件脚手架创建成功: {plugin_dir}")
            return str(plugin_dir)
            
        except Exception as e:
            logger.error(f"插件脚手架创建失败: {e}")
            return None
    
    @staticmethod
    def validate_plugin_code(plugin_path: str) -> List[str]:
        """验证插件代码质量"""
        errors = []
        
        try:
            import ast
            
            plugin_dir = Path(plugin_path)
            plugin_file = plugin_dir / 'plugin.py'
            
            if not plugin_file.exists():
                errors.append("缺少plugin.py文件")
                return errors
            
            # 解析Python代码
            with open(plugin_file, 'r', encoding='utf-8') as f:
                code = f.read()
            
            tree = ast.parse(code)
            
            # 检查必需的类和方法
            has_plugin_class = False
            has_initialize_method = False
            has_cleanup_method = False
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id == 'PluginBase':
                            has_plugin_class = True
                            
                            # 检查必需的方法
                            for item in node.body:
                                if isinstance(item, ast.FunctionDef):
                                    if item.name == 'initialize':
                                        has_initialize_method = True
                                    elif item.name == 'cleanup':
                                        has_cleanup_method = True
            
            if not has_plugin_class:
                errors.append("未找到继承自PluginBase的类")
            
            if not has_initialize_method:
                errors.append("缺少initialize方法")
            
            if not has_cleanup_method:
                errors.append("缺少cleanup方法")
                
        except SyntaxError as e:
            errors.append(f"语法错误: {e}")
        except Exception as e:
            errors.append(f"代码验证失败: {e}")
        
        return errors