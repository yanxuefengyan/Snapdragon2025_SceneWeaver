"""
iOS Build Configuration - iOS构建配置
SceneWeaver iOS平台的构建和打包配置
"""

import os
from pathlib import Path
from typing import Dict, List, Any
import plistlib
import json


class IOSBuildConfig:
    """iOS构建配置类"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.ios_dir = Path(__file__).parent
        
        # 构建配置
        self.build_config = {
            'app_name': 'SceneWeaver',
            'bundle_identifier': 'com.scene.weaver',
            'version': '1.0.0',
            'build_number': '1',
            'deployment_target': '14.0',
            'supported_devices': ['iphone', 'ipad'],
            'device_families': [1, 2],  # 1=iPhone, 2=iPad
            
            # 应用权限
            'permissions': {
                'camera': '用于AR功能和物体识别',
                'microphone': '用于语音控制',
                'photo_library': '用于导入媒体文件',
                'location_when_in_use': '用于位置相关功能'
            },
            
            # 架构支持
            'architectures': ['arm64'],
            'valid_archs': ['arm64'],
            
            # Python相关
            'python_version': '3.12',
            'requirements': [
                'pygame',
                'numpy',
                'pillow',
                'opencv-python',
                'pyyaml'
            ],
            
            # App Store配置
            'app_store': {
                'category': 'Entertainment',
                'keywords': ['AR', 'AI', 'Graphics', 'Creative'],
                'support_url': 'https://scene-weaver.com/support',
                'privacy_url': 'https://scene-weaver.com/privacy'
            }
        }
    
    def generate_info_plist(self) -> str:
        """生成Info.plist文件"""
        info_dict = {
            'CFBundleDevelopmentRegion': 'en',
            'CFBundleDisplayName': self.build_config['app_name'],
            'CFBundleExecutable': self.build_config['app_name'],
            'CFBundleIdentifier': self.build_config['bundle_identifier'],
            'CFBundleInfoDictionaryVersion': '6.0',
            'CFBundleName': self.build_config['app_name'],
            'CFBundlePackageType': 'APPL',
            'CFBundleShortVersionString': self.build_config['version'],
            'CFBundleVersion': self.build_config['build_number'],
            'LSRequiresIPhoneOS': True,
            'UIApplicationSceneManifest': {
                'UIApplicationSupportsMultipleScenes': False,
                'UISceneConfigurations': {
                    'UIWindowSceneSessionRoleApplication': [{
                        'UISceneConfigurationName': 'Default Configuration',
                        'UISceneDelegateClassName': '$(PRODUCT_MODULE_NAME).SceneDelegate'
                    }]
                }
            },
            'UILaunchStoryboardName': 'LaunchScreen',
            'UIRequiredDeviceCapabilities': ['arm64'],
            'UISupportedInterfaceOrientations': [
                'UIInterfaceOrientationPortrait',
                'UIInterfaceOrientationLandscapeLeft',
                'UIInterfaceOrientationLandscapeRight'
            ],
            'UISupportedInterfaceOrientations~ipad': [
                'UIInterfaceOrientationPortrait',
                'UIInterfaceOrientationPortraitUpsideDown',
                'UIInterfaceOrientationLandscapeLeft',
                'UIInterfaceOrientationLandscapeRight'
            ],
            'UIViewControllerBasedStatusBarAppearance': False
        }
        
        # 添加权限描述
        for perm_key, perm_desc in self.build_config['permissions'].items():
            info_dict[f'NS{perm_key.capitalize()}UsageDescription'] = perm_desc
        
        return plistlib.dumps(info_dict)
    
    def generate_project_config(self) -> Dict[str, Any]:
        """生成项目配置"""
        return {
            'name': self.build_config['app_name'],
            'productName': self.build_config['app_name'],
            'bundleId': self.build_config['bundle_identifier'],
            'deploymentTarget': self.build_config['deployment_target'],
            'devices': self.build_config['supported_devices'],
            'architectures': self.build_config['architectures'],
            'validArchs': self.build_config['valid_archs'],
            'pythonRequirements': self.build_config['requirements']
        }
    
    def generate_xcode_project_structure(self) -> Dict[str, Any]:
        """生成Xcode项目结构"""
        return {
            'project': {
                'name': f"{self.build_config['app_name']}.xcodeproj",
                'targets': [
                    {
                        'name': self.build_config['app_name'],
                        'type': 'application',
                        'platform': 'iOS',
                        'deploymentTarget': self.build_config['deployment_target'],
                        'settings': {
                            'PRODUCT_NAME': self.build_config['app_name'],
                            'PRODUCT_BUNDLE_IDENTIFIER': self.build_config['bundle_identifier'],
                            'IPHONEOS_DEPLOYMENT_TARGET': self.build_config['deployment_target'],
                            'TARGETED_DEVICE_FAMILY': ','.join(map(str, self.build_config['device_families'])),
                            'ARCHS': ' '.join(self.build_config['architectures']),
                            'VALID_ARCHS': ' '.join(self.build_config['valid_archs'])
                        }
                    }
                ]
            }
        }
    
    def generate_app_store_config(self) -> Dict[str, Any]:
        """生成App Store配置"""
        return {
            'appStore': {
                'bundleId': self.build_config['bundle_identifier'],
                'version': self.build_config['version'],
                'category': self.build_config['app_store']['category'],
                'keywords': self.build_config['app_store']['keywords'],
                'supportUrl': self.build_config['app_store']['support_url'],
                'privacyUrl': self.build_config['app_store']['privacy_url'],
                'copyright': '© 2026 SceneWeaver Team'
            }
        }
    
    def create_build_scripts(self):
        """创建构建脚本"""
        # 创建Info.plist
        info_plist_content = self.generate_info_plist()
        info_plist_path = self.ios_dir / 'Info.plist'
        with open(info_plist_path, 'wb') as f:
            f.write(info_plist_content)
        
        # 创建项目配置文件
        project_config = self.generate_project_config()
        project_config_path = self.ios_dir / 'project_config.json'
        with open(project_config_path, 'w', encoding='utf-8') as f:
            json.dump(project_config, f, indent=2, ensure_ascii=False)
        
        # 创建Xcode项目结构
        xcode_config = self.generate_xcode_project_structure()
        xcode_config_path = self.ios_dir / 'xcode_project.json'
        with open(xcode_config_path, 'w', encoding='utf-8') as f:
            json.dump(xcode_config, f, indent=2, ensure_ascii=False)
        
        # 创建App Store配置
        app_store_config = self.generate_app_store_config()
        app_store_config_path = self.ios_dir / 'app_store_config.json'
        with open(app_store_config_path, 'w', encoding='utf-8') as f:
            json.dump(app_store_config, f, indent=2, ensure_ascii=False)
        
        # 创建构建脚本
        self._create_build_script()
        
        return {
            'info_plist': info_plist_path,
            'project_config': project_config_path,
            'xcode_config': xcode_config_path,
            'app_store_config': app_store_config_path
        }
    
    def _create_build_script(self):
        """创建构建脚本"""
        build_script = f"""#!/bin/bash
# SceneWeaver iOS构建脚本

echo "开始构建SceneWeaver iOS应用..."

# 检查Xcode命令行工具
if ! xcode-select -p &> /dev/null; then
    echo "错误: 未找到Xcode命令行工具"
    echo "请安装Xcode并运行: xcode-select --install"
    exit 1
fi

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python 3"
    exit 1
fi

# 设置构建环境
export PYTHON_VERSION="{self.build_config['python_version']}"
export APP_NAME="{self.build_config['app_name']}"
export BUNDLE_ID="{self.build_config['bundle_identifier']}"
export DEPLOYMENT_TARGET="{self.build_config['deployment_target']}"

# 创建构建目录
BUILD_DIR="build/ios"
mkdir -p "$BUILD_DIR"

# 复制源代码
echo "复制源代码..."
cp -r src "$BUILD_DIR/"
cp -r assets "$BUILD_DIR/"
cp config.yaml "$BUILD_DIR/"

# 安装Python依赖
echo "安装Python依赖..."
pip3 install -r requirements.txt --target "$BUILD_DIR/python_packages"

# 生成Xcode项目
echo "生成Xcode项目..."
# 这里应该调用实际的Xcode项目生成工具
# xcodegen generate --spec xcode_project.json

# 构建应用
echo "构建iOS应用..."
# xcodebuild -project "$APP_NAME.xcodeproj" -scheme "$APP_NAME" -configuration Release -destination "generic/platform=iOS" archive -archivePath "$BUILD_DIR/$APP_NAME.xcarchive"

echo "构建完成！"
echo "归档文件位置: $BUILD_DIR/$APP_NAME.xcarchive"
"""
        
        script_path = self.project_root / 'build_ios.sh'
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(build_script)
        
        # 设置执行权限
        if os.name != 'nt':
            os.chmod(script_path, 0o755)
    
    def get_required_permissions(self) -> Dict[str, str]:
        """获取所需权限列表"""
        return self.build_config['permissions']
    
    def get_supported_devices(self) -> List[str]:
        """获取支持的设备列表"""
        return self.build_config['supported_devices']
    
    def generate_entitlements(self) -> str:
        """生成权限文件"""
        entitlements = {
            'get-task-allow': False,  # App Store发布需要设为False
            'application-identifier': f"*.{self.build_config['bundle_identifier']}",
            'keychain-access-groups': [self.build_config['bundle_identifier']],
            'com.apple.developer.team-identifier': 'YOUR_TEAM_ID_HERE'
        }
        
        return plistlib.dumps(entitlements)


# 构建辅助函数
def setup_ios_development_environment():
    """设置iOS开发环境"""
    print("设置iOS开发环境...")
    
    # 检查必要的工具
    required_tools = ['xcodebuild', 'xcrun', 'codesign']
    missing_tools = []
    
    for tool in required_tools:
        if os.system(f"which {tool}") != 0:
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"缺少以下工具: {', '.join(missing_tools)}")
        print("请安装Xcode并确保命令行工具可用。")
        return False
    
    # 检查开发者账号
    try:
        result = os.system("security find-identity -v -p codesigning")
        if result != 0:
            print("警告: 未找到代码签名身份，可能影响真机调试和发布。")
    except:
        print("无法检查代码签名身份。")
    
    print("iOS开发环境检查通过")
    return True


def build_ios_app():
    """构建iOS应用"""
    config = IOSBuildConfig()
    
    if not setup_ios_development_environment():
        return False
    
    print("生成构建配置文件...")
    config_files = config.create_build_scripts()
    
    for name, path in config_files.items():
        print(f"{name}: {path}")
    
    print("开始构建过程...")
    # 这里应该调用实际的构建命令
    # os.system("./build_ios.sh")
    
    print("iOS应用构建配置完成")
    return True


if __name__ == '__main__':
    build_ios_app()