"""
Example AI Model Plugin - 示例AI模型插件
演示如何创建SceneWeaver AI模型插件
"""

import numpy as np
from src.plugins.plugin_manager import PluginBase, PluginInfo, PluginType
from src.plugins.sdk import PluginContext


class ExampleAIModelPlugin(PluginBase):
    """示例AI模型插件"""
    
    @property
    def plugin_info(self) -> PluginInfo:
        return PluginInfo(
            name="example_ai_model",
            version="1.0.0",
            author="SceneWeaver Team",
            description="示例AI模型插件，提供简单的图像分类功能",
            plugin_type=PluginType.AI_MODEL,
            module_name="example_ai_model.plugin",
            file_path=__file__,
            dependencies=["numpy"],
            config_schema={
                "model_type": {
                    "type": "string",
                    "default": "simple_classifier",
                    "options": ["simple_classifier", "feature_extractor"],
                    "description": "模型类型"
                },
                "confidence_threshold": {
                    "type": "float",
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "description": "置信度阈值"
                }
            }
        )
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            # 获取AI API
            ai_api = self.plugin_manager.get_api('ai')
            if not ai_api:
                self.logger.error("无法获取AI API")
                return False
            
            # 注册示例模型
            self._register_example_model(ai_api)
            
            self.logger.info("示例AI模型插件初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"插件初始化失败: {e}")
            return False
    
    def _register_example_model(self, ai_api):
        """注册示例AI模型"""
        # 注册一个简单的图像分类模型
        def simple_classifier(image_data):
            """简单的图像分类函数"""
            # 模拟图像处理
            if isinstance(image_data, np.ndarray):
                # 简单的特征提取
                mean_value = np.mean(image_data)
                std_value = np.std(image_data)
                
                # 简单的分类逻辑
                if mean_value > 128:
                    return {"class": "bright", "confidence": 0.8}
                else:
                    return {"class": "dark", "confidence": 0.7}
            else:
                return {"class": "unknown", "confidence": 0.0}
        
        # 注册模型（实际实现中需要调用AI API的方法）
        # ai_api.register_model("simple_image_classifier", simple_classifier, "custom")
    
    def cleanup(self):
        """清理插件资源"""
        self.logger.info("示例AI模型插件资源清理完成")


# 插件入口点
def create_plugin(context: PluginContext):
    """创建插件实例"""
    return ExampleAIModelPlugin(context)