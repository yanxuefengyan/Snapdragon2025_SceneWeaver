"""
Android Build Configuration - Android构建配置
SceneWeaver Android平台的构建和打包配置
"""

import os
from pathlib import Path
from typing import Dict, List, Any


class AndroidBuildConfig:
    """Android构建配置类"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.android_dir = Path(__file__).parent
        
        # 构建配置
        self.build_config = {
            'app_name': 'SceneWeaver',
            'package_name': 'com.scene.weaver',
            'version_code': 1,
            'version_name': '1.0.0',
            'min_sdk': 21,  # Android 5.0
            'target_sdk': 33,  # Android 13
            'compile_sdk': 33,
            
            # 应用权限
            'permissions': [
                'INTERNET',
                'CAMERA',
                'WRITE_EXTERNAL_STORAGE',
                'READ_EXTERNAL_STORAGE',
                'VIBRATE'
            ],
            
            # 架构支持
            'architectures': ['armeabi-v7a', 'arm64-v8a', 'x86', 'x86_64'],
            
            # Python相关
            'python_version': '3.12',
            'requirements': [
                'pygame',
                'numpy',
                'pillow',
                'opencv-python',
                'pyyaml'
            ]
        }
    
    def generate_buildozer_spec(self) -> str:
        """生成Buildozer配置文件"""
        spec_content = f"""[app]
title = {self.build_config['app_name']}
package.name = scene_weaver
package.domain = com.scene.weaver
source.dir = src/platform/android
source.include_exts = py,png,jpg,kv,atlas
version = {self.build_config['version_name']}
requirements = {','.join(self.build_config['requirements'])}
android.permissions = {','.join(self.build_config['permissions'])}
android.api = {self.build_config['target_sdk']}
android.minapi = {self.build_config['min_sdk']}
android.ndk = 25b
android.arch = {','.join(self.build_config['architectures'][:2])}  # 主要架构

[buildozer]
log_level = 2
warn_on_root = 1

[app_config]
orientation = sensor
fullscreen = 1
presplash_color = #FFFFFF
android.wakelock = 1
android.presplash = ./assets/splash.png
"""
        return spec_content
    
    def generate_gradle_config(self) -> str:
        """生成Gradle配置文件"""
        gradle_content = f"""android {{
    compileSdkVersion {self.build_config['compile_sdk']}
    ndkVersion "25.1.8937393"
    
    defaultConfig {{
        applicationId "{self.build_config['package_name']}"
        minSdkVersion {self.build_config['min_sdk']}
        targetSdkVersion {self.build_config['target_sdk']}
        versionCode {self.build_config['version_code']}
        versionName "{self.build_config['version_name']}"
        
        ndk {{
            abiFilters {', '.join([f'"{arch}"' for arch in self.build_config['architectures']])}
        }}
    }}
    
    buildTypes {{
        release {{
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }}
    }}
    
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }}
}}

dependencies {{
    implementation 'org.python:python:3.12.0'
    implementation 'org.kivy:kivy:2.2.0'
}}
"""
        return gradle_content
    
    def create_build_scripts(self):
        """创建构建脚本"""
        # 创建Buildozer配置文件
        buildozer_spec = self.generate_buildozer_spec()
        buildozer_path = self.project_root / 'buildozer.spec'
        with open(buildozer_path, 'w', encoding='utf-8') as f:
            f.write(buildozer_spec)
        
        # 创建Gradle配置文件
        gradle_config = self.generate_gradle_config()
        gradle_path = self.android_dir / 'build.gradle'
        with open(gradle_path, 'w', encoding='utf-8') as f:
            f.write(gradle_config)
        
        # 创建构建脚本
        self._create_build_script()
        
        return buildozer_path, gradle_path
    
    def _create_build_script(self):
        """创建构建脚本"""
        build_script = f"""#!/bin/bash
# SceneWeaver Android构建脚本

echo "开始构建SceneWeaver Android应用..."

# 检查依赖
echo "检查构建依赖..."
if ! command -v buildozer &> /dev/null; then
    echo "安装Buildozer..."
    pip install buildozer
fi

# 清理之前的构建
echo "清理之前的构建文件..."
buildozer android clean

# 构建应用
echo "开始构建应用..."
buildozer android debug

# 检查构建结果
if [ -f "bin/SceneWeaver-{self.build_config['version_name']}-debug.apk" ]; then
    echo "构建成功！APK文件位于: bin/SceneWeaver-{self.build_config['version_name']}-debug.apk"
else
    echo "构建失败！请检查错误信息。"
    exit 1
fi
"""
        
        script_path = self.project_root / 'build_android.sh'
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(build_script)
        
        # 设置执行权限（在Unix系统上）
        if os.name != 'nt':
            os.chmod(script_path, 0o755)
    
    def get_required_permissions(self) -> List[str]:
        """获取所需权限列表"""
        return self.build_config['permissions']
    
    def get_supported_architectures(self) -> List[str]:
        """获取支持的架构列表"""
        return self.build_config['architectures']


# 构建辅助函数
def setup_android_development_environment():
    """设置Android开发环境"""
    print("设置Android开发环境...")
    
    # 检查必要的工具
    required_tools = ['buildozer', 'adb', 'java']
    missing_tools = []
    
    for tool in required_tools:
        if os.system(f"which {tool}") != 0:
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"缺少以下工具: {', '.join(missing_tools)}")
        print("请安装必要的开发工具后再进行构建。")
        return False
    
    print("Android开发环境检查通过")
    return True


def build_android_app():
    """构建Android应用"""
    config = AndroidBuildConfig()
    
    if not setup_android_development_environment():
        return False
    
    print("生成构建配置文件...")
    buildozer_path, gradle_path = config.create_build_scripts()
    
    print(f"Buildozer配置文件: {buildozer_path}")
    print(f"Gradle配置文件: {gradle_path}")
    
    print("开始构建过程...")
    # 这里应该调用实际的构建命令
    # os.system("./build_android.sh")
    
    print("Android应用构建配置完成")
    return True


if __name__ == '__main__':
    build_android_app()