# SceneWeaver Web平台开发指南

## 概述

本文档详细介绍SceneWeaver在Web平台上的开发、构建和部署流程，包括WebGL渲染支持、响应式界面设计和云端部署方案。

## 系统架构

### Web平台适配层
```
SceneWeaver Core
    ↓
Web Platform Adapter
    ├── WebPlatform (平台检测和基础适配)
    ├── WebGLRendererAdapter (WebGL渲染适配器)
    ├── WebInputHandler (Web输入处理)
    └── WebSceneWeaver (Web主应用入口)
    ↓
Web APIs/Browser Runtime
```

### 主要组件

1. **WebPlatform** - Web平台检测和基础适配
2. **WebGLRendererAdapter** - WebGL图形API集成和优化
3. **WebInputHandler** - Web输入处理（鼠标、键盘、触摸）
4. **WebSceneWeaver** - Web主应用入口和生命周期管理

## 开发环境设置

### 系统要求
- **Node.js**: 14.0+ LTS版本
- **npm**: 6.0+ 或 yarn 1.22+
- **Python**: 3.8+ (用于Brython)
- **现代浏览器**: Chrome 80+, Firefox 75+, Safari 13+

### 必需工具安装

#### 1. Node.js和npm
```bash
# 下载并安装Node.js LTS
# https://nodejs.org/

# 验证安装
node --version
npm --version
```

#### 2. Python环境（可选，用于本地开发）
```bash
# 安装Python 3.8+
# 确保pip可用

# 安装开发依赖
pip install -r requirements.txt
```

#### 3. 开发工具
```bash
# 全局安装开发工具
npm install -g webpack webpack-cli webpack-dev-server

# 安装项目依赖
npm install
```

## 项目结构

```
src/platform/web/
├── __init__.py              # Web平台检测和基础类
├── main.py                  # Web主程序入口
├── webgl_renderer.py        # WebGL渲染适配器
├── input_handler.py         # Web输入处理
├── build_config.py          # 构建配置生成器
└── assets/                  # Web特定资源
    ├── index.html          # HTML模板
    ├── sw.js               # Service Worker
    ├── manifest.json       # PWA配置
    └── icons/              # 应用图标
```

## WebGL渲染集成

### WebGL渲染适配器特性

#### 1. 多版本WebGL支持
```python
class WebGLRendererAdapter:
    def _init_webgl_context(self) -> bool:
        # 优先尝试WebGL 2.0
        self.gl_context = (self.canvas.getContext('webgl2') or 
                          self.canvas.getContext('experimental-webgl2'))
        
        if self.gl_context:
            self.webgl_version = 2
        else:
            # 回退到WebGL 1.0
            self.gl_context = (self.canvas.getContext('webgl') or 
                              self.canvas.getContext('experimental-webgl'))
            self.webgl_version = 1
```

#### 2. 着色器程序管理
```python
def _load_shader_programs(self) -> bool:
    # 基础渲染着色器
    basic_program = self._create_shader_program(
        self._get_vertex_shader_source(),
        self._get_fragment_shader_source()
    )
    
    # 粒子系统着色器
    particle_program = self._create_shader_program(
        self._get_particle_vertex_shader(),
        self._get_particle_fragment_shader()
    )
    
    # 光照计算着色器
    lighting_program = self._create_shader_program(
        self._get_lighting_vertex_shader(),
        self._get_lighting_fragment_shader()
    )
```

#### 3. 性能优化特性
```python
# 资源缓存管理
def _init_resource_caches(self):
    self._precompile_shader_variants()
    self._init_texture_units()

# 实例化渲染支持
@property
def use_instancing(self):
    return self.config.get('use_instancing', True)
```

## 输入处理系统

### Web输入处理特性

#### 1. 多输入设备支持
```python
class WebInputHandler:
    def _bind_canvas_events(self):
        # 鼠标事件
        self.canvas.addEventListener('mousedown', self._on_mouse_down)
        self.canvas.addEventListener('mouseup', self._on_mouse_up)
        self.canvas.addEventListener('mousemove', self._on_mouse_move)
        self.canvas.addEventListener('wheel', self._on_mouse_wheel)
        
        # 触摸事件
        self.canvas.addEventListener('touchstart', self._on_touch_start)
        self.canvas.addEventListener('touchmove', self._on_touch_move)
        self.canvas.addEventListener('touchend', self._on_touch_end)
```

#### 2. 事件标准化处理
```python
def _on_mouse_move(self, event):
    input_event = InputEvent(
        event_type=InputEventType.MOUSE_MOVE,
        x=event.clientX,
        y=event.clientY,
        buttons=event.buttons,
        pointer_type=PointerType.MOUSE,
        timestamp=event.timeStamp
    )
    
    self.mouse_position = (event.clientX, event.clientY)
    self._trigger_callbacks(input_event)
```

#### 3. 响应式设计支持
```python
def _should_prevent_key(self, event):
    # 防止方向键影响页面滚动
    prevent_keys = ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' ', 'Spacebar']
    return event.key in prevent_keys
```

## 构建和部署

### 1. 生成构建配置
```python
from platform.web.build_config import WebBuildConfig

config = WebBuildConfig()
config_files = config.create_build_scripts()
```

### 2. 开发模式构建
```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问应用
# http://localhost:8080
```

### 3. 生产模式构建
```bash
# 构建生产版本
npm run build

# 预览构建结果
npm run preview

# 部署到GitHub Pages
npm run deploy
```

## Web特定配置

### package.json配置
```json
{
  "name": "scene-weaver-web",
  "scripts": {
    "build": "webpack --mode production",
    "dev": "webpack serve --mode development",
    "preview": "python -m http.server 8080 --directory dist/web"
  },
  "dependencies": {
    "brython": "^3.12.0"
  }
}
```

### Webpack配置要点
```javascript
module.exports = {
    entry: {
        main: './src/platform/web/index.js',
        brython: 'brython',
        'brython_stdlib': 'brython_stdlib'
    },
    
    module: {
        rules: [
            {
                test: /\.py$/,
                use: 'raw-loader'  // 处理Python文件
            }
        ]
    }
};
```

## PWA和离线支持

### Service Worker配置
```javascript
// sw.js
const CACHE_NAME = 'scene-weaver-v1.0.0';
const urlsToCache = [
    '/',
    '/index.html',
    '/brython.js',
    '/src/platform/web/main.py'
];

self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                return cache.addAll(urlsToCache);
            })
    );
});
```

### Web App Manifest
```json
{
  "name": "SceneWeaver",
  "short_name": "SceneWeaver",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#000000",
  "theme_color": "#2196F3"
}
```

## 性能优化指南

### 1. WebGL性能优化
```python
# 纹理压缩
def _bind_texture(self, texture_data, program):
    # 使用压缩纹理格式
    if self.compress_textures:
        # 实现纹理压缩逻辑
        pass

# 批量渲染
def render_batch(self, objects):
    # 合并相似的渲染调用
    # 减少状态切换
    pass
```

### 2. 资源管理优化
```python
# 智能缓存策略
class ResourceCache:
    def __init__(self):
        self.lru_cache = {}
        self.max_size = 100
    
    def get_or_create(self, key, factory):
        if key in self.lru_cache:
            return self.lru_cache[key]
        
        resource = factory()
        if len(self.lru_cache) >= self.max_size:
            # 移除最少使用的资源
            oldest_key = next(iter(self.lru_cache))
            del self.lru_cache[oldest_key]
        
        self.lru_cache[key] = resource
        return resource
```

### 3. 帧率控制
```python
# 基于requestAnimationFrame的渲染循环
def _start_render_loop(self):
    def render_frame(timestamp):
        try:
            # 更新和渲染逻辑
            self.core_engine.update(1/60)
            self.core_engine.render()
            
            # 请求下一帧
            self.window.requestAnimationFrame(render_frame)
        except Exception as e:
            self.logger.error(f"渲染帧失败: {e}")
    
    self.window.requestAnimationFrame(render_frame)
```

## 调试和测试

### 1. 浏览器开发者工具
```javascript
// 启用详细的错误日志
document.addEventListener('DOMContentLoaded', function() {
    brython({debug: 1, pythonpath: ['/src']});
});

// 错误处理
window.addEventListener('error', function(e) {
    console.error('应用错误:', e.error);
});
```

### 2. 性能监控
```python
def get_performance_stats(self) -> Dict[str, Any]:
    return {
        'webgl_version': self.webgl_version,
        'vendor': self.gl_context.getParameter(self.gl_context.VENDOR),
        'renderer': self.gl_context.getParameter(self.gl_context.RENDERER),
        'viewport_size': (self.viewport_width, self.viewport_height),
        'extensions_loaded': len(self.extensions)
    }
```

### 3. 移动设备测试
```html
<!-- 响应式设计测试 -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
@media (max-width: 768px) {
    #scene-weaver-canvas {
        touch-action: none;  /* 禁用默认触摸行为 */
    }
}
</style>
```

## 部署方案

### 1. 静态网站部署
```bash
# GitHub Pages
npm run deploy

# Netlify
# 连接Git仓库，自动部署

# Vercel
vercel --prod
```

### 2. Docker部署
```dockerfile
FROM nginx:alpine
COPY dist/web /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 3. CDN优化
```javascript
// webpack.config.js
module.exports = {
    optimization: {
        splitChunks: {
            chunks: 'all',
            cacheGroups: {
                vendor: {
                    test: /[\\/]node_modules[\\/]/,
                    name: 'vendors',
                    chunks: 'all'
                }
            }
        }
    }
};
```

## 常见问题解决

### 1. WebGL初始化失败
```javascript
// 降级处理
if (!gl) {
    // 尝试WebGL 1.0
    gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    
    if (!gl) {
        // 使用Canvas 2D作为后备
        const ctx2d = canvas.getContext('2d');
        // 实现2D渲染后备方案
    }
}
```

### 2. 移动设备性能问题
```python
# 动态质量调整
def adjust_quality_for_device(self, device_info):
    if device_info.get('is_mobile'):
        self.target_fps = 30
        self.use_instancing = False
        self.compress_textures = True
```

### 3. 跨域资源共享
```javascript
// webpack-dev-server配置
devServer: {
    headers: {
        'Access-Control-Allow-Origin': '*'
    }
}
```

## 最佳实践

### 1. 代码组织
```python
# 模块化设计
# 分离关注点
# 使用TypeScript类型检查（通过Pyright等工具）
```

### 2. 用户体验
```html
<!-- 渐进式加载 -->
<div id="loading-screen">
    <div class="spinner"></div>
    <div>正在加载...</div>
</div>

<script>
// 平滑的加载过渡
function hideLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    loadingScreen.style.opacity = '0';
    setTimeout(() => {
        loadingScreen.style.display = 'none';
    }, 500);
}
</script>
```

### 3. 可访问性
```html
<!-- 键盘导航支持 -->
<button aria-label="全屏切换" onclick="toggleFullscreen()">
    <svg><!-- 全屏图标 --></svg>
</button>

<!-- 屏幕阅读器支持 -->
<div role="status" aria-live="polite" id="status-message"></div>
```

## 未来扩展方向

### 计划功能
- [ ] WebGPU支持
- [ ] WebXR (VR/AR)集成
- [ ] 多人协作功能
- [ ] 云端渲染支持
- [ ] PWA高级功能

### 技术升级
- [ ] 更先进的着色器编译
- [ ] 实时代码编辑器
- [ ] 性能分析工具集成
- [ ] 自动化测试框架

---

**版本**: 1.0.0  
**最后更新**: 2026年2月  
**作者**: SceneWeaver开发团队