"""
Example Render Effect Plugin - 示例渲染效果插件
演示如何创建SceneWeaver渲染效果插件
"""

from src.plugins.plugin_manager import PluginBase, PluginInfo, PluginType
from src.plugins.sdk import PluginContext


class ExampleRenderEffectPlugin(PluginBase):
    """示例渲染效果插件"""
    
    @property
    def plugin_info(self) -> PluginInfo:
        return PluginInfo(
            name="example_render_effect",
            version="1.0.0",
            author="SceneWeaver Team",
            description="示例渲染效果插件，展示模糊和色彩调整效果",
            plugin_type=PluginType.RENDER_EFFECT,
            module_name="example_render_effect.plugin",
            file_path=__file__,
            dependencies=[],
            config_schema={
                "blur_strength": {
                    "type": "float",
                    "default": 1.0,
                    "min": 0.0,
                    "max": 10.0,
                    "description": "模糊强度"
                },
                "saturation": {
                    "type": "float",
                    "default": 1.0,
                    "min": 0.0,
                    "max": 2.0,
                    "description": "饱和度调整"
                },
                "brightness": {
                    "type": "float",
                    "default": 1.0,
                    "min": 0.0,
                    "max": 2.0,
                    "description": "亮度调整"
                }
            }
        )
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            # 获取渲染API
            render_api = self.plugin_manager.get_api('render')
            if not render_api:
                self.logger.error("无法获取渲染API")
                return False
            
            # 注册自定义着色器
            self._register_shaders(render_api)
            
            self.logger.info("示例渲染效果插件初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"插件初始化失败: {e}")
            return False
    
    def _register_shaders(self, render_api):
        """注册自定义着色器"""
        # 简化的片段着色器示例
        fragment_shader = """
        uniform sampler2D texture;
        uniform float blur_strength;
        uniform float saturation;
        uniform float brightness;
        
        void main() {
            vec4 color = texture2D(texture, gl_TexCoord[0].xy);
            
            // 应用亮度调整
            color.rgb *= brightness;
            
            // 应用饱和度调整
            float gray = dot(color.rgb, vec3(0.299, 0.587, 0.114));
            color.rgb = mix(vec3(gray), color.rgb, saturation);
            
            gl_FragColor = color;
        }
        """
        
        # 注册着色器（实际实现中需要完整的顶点着色器）
        # render_api.register_shader("example_effect", vertex_shader, fragment_shader)
    
    def cleanup(self):
        """清理插件资源"""
        self.logger.info("示例渲染效果插件资源清理完成")


# 插件入口点
def create_plugin(context: PluginContext):
    """创建插件实例"""
    return ExampleRenderEffectPlugin(context)