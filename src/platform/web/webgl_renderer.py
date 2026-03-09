"""
Web WebGL Renderer - Web WebGL渲染器
基于WebGL的高性能图形渲染适配器
"""

import logging
from typing import Dict, Any, Optional, List
import numpy as np

logger = logging.getLogger(__name__)


class WebGLRendererAdapter:
    """WebGL渲染适配器"""
    
    def __init__(self, base_renderer, config: Dict[str, Any]):
        self.base_renderer = base_renderer
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # WebGL特定组件
        self.gl_context = None
        self.canvas = None
        self.program = None
        self.vertex_buffer = None
        self.index_buffer = None
        
        # 渲染状态
        self.viewport_width = 1280
        self.viewport_height = 720
        self.clear_color = [0.0, 0.0, 0.0, 1.0]
        
        # WebGL版本支持
        self.webgl_version = 1  # 1 or 2
        self.extensions = []
        
        # 着色器程序
        self.shader_programs = {}
        self.current_program = None
        
        # 纹理管理
        self.textures = {}
        self.texture_units = {}
        
        # 性能优化参数
        self.target_fps = config.get('target_fps', 60)
        self.use_instancing = config.get('use_instancing', True)
        self.compress_textures = config.get('compress_textures', True)
        
        # 资源管理
        self.buffer_cache = {}
        self.uniform_cache = {}
        
    def initialize(self) -> bool:
        """初始化WebGL渲染器"""
        try:
            # 创建canvas元素
            if not self._create_canvas():
                return False
            
            # 初始化WebGL上下文
            if not self._init_webgl_context():
                return False
            
            # 加载着色器程序
            if not self._load_shader_programs():
                return False
            
            # 配置渲染状态
            self._configure_render_state()
            
            # 初始化资源缓存
            self._init_resource_caches()
            
            self.logger.info("WebGL渲染器初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"WebGL渲染器初始化失败: {e}")
            return False
    
    def _create_canvas(self) -> bool:
        """创建canvas元素"""
        try:
            from js import document
            
            # 创建或获取canvas元素
            canvas_id = self.config.get('canvas_id', 'scene-weaver-canvas')
            self.canvas = document.getElementById(canvas_id)
            
            if not self.canvas:
                self.canvas = document.createElement('canvas')
                self.canvas.id = canvas_id
                self.canvas.width = self.viewport_width
                self.canvas.height = self.viewport_height
                
                # 添加到文档中
                document.body.appendChild(self.canvas)
            
            self.logger.info(f"Canvas创建成功: {canvas_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Canvas创建失败: {e}")
            return False
    
    def _init_webgl_context(self) -> bool:
        """初始化WebGL上下文"""
        try:
            # 尝试WebGL 2.0
            self.gl_context = (self.canvas.getContext('webgl2') or 
                              self.canvas.getContext('experimental-webgl2'))
            
            if self.gl_context:
                self.webgl_version = 2
                self.logger.info("WebGL 2.0上下文初始化成功")
            else:
                # 回退到WebGL 1.0
                self.gl_context = (self.canvas.getContext('webgl') or 
                                  self.canvas.getContext('experimental-webgl'))
                if self.gl_context:
                    self.webgl_version = 1
                    self.logger.info("WebGL 1.0上下文初始化成功")
                else:
                    self.logger.error("无法创建WebGL上下文")
                    return False
            
            # 检查和加载扩展
            self._load_extensions()
            
            # 设置视口
            self.gl_context.viewport(0, 0, self.canvas.width, self.canvas.height)
            
            return True
            
        except Exception as e:
            self.logger.error(f"WebGL上下文初始化失败: {e}")
            return False
    
    def _load_extensions(self):
        """加载WebGL扩展"""
        extensions_to_load = [
            'OES_texture_float',
            'OES_texture_half_float',
            'WEBGL_compressed_texture_s3tc',
            'EXT_color_buffer_float',
            'WEBGL_debug_renderer_info'
        ]
        
        for ext_name in extensions_to_load:
            try:
                extension = self.gl_context.getExtension(ext_name)
                if extension:
                    self.extensions.append(ext_name)
                    self.logger.debug(f"扩展加载成功: {ext_name}")
            except Exception as e:
                self.logger.debug(f"扩展加载失败: {ext_name} - {e}")
    
    def _load_shader_programs(self) -> bool:
        """加载着色器程序"""
        try:
            # 基础着色器程序
            basic_program = self._create_shader_program(
                self._get_vertex_shader_source(),
                self._get_fragment_shader_source()
            )
            
            if basic_program:
                self.shader_programs['basic'] = basic_program
                self.current_program = basic_program
            
            # 粒子系统着色器
            particle_program = self._create_shader_program(
                self._get_particle_vertex_shader(),
                self._get_particle_fragment_shader()
            )
            
            if particle_program:
                self.shader_programs['particle'] = particle_program
            
            # 光照计算着色器
            lighting_program = self._create_shader_program(
                self._get_lighting_vertex_shader(),
                self._get_lighting_fragment_shader()
            )
            
            if lighting_program:
                self.shader_programs['lighting'] = lighting_program
            
            self.logger.info(f"着色器程序加载完成: {len(self.shader_programs)}个")
            return len(self.shader_programs) > 0
            
        except Exception as e:
            self.logger.error(f"着色器程序加载失败: {e}")
            return False
    
    def _create_shader_program(self, vertex_source: str, fragment_source: str):
        """创建着色器程序"""
        try:
            # 创建顶点着色器
            vertex_shader = self._compile_shader(vertex_source, 'VERTEX_SHADER')
            if not vertex_shader:
                return None
            
            # 创建片段着色器
            fragment_shader = self._compile_shader(fragment_source, 'FRAGMENT_SHADER')
            if not fragment_shader:
                return None
            
            # 创建程序对象
            program = self.gl_context.createProgram()
            self.gl_context.attachShader(program, vertex_shader)
            self.gl_context.attachShader(program, fragment_shader)
            self.gl_context.linkProgram(program)
            
            # 检查链接状态
            if not self.gl_context.getProgramParameter(program, 'LINK_STATUS'):
                error = self.gl_context.getProgramInfoLog(program)
                self.logger.error(f"着色器程序链接失败: {error}")
                return None
            
            return program
            
        except Exception as e:
            self.logger.error(f"着色器程序创建失败: {e}")
            return None
    
    def _compile_shader(self, source: str, shader_type: str):
        """编译着色器"""
        try:
            # 创建着色器对象
            shader = self.gl_context.createShader(getattr(self.gl_context, shader_type))
            self.gl_context.shaderSource(shader, source)
            self.gl_context.compileShader(shader)
            
            # 检查编译状态
            if not self.gl_context.getShaderParameter(shader, 'COMPILE_STATUS'):
                error = self.gl_context.getShaderInfoLog(shader)
                self.logger.error(f"{shader_type}编译失败: {error}")
                return None
            
            return shader
            
        except Exception as e:
            self.logger.error(f"着色器编译失败: {e}")
            return None
    
    def _get_vertex_shader_source(self) -> str:
        """获取顶点着色器源码"""
        if self.webgl_version == 2:
            version_directive = "#version 300 es"
            attribute_keyword = "in"
            varying_keyword = "out"
        else:
            version_directive = ""
            attribute_keyword = "attribute"
            varying_keyword = "varying"
        
        return f"""{version_directive}
        precision mediump float;
        
        {attribute_keyword} vec3 a_position;
        {attribute_keyword} vec3 a_normal;
        {attribute_keyword} vec2 a_texcoord;
        
        uniform mat4 u_model_view_matrix;
        uniform mat4 u_projection_matrix;
        uniform mat3 u_normal_matrix;
        
        {varying_keyword} vec3 v_normal;
        {varying_keyword} vec2 v_texcoord;
        {varying_keyword} vec3 v_position;
        
        void main() {{
            vec4 position = u_model_view_matrix * vec4(a_position, 1.0);
            v_position = position.xyz;
            v_normal = u_normal_matrix * a_normal;
            v_texcoord = a_texcoord;
            gl_Position = u_projection_matrix * position;
        }}
        """
    
    def _get_fragment_shader_source(self) -> str:
        """获取片段着色器源码"""
        if self.webgl_version == 2:
            version_directive = "#version 300 es"
            varying_keyword = "in"
            frag_color = "out vec4 fragColor;"
            texture_func = "texture"
        else:
            version_directive = ""
            varying_keyword = "varying"
            frag_color = ""
            texture_func = "texture2D"
        
        return f"""{version_directive}
        precision mediump float;
        
        {frag_color}
        {varying_keyword} vec3 v_normal;
        {varying_keyword} vec2 v_texcoord;
        {varying_keyword} vec3 v_position;
        
        uniform vec3 u_light_position;
        uniform vec3 u_light_color;
        uniform vec3 u_ambient_color;
        uniform sampler2D u_texture;
        uniform bool u_use_texture;
        
        void main() {{
            vec3 normal = normalize(v_normal);
            vec3 light_dir = normalize(u_light_position - v_position);
            float diffuse = max(dot(normal, light_dir), 0.0);
            
            vec3 ambient = u_ambient_color;
            vec3 diffuse_light = u_light_color * diffuse;
            
            vec3 final_color = ambient + diffuse_light;
            
            if (u_use_texture) {{
                vec4 tex_color = {texture_func}(u_texture, v_texcoord);
                final_color *= tex_color.rgb;
            }}
            
            {'fragColor = vec4(final_color, 1.0);' if self.webgl_version == 2 else 'gl_FragColor = vec4(final_color, 1.0);'}
        }}
        """
    
    def _get_particle_vertex_shader(self) -> str:
        """获取粒子系统顶点着色器"""
        # 简化的粒子顶点着色器
        return """
        precision mediump float;
        attribute vec3 a_position;
        attribute vec4 a_color;
        attribute float a_size;
        
        uniform mat4 u_model_view_matrix;
        uniform mat4 u_projection_matrix;
        
        varying vec4 v_color;
        
        void main() {
            v_color = a_color;
            gl_PointSize = a_size;
            gl_Position = u_projection_matrix * u_model_view_matrix * vec4(a_position, 1.0);
        }
        """
    
    def _get_particle_fragment_shader(self) -> str:
        """获取粒子系统片段着色器"""
        return """
        precision mediump float;
        varying vec4 v_color;
        
        void main() {
            float distance = length(gl_PointCoord - vec2(0.5));
            if (distance > 0.5) discard;
            gl_FragColor = v_color;
        }
        """
    
    def _get_lighting_vertex_shader(self) -> str:
        """获取光照计算顶点着色器"""
        return self._get_vertex_shader_source()  # 复用基础顶点着色器
    
    def _get_lighting_fragment_shader(self) -> str:
        """获取光照计算片段着色器"""
        return self._get_fragment_shader_source()  # 复用基础片段着色器
    
    def _configure_render_state(self):
        """配置渲染状态"""
        try:
            gl = self.gl_context
            
            # 设置清除颜色
            gl.clearColor(*self.clear_color)
            
            # 启用深度测试
            gl.enable(gl.DEPTH_TEST)
            gl.depthFunc(gl.LEQUAL)
            
            # 启用面剔除
            gl.enable(gl.CULL_FACE)
            gl.cullFace(gl.BACK)
            
            # 启用混合
            gl.enable(gl.BLEND)
            gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA)
            
            self.logger.info("渲染状态配置完成")
            
        except Exception as e:
            self.logger.error(f"渲染状态配置失败: {e}")
    
    def _init_resource_caches(self):
        """初始化资源缓存"""
        # 预编译常用着色器变体
        self._precompile_shader_variants()
        
        # 初始化纹理单元
        self._init_texture_units()
        
        self.logger.info("资源缓存初始化完成")
    
    def _precompile_shader_variants(self):
        """预编译着色器变体"""
        # 这里可以预编译不同的着色器配置
        pass
    
    def _init_texture_units(self):
        """初始化纹理单元"""
        max_texture_units = self.gl_context.getParameter(self.gl_context.MAX_TEXTURE_IMAGE_UNITS)
        for i in range(min(max_texture_units, 8)):  # 限制使用前8个纹理单元
            self.texture_units[i] = None
    
    def begin_frame(self) -> bool:
        """开始渲染帧"""
        try:
            gl = self.gl_context
            
            # 清除缓冲区
            gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT)
            
            # 设置视口
            gl.viewport(0, 0, self.canvas.width, self.canvas.height)
            
            return True
            
        except Exception as e:
            self.logger.error(f"开始渲染帧失败: {e}")
            return False
    
    def render_geometry(self, vertices, indices, texture=None, program_name='basic'):
        """渲染几何体"""
        try:
            gl = self.gl_context
            
            # 选择着色器程序
            program = self.shader_programs.get(program_name, self.current_program)
            if not program:
                return False
            
            gl.useProgram(program)
            
            # 设置顶点属性
            self._setup_vertex_attributes(program, vertices)
            
            # 设置索引缓冲区
            self._setup_index_buffer(indices)
            
            # 设置纹理（如果提供）
            if texture:
                self._bind_texture(texture, program)
            
            # 绘制几何体
            gl.drawElements(gl.TRIANGLES, len(indices), gl.UNSIGNED_SHORT, 0)
            
            return True
            
        except Exception as e:
            self.logger.error(f"渲染几何体失败: {e}")
            return False
    
    def _setup_vertex_attributes(self, program, vertices):
        """设置顶点属性"""
        gl = self.gl_context
        
        # 创建或获取顶点缓冲区
        buffer_key = f"vertex_buffer_{hash(vertices.tobytes())}"
        if buffer_key not in self.buffer_cache:
            buffer = gl.createBuffer()
            gl.bindBuffer(gl.ARRAY_BUFFER, buffer)
            gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW)
            self.buffer_cache[buffer_key] = buffer
        else:
            buffer = self.buffer_cache[buffer_key]
            gl.bindBuffer(gl.ARRAY_BUFFER, buffer)
        
        # 设置位置属性
        position_loc = gl.getAttribLocation(program, 'a_position')
        if position_loc >= 0:
            gl.enableVertexAttribArray(position_loc)
            gl.vertexAttribPointer(position_loc, 3, gl.FLOAT, False, 32, 0)
        
        # 设置法线属性
        normal_loc = gl.getAttribLocation(program, 'a_normal')
        if normal_loc >= 0:
            gl.enableVertexAttribArray(normal_loc)
            gl.vertexAttribPointer(normal_loc, 3, gl.FLOAT, False, 32, 12)
        
        # 设置纹理坐标属性
        texcoord_loc = gl.getAttribLocation(program, 'a_texcoord')
        if texcoord_loc >= 0:
            gl.enableVertexAttribArray(texcoord_loc)
            gl.vertexAttribPointer(texcoord_loc, 2, gl.FLOAT, False, 32, 24)
    
    def _setup_index_buffer(self, indices):
        """设置索引缓冲区"""
        gl = self.gl_context
        
        # 创建或获取索引缓冲区
        buffer_key = f"index_buffer_{hash(indices.tobytes())}"
        if buffer_key not in self.buffer_cache:
            buffer = gl.createBuffer()
            gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, buffer)
            gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, indices, gl.STATIC_DRAW)
            self.buffer_cache[buffer_key] = buffer
        else:
            buffer = self.buffer_cache[buffer_key]
            gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, buffer)
    
    def _bind_texture(self, texture_data, program):
        """绑定纹理"""
        gl = self.gl_context
        
        # 创建或获取纹理
        texture_key = f"texture_{id(texture_data)}"
        if texture_key not in self.textures:
            texture = gl.createTexture()
            gl.bindTexture(gl.TEXTURE_2D, texture)
            
            # 设置纹理参数
            gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE)
            gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE)
            gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR)
            gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR)
            
            # 上传纹理数据（这里需要实际的图像数据处理）
            # gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, width, height, 0, gl.RGBA, gl.UNSIGNED_BYTE, image_data)
            
            self.textures[texture_key] = texture
        else:
            texture = self.textures[texture_key]
            gl.bindTexture(gl.TEXTURE_2D, texture)
        
        # 设置着色器中的纹理uniform
        texture_loc = gl.getUniformLocation(program, 'u_texture')
        if texture_loc >= 0:
            gl.uniform1i(texture_loc, 0)  # 使用纹理单元0
    
    def end_frame(self):
        """结束渲染帧"""
        # WebGL会自动交换缓冲区
        pass
    
    def resize(self, width: int, height: int):
        """调整渲染区域大小"""
        try:
            self.viewport_width = width
            self.viewport_height = height
            
            if self.canvas:
                self.canvas.width = width
                self.canvas.height = height
            
            if self.gl_context:
                self.gl_context.viewport(0, 0, width, height)
            
            self.logger.info(f"渲染区域调整为: {width}x{height}")
            
        except Exception as e:
            self.logger.error(f"调整渲染区域失败: {e}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        try:
            gl = self.gl_context
            ext = gl.getExtension('WEBGL_debug_renderer_info')
            
            vendor = gl.getParameter(gl.VENDOR) if ext else "Unknown"
            renderer = gl.getParameter(gl.RENDERER) if ext else "Unknown"
            
            return {
                'webgl_version': self.webgl_version,
                'vendor': vendor,
                'renderer': renderer,
                'viewport_size': (self.viewport_width, self.viewport_height),
                'extensions_loaded': len(self.extensions),
                'shader_programs': len(self.shader_programs),
                'textures_loaded': len(self.textures),
                'target_fps': self.target_fps,
                'use_instancing': self.use_instancing
            }
        except Exception as e:
            self.logger.warning(f"性能统计获取失败: {e}")
            return {}
    
    def cleanup(self):
        """清理渲染器资源"""
        try:
            gl = self.gl_context
            
            # 删除着色器程序
            for program in self.shader_programs.values():
                gl.deleteProgram(program)
            
            # 删除缓冲区
            for buffer in self.buffer_cache.values():
                gl.deleteBuffer(buffer)
            
            # 删除纹理
            for texture in self.textures.values():
                gl.deleteTexture(texture)
            
            self.shader_programs.clear()
            self.buffer_cache.clear()
            self.textures.clear()
            self.texture_units.clear()
            
            self.gl_context = None
            self.canvas = None
            
            self.logger.info("WebGL渲染器资源清理完成")
            
        except Exception as e:
            self.logger.error(f"WebGL渲染器清理失败: {e}")