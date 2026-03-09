# SceneWeaver iOS平台开发指南

## 概述

本文档详细介绍SceneWeaver在iOS平台上的开发、构建和部署流程，包括Metal图形API集成、iOS特有功能适配和App Store发布准备。

## 系统架构

### iOS平台适配层
```
SceneWeaver Core
    ↓
iOS Platform Adapter
    ├── IOSPlatform (平台检测和基础适配)
    ├── MetalRendererAdapter (Metal渲染适配器)
    ├── IOSTouchHandler (触摸输入处理)
    └── IOSSceneWeaver (iOS主应用入口)
    ↓
iOS SDK/Metal Framework
```

### 主要组件

1. **IOSPlatform** - iOS平台检测和基础适配
2. **MetalRendererAdapter** - Metal图形API集成和优化
3. **IOSTouchHandler** - iOS触摸输入和手势识别
4. **IOSSceneWeaver** - iOS主应用入口和生命周期管理

## 开发环境设置

### 系统要求
- **操作系统**: macOS 11.0+ (Big Sur)
- **Xcode**: 13.0+
- **Python**: 3.8+
- **iOS SDK**: 14.0+

### 必需工具安装

#### 1. Xcode和命令行工具
```bash
# 从App Store安装Xcode
# 或从Apple Developer网站下载

# 安装命令行工具
xcode-select --install

# 验证安装
xcodebuild -version
```

#### 2. Python环境
```bash
# 使用pyenv管理Python版本
brew install pyenv
pyenv install 3.12.0
pyenv global 3.12.0

# 或使用系统Python
pip3 install --upgrade pip
```

#### 3. iOS开发证书
```bash
# 生成开发证书
# 1. 访问Apple Developer网站
# 2. 创建App ID和开发证书
# 3. 下载并安装到钥匙串访问

# 验证证书
security find-identity -v -p codesigning
```

## 项目结构

```
src/platform/ios/
├── __init__.py              # iOS平台检测和基础类
├── main.py                  # iOS主程序入口
├── metal_renderer.py        # Metal渲染适配器
├── touch_input.py           # 触摸输入处理
├── build_config.py          # 构建配置生成器
└── assets/                  # iOS特定资源
    ├── icons/              # 应用图标 (多种尺寸)
    ├── launch/             # 启动画面
    ├── storyboards/        # Interface Builder文件
    └── localization/       # 多语言支持文件
```

## Metal渲染集成

### Metal渲染适配器特性

#### 1. 高性能图形渲染
```python
class MetalRendererAdapter:
    def initialize(self) -> bool:
        # 初始化Metal设备
        # 创建命令队列
        # 配置渲染管线
        # 设置深度模板状态
        pass
    
    def render_geometry(self, vertices, indices, texture=None):
        # 高效的几何体渲染
        # 纹理映射支持
        # 着色器程序执行
        pass
```

#### 2. 资源管理优化
```python
# 缓冲区管理
def _create_or_get_buffer(self, data, buffer_type: str):
    # 缓冲区缓存机制
    # 内存重用优化
    # 自动资源回收
    pass

# 纹理管理
def _convert_to_metal_texture(self, texture_data):
    # 纹理格式转换
    # 压缩纹理支持
    # Mipmap生成
    pass
```

#### 3. 性能监控和调优
```python
def get_performance_stats(self) -> Dict[str, Any]:
    return {
        'target_fps': self.target_fps,
        'msaa_samples': self.msaa_samples,
        'texture_compression': self.texture_compression,
        'dynamic_resolution': self.dynamic_resolution,
        'cached_resources': len(self.resource_cache)
    }
```

## 触摸输入处理

### iOS特有手势支持

#### 1. 基础触摸事件
```python
class IOSTouchHandler:
    def handle_touch_event(self, touch_id: int, x: float, y: float, 
                          force: float, phase: TouchEventType):
        # 多点触控跟踪
        # 触摸相位处理
        # 压感支持 (3D Touch)
        pass
```

#### 2. 手势识别系统
支持的手势类型：
- ✅ 单击 (Tap)
- ✅ 双击 (Double Tap)
- ✅ 滑动 (Swipe)
- ✅ 捏合缩放 (Pinch)
- ✅ 旋转 (Rotation)
- ✅ 长按 (Long Press)
- ✅ 平移 (Pan)

#### 3. 触觉反馈集成
```python
def _provide_haptic_feedback(self, gesture_type: GestureType):
    # 不同强度的触觉反馈
    # 根据手势类型定制反馈
    # 用户偏好设置支持
    pass
```

## 构建和部署

### 1. 生成构建配置
```python
from platform.ios.build_config import IOSBuildConfig

config = IOSBuildConfig()
config_files = config.create_build_scripts()
```

### 2. Xcode项目构建
```bash
# 生成Info.plist
# 生成项目配置文件
# 创建Xcode项目结构

# 构建Debug版本
xcodebuild -project SceneWeaver.xcodeproj -scheme SceneWeaver -configuration Debug

# 构建Release版本
xcodebuild -project SceneWeaver.xcodeproj -scheme SceneWeaver -configuration Release
```

### 3. 真机调试
```bash
# 连接iOS设备
# 选择正确的开发团队
# 配置代码签名
# 部署到设备进行测试
```

## iOS特定配置

### Info.plist配置
```xml
<key>NSCameraUsageDescription</key>
<string>用于AR功能和物体识别</string>

<key>NSMicrophoneUsageDescription</key>
<string>用于语音控制</string>

<key>NSPhotoLibraryUsageDescription</key>
<string>用于导入媒体文件</string>

<key>UIRequiresFullScreen</key>
<true/>

<key>UIStatusBarHidden</key>
<true/>
```

### 性能优化配置
```yaml
ios:
  status_bar_hidden: true          # 隐藏状态栏
  idle_timer_disabled: true        # 禁用屏幕休眠
  msaa_samples: 4                  # 多重采样抗锯齿
  texture_compression: true        # 纹理压缩
  dynamic_resolution: true         # 动态分辨率调整
```

## App Store发布准备

### 1. 应用元数据
```json
{
  "appStore": {
    "bundleId": "com.scene.weaver",
    "version": "1.0.0",
    "category": "Entertainment",
    "keywords": ["AR", "AI", "Graphics", "Creative"],
    "supportUrl": "https://scene-weaver.com/support",
    "privacyUrl": "https://scene-weaver.com/privacy"
  }
}
```

### 2. 截图和预览
- iPhone各尺寸截图 (6.1", 6.7", 5.4")
- iPad截图
- App Store预览视频
- 应用图标 (1024x1024)

### 3. 审核准备
```bash
# 生成发布版本
xcodebuild -project SceneWeaver.xcodeproj -scheme SceneWeaver -configuration Release archive

# 导出IPA文件
xcodebuild -exportArchive -archivePath build/SceneWeaver.xcarchive -exportPath build/ipa -exportOptionsPlist exportOptions.plist

# 上传到App Store Connect
xcrun altool --upload-app -f build/ipa/SceneWeaver.ipa -u YOUR_APPLE_ID
```

## 性能优化指南

### 1. Metal性能优化
```python
# 渲染批次合并
def batch_render_calls(self, renderables):
    # 合并相似的渲染调用
    # 减少状态切换
    # 优化绘制顺序
    pass

# 内存管理
def manage_gpu_memory(self):
    # 及时释放未使用资源
    # 使用环形缓冲区
    # 实现资源池
    pass
```

### 2. 电池优化
```python
# 动态性能调整
def adjust_performance_for_battery(self, battery_level: int):
    if battery_level < 20:
        self.target_fps = 30
        self.texture_quality = 'low'
    elif battery_level < 50:
        self.target_fps = 45
        self.texture_quality = 'medium'
    else:
        self.target_fps = 60
        self.texture_quality = 'high'
```

### 3. 内存优化
```python
# 资源压缩
def compress_resources_for_mobile(self):
    # 纹理压缩格式选择
    # 模型LOD (Level of Detail)
    # 音频压缩优化
    pass
```

## 调试和测试

### 1. Xcode调试
```bash
# 启用Metal调试
defaults write com.apple.dt.Xcode IDEMetalShaderValidation -bool YES

# 查看帧率统计
# 在Xcode中使用Debug Navigator
# 查看GPU和CPU使用情况
```

### 2. 性能分析
```bash
# 使用Instruments
open -a Instruments

# 分析工具选择:
# - Time Profiler (CPU性能)
# - Metal System Trace (GPU性能)
# - Allocations (内存使用)
# - Leaks (内存泄漏)
```

### 3. 日志监控
```python
# iOS日志系统集成
import os
log_path = os.path.expanduser("~/Documents/SceneWeaver/ios.log")

# 在Xcode Console中查看
# 使用设备控制台应用
# 系统日志分析
```

## 常见问题解决

### 1. 构建失败
```bash
# 清理构建缓存
rm -rf ~/Library/Developer/Xcode/DerivedData
xcodebuild clean

# 重新生成项目文件
python src/platform/ios/build_config.py
```

### 2. 签名问题
```bash
# 检查证书和配置文件
security find-identity -v -p codesigning

# 修复权限问题
sudo xcode-select --reset
```

### 3. 性能问题
```python
# 启用性能监控
config['performance']['monitor_enabled'] = True

# 降低渲染质量
config['graphics']['effects_quality'] = 'low'
config['graphics']['msaa_samples'] = 2
```

## 最佳实践

### 1. 代码组织
```python
# 遵循iOS开发规范
# 使用Swift/Objective-C桥接
# 实现AppDelegate生命周期管理
# 遵循MVC/MVVM架构模式
```

### 2. 资源管理
```python
# 使用Asset Catalog管理图片
# 实现按需加载机制
# 支持Dark Mode
# 适配不同屏幕尺寸
```

### 3. 用户体验
```python
# 实现流畅的动画过渡
# 提供适当的触觉反馈
# 支持VoiceOver无障碍功能
# 遵循Human Interface Guidelines
```

## 未来扩展方向

### 计划功能
- [ ] ARKit深度集成
- [ ] Core ML模型优化
- [ ] SwiftUI界面重构
- [ ] Widget扩展支持
- [ ] Handoff功能集成

### 技术升级
- [ ] Metal Performance Shaders集成
- [ ] RealityKit支持
- [ ] 更高级的触觉反馈
- [ ] 空间音频支持

---

**版本**: 1.0.0  
**最后更新**: 2026年2月  
**作者**: SceneWeaver开发团队