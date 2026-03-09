"""
Web Build Configuration - Web构建配置
SceneWeaver Web平台的构建和部署配置
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any


class WebBuildConfig:
    """Web构建配置类"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.web_dir = Path(__file__).parent
        
        # 构建配置
        self.build_config = {
            'app_name': 'SceneWeaver',
            'version': '1.0.0',
            'target': 'web',
            
            # 构建选项
            'bundler': 'webpack',  # webpack, rollup, parcel
            'transpiler': 'brython',  # brython, pyodide, skulpt
            'minify': True,
            'source_maps': True,
            
            # 输出配置
            'output_dir': 'dist/web',
            'public_path': '/',
            'asset_prefix': '',
            
            # 优化选项
            'split_chunks': True,
            'tree_shaking': True,
            'compression': 'gzip',
            
            # 服务配置
            'dev_server': {
                'port': 8080,
                'host': 'localhost',
                'hot_reload': True,
                'proxy': {}
            },
            
            # 部署配置
            'deployment': {
                'target': 'static',  # static, serverless, docker
                'cdn': True,
                'pwa': True,
                'service_worker': True
            }
        }
    
    def generate_package_json(self) -> Dict[str, Any]:
        """生成package.json配置"""
        return {
            "name": self.build_config['app_name'].lower().replace(' ', '-'),
            "version": self.build_config['version'],
            "description": "AIGC实景导演Web版本",
            "main": "index.js",
            "scripts": {
                "build": "webpack --mode production",
                "dev": "webpack serve --mode development",
                "preview": "python -m http.server 8080 --directory dist/web",
                "deploy": "npm run build && gh-pages -d dist/web"
            },
            "dependencies": {
                "brython": "^3.12.0",
                "three": "^0.150.0",  # 备用3D库
                "lodash": "^4.17.21"
            },
            "devDependencies": {
                "webpack": "^5.75.0",
                "webpack-cli": "^5.0.0",
                "webpack-dev-server": "^4.11.0",
                "css-loader": "^6.7.0",
                "style-loader": "^3.3.0",
                "file-loader": "^6.2.0",
                "html-webpack-plugin": "^5.5.0",
                "copy-webpack-plugin": "^11.0.0",
                "gh-pages": "^4.0.0"
            },
            "browserslist": [
                "> 1%",
                "last 2 versions",
                "not dead"
            ]
        }
    
    def generate_webpack_config(self) -> str:
        """生成Webpack配置文件"""
        config = f"""
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = {{
    entry: {{
        main: './src/platform/web/index.js',
        brython: 'brython',
        'brython_stdlib': 'brython_stdlib'
    }},
    
    output: {{
        path: path.resolve(__dirname, '{self.build_config['output_dir']}'),
        filename: '[name].[contenthash].js',
        publicPath: '{self.build_config['public_path']}',
        clean: true
    }},
    
    module: {{
        rules: [
            {{
                test: /\\.css$/,
                use: ['style-loader', 'css-loader']
            }},
            {{
                test: /\\.py$/,
                use: 'raw-loader'
            }},
            {{
                test: /\\.(png|jpg|gif|svg)$/,
                type: 'asset/resource'
            }}
        ]
    }},
    
    plugins: [
        new HtmlWebpackPlugin({{
            template: './src/platform/web/index.html',
            filename: 'index.html',
            inject: 'body'
        }}),
        
        new CopyWebpackPlugin({{
            patterns: [
                {{ from: 'assets', to: 'assets' }},
                {{ from: 'models', to: 'models' }},
                {{ from: 'src/**/*.py', to: '[path][name][ext]' }}
            ]
        }})
    ],
    
    devServer: {{
        host: '{self.build_config['dev_server']['host']}',
        port: {self.build_config['dev_server']['port']},
        hot: {str(self.build_config['dev_server']['hot_reload']).lower()},
        open: true,
        historyApiFallback: true,
        static: {{
            directory: path.join(__dirname, 'public')
        }}
    }},
    
    optimization: {{
        splitChunks: {{
            chunks: 'all',
            cacheGroups: {{
                vendor: {{
                    test: /[\\\\/]node_modules[\\\\/]/,
                    name: 'vendors',
                    chunks: 'all'
                }}
            }}
        }}
    }},
    
    resolve: {{
        extensions: ['.js', '.py', '.json'],
        alias: {{
            '@': path.resolve(__dirname, 'src')
        }}
    }},
    
    mode: process.env.NODE_ENV === 'production' ? 'production' : 'development',
    
    devtool: process.env.NODE_ENV === 'production' ? 'source-map' : 'eval-source-map'
}};
"""
        return config
    
    def generate_html_template(self) -> str:
        """生成HTML模板"""
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="AIGC实景导演 - 基于Web的实时混合现实创作系统">
    <title>{self.build_config['app_name']}</title>
    
    <!-- PWA配置 -->
    <link rel="manifest" href="/manifest.json">
    <link rel="apple-touch-icon" href="/icons/icon-192x192.png">
    <meta name="theme-color" content="#2196F3">
    
    <!-- Brython配置 -->
    <script type="text/javascript" src="/brython.js"></script>
    <script type="text/javascript" src="/brython_stdlib.js"></script>
    
    <!-- 应用样式 -->
    <style>
        body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            background-color: #000;
            font-family: Arial, sans-serif;
        }}
        
        #scene-weaver-canvas {{
            display: block;
            width: 100vw;
            height: 100vh;
        }}
        
        #loading-screen {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: #000;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
            z-index: 1000;
        }}
        
        .spinner {{
            width: 50px;
            height: 50px;
            border: 5px solid #333;
            border-top: 5px solid #2196F3;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        /* 响应式设计 */
        @media (max-width: 768px) {{
            #scene-weaver-canvas {{
                touch-action: none;
            }}
        }}
    </style>
</head>
<body>
    <!-- 加载屏幕 -->
    <div id="loading-screen">
        <div class="spinner"></div>
        <div>正在加载 {self.build_config['app_name']}...</div>
        <div id="loading-progress">0%</div>
    </div>
    
    <!-- 主要Canvas -->
    <canvas id="scene-weaver-canvas"></canvas>
    
    <!-- Brython应用入口 -->
    <script type="text/python" src="/src/platform/web/main.py"></script>
    
    <!-- 初始化脚本 -->
    <script>
        // 隐藏加载屏幕
        function hideLoadingScreen() {{
            const loadingScreen = document.getElementById('loading-screen');
            if (loadingScreen) {{
                loadingScreen.style.opacity = '0';
                setTimeout(() => {{
                    loadingScreen.style.display = 'none';
                }}, 500);
            }}
        }}
        
        // 更新加载进度
        function updateLoadingProgress(progress) {{
            const progressElement = document.getElementById('loading-progress');
            if (progressElement) {{
                progressElement.textContent = Math.round(progress) + '%';
            }}
        }}
        
        // Brython初始化完成后
        document.addEventListener('DOMContentLoaded', function() {{
            brython({{debug: 1, pythonpath: ['/src']}});
        }});
        
        // 错误处理
        window.addEventListener('error', function(e) {{
            console.error('应用错误:', e.error);
            // 可以在这里显示错误信息给用户
        }});
    </script>
</body>
</html>
"""
        return html_content
    
    def generate_service_worker(self) -> str:
        """生成Service Worker"""
        sw_content = f"""// Service Worker for {self.build_config['app_name']}
const CACHE_NAME = '{self.build_config['app_name'].lower()}-v{self.build_config['version']}';
const urlsToCache = [
    '/',
    '/index.html',
    '/brython.js',
    '/brython_stdlib.js',
    '/src/platform/web/main.py',
    // 这里可以添加更多需要缓存的资源
];

self.addEventListener('install', function(event) {{
    // 预缓存重要资源
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {{
                return cache.addAll(urlsToCache);
            }})
    );
}});

self.addEventListener('fetch', function(event) {{
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {{
                // 缓存命中则返回缓存，否则发起网络请求
                return response || fetch(event.request);
            }}
        )
    );
}});

self.addEventListener('activate', function(event) {{
    // 清理旧缓存
    event.waitUntil(
        caches.keys().then(function(cacheNames) {{
            return Promise.all(
                cacheNames.map(function(cacheName) {{
                    if (cacheName !== CACHE_NAME) {{
                        return caches.delete(cacheName);
                    }}
                }})
            );
        }})
    );
}});
"""
        return sw_content
    
    def generate_manifest_json(self) -> str:
        """生成Web App Manifest"""
        manifest = {
            "name": self.build_config['app_name'],
            "short_name": "SceneWeaver",
            "description": "AIGC实景导演 - 实时混合现实创作系统",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#000000",
            "theme_color": "#2196F3",
            "icons": [
                {
                    "src": "/icons/icon-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                },
                {
                    "src": "/icons/icon-512x512.png",
                    "sizes": "512x512",
                    "type": "image/png"
                }
            ]
        }
        return json.dumps(manifest, indent=2, ensure_ascii=False)
    
    def create_build_scripts(self):
        """创建构建脚本"""
        # 创建package.json
        package_json = self.generate_package_json()
        package_path = self.project_root / 'package.json'
        with open(package_path, 'w', encoding='utf-8') as f:
            json.dump(package_json, f, indent=2, ensure_ascii=False)
        
        # 创建webpack.config.js
        webpack_config = self.generate_webpack_config()
        webpack_path = self.project_root / 'webpack.config.js'
        with open(webpack_path, 'w', encoding='utf-8') as f:
            f.write(webpack_config)
        
        # 创建HTML模板
        html_template = self.generate_html_template()
        html_path = self.web_dir / 'index.html'
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        # 创建Service Worker
        service_worker = self.generate_service_worker()
        sw_path = self.web_dir / 'sw.js'
        with open(sw_path, 'w', encoding='utf-8') as f:
            f.write(service_worker)
        
        # 创建Manifest
        manifest_json = self.generate_manifest_json()
        manifest_path = self.web_dir / 'manifest.json'
        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write(manifest_json)
        
        # 创建构建脚本
        self._create_build_script()
        
        return {
            'package_json': package_path,
            'webpack_config': webpack_path,
            'html_template': html_path,
            'service_worker': sw_path,
            'manifest': manifest_path
        }
    
    def _create_build_script(self):
        """创建构建脚本"""
        build_script = f"""#!/bin/bash
# SceneWeaver Web构建脚本

echo "开始构建SceneWeaver Web应用..."

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js"
    echo "请安装Node.js LTS版本"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "错误: 未找到npm"
    exit 1
fi

# 安装依赖
echo "安装项目依赖..."
npm install

# 构建生产版本
echo "构建生产版本..."
npm run build

# 检查构建结果
if [ -d "dist/web" ]; then
    echo "构建成功！文件位于: dist/web"
    
    # 可选：启动本地预览服务器
    echo "启动本地预览服务器..."
    npm run preview &
    
    echo "Web应用构建完成！"
    echo "访问地址: http://localhost:8080"
else
    echo "构建失败！请检查错误信息。"
    exit 1
fi
"""
        
        script_path = self.project_root / 'build_web.sh'
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(build_script)
        
        # 设置执行权限
        if os.name != 'nt':
            os.chmod(script_path, 0o755)
        
        # 创建Windows批处理脚本
        bat_script = """@echo off
REM SceneWeaver Web构建脚本 (Windows)

echo 开始构建SceneWeaver Web应用...

REM 检查Node.js环境
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Node.js
    echo 请安装Node.js LTS版本
    exit /b 1
)

npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到npm
    exit /b 1
)

REM 安装依赖
echo 安装项目依赖...
npm install

REM 构建生产版本
echo 构建生产版本...
npm run build

REM 检查构建结果
if exist "dist\\web" (
    echo 构建成功！文件位于: dist\\web
    
    REM 启动本地预览服务器
    echo 启动本地预览服务器...
    start npm run preview
    
    echo Web应用构建完成！
    echo 访问地址: http://localhost:8080
) else (
    echo 构建失败！请检查错误信息。
    exit /b 1
)
"""
        
        bat_path = self.project_root / 'build_web.bat'
        with open(bat_path, 'w', encoding='utf-8') as f:
            f.write(bat_script)
    
    def generate_docker_config(self) -> Dict[str, Any]:
        """生成Docker配置"""
        return {
            'dockerfile': """FROM nginx:alpine

# 复制构建文件
COPY dist/web /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]
""",
            'nginx_conf': """events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    sendfile        on;
    tcp_nopush      on;
    tcp_nodelay     on;
    keepalive_timeout  65;
    types_hash_max_size 2048;
    
    server {
        listen       80;
        server_name  localhost;
        
        location / {
            root   /usr/share/nginx/html;
            index  index.html;
            try_files $uri $uri/ /index.html;
        }
        
        # 启用gzip压缩
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    }
}
"""
        }
    
    def get_build_info(self) -> Dict[str, Any]:
        """获取构建信息"""
        return {
            'app_name': self.build_config['app_name'],
            'version': self.build_config['version'],
            'target': self.build_config['target'],
            'bundler': self.build_config['bundler'],
            'transpiler': self.build_config['transpiler'],
            'output_dir': self.build_config['output_dir'],
            'dev_server_port': self.build_config['dev_server']['port']
        }


# 构建辅助函数
def setup_web_development_environment():
    """设置Web开发环境"""
    print("设置Web开发环境...")
    
    # 检查必要的工具
    required_tools = ['node', 'npm']
    missing_tools = []
    
    for tool in required_tools:
        if os.system(f"which {tool}") != 0:
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"缺少以下工具: {', '.join(missing_tools)}")
        print("请安装Node.js和npm后再进行构建。")
        return False
    
    # 检查Node.js版本
    import subprocess
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"Node.js版本: {version}")
        
        # 检查版本是否符合要求
        if version.startswith('v') and int(version[1:].split('.')[0]) < 14:
            print("警告: 建议使用Node.js 14+版本")
    except Exception as e:
        print(f"检查Node.js版本失败: {e}")
    
    print("Web开发环境检查通过")
    return True


def build_web_app():
    """构建Web应用"""
    config = WebBuildConfig()
    
    if not setup_web_development_environment():
        return False
    
    print("生成构建配置文件...")
    config_files = config.create_build_scripts()
    
    for name, path in config_files.items():
        print(f"{name}: {path}")
    
    print("开始构建过程...")
    # 这里应该调用实际的构建命令
    # os.system("./build_web.sh")  # Linux/Mac
    # os.system("build_web.bat")   # Windows
    
    print("Web应用构建配置完成")
    return True


if __name__ == '__main__':
    build_web_app()