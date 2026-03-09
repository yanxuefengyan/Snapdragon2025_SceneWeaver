# SceneWeaver Android平台开发指南

## 概述

本文档详细介绍SceneWeaver在Android平台上的开发、构建和部署流程。

## 系统架构

### Android平台适配层
```
SceneWeaver Core
    ↓
Android Platform Adapter
    ├── Android Platform Detection
    ├── Touch Input Handler
    ├── Renderer Optimizer
    └── Resource Manager
    ↓
Android SDK/Native
```

### 主要组件

1. **AndroidPlatform** - 平台检测和基础适配
2. **AndroidTouchHandler** - 触摸输入和手势识别
3. **AndroidRendererAdapter** - 渲染性能优化
4. **AndroidSceneWeaver** - Android主应用入口

## 开发环境设置

### 系统要求
- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.8+
- **Java**: JDK 8+
- **Android SDK**: API Level 21+

### 必需工具安装

#### 1. Python依赖
```bash
pip install buildozer cython kivy
```

#### 2. Android工具链
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y build-essential git python3 python3-dev \
    ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev \
    libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev \
    libavcodec-dev zlib1g-dev

# macOS (使用Homebrew)
brew install autoconf automake libtool pkg-config
brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf

# Windows (使用Chocolatey)
choco install git python ffmpeg
```

#### 3. Android SDK
```bash
# 下载Android命令行工具
wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
unzip commandlinetools-linux-9477386_latest.zip -d ~/android-sdk

# 设置环境变量
export ANDROID_HOME=~/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools

# 安装必要组件
sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.2"
```

## 项目结构

```
src/platform/android/
├── __init__.py              # Android平台检测和基础类
├── main.py                  # Android主程序入口
├── touch_input.py           # 触摸输入处理
├── renderer_adapter.py      # 渲染适配器
├── build_config.py          # 构建配置生成器
└── assets/                  # Android特定资源
    ├── icons/              # 应用图标
    ├── splash/             # 启动画面
    └── layouts/            # UI布局文件
```

## 构建流程

### 1. 生成构建配置
```python
from platform.android.build_config import AndroidBuildConfig

config = AndroidBuildConfig()
buildozer_path, gradle_path = config.create_build_scripts()
```

### 2. 构建APK
```bash
# 方法1: 使用Buildozer (推荐)
buildozer android debug

# 方法2: 使用提供的构建脚本
./build_android.sh

# 方法3: 手动构建
cd src/platform/android
python build_config.py
buildozer android debug
```

### 3. 构建选项

#### 调试版本
```bash
buildozer android debug
```

#### 发布版本
```bash
buildozer android release
```

#### 特定架构
```bash
buildozer android debug --arch arm64-v8a
```

## 配置说明

### buildozer.spec 配置详解

```ini
[app]
# 应用基本信息
title = SceneWeaver
package.name = scene_weaver
package.domain = com.scene.weaver
version = 1.0.0

# 权限配置
android.permissions = INTERNET,CAMERA,WRITE_EXTERNAL_STORAGE

# SDK版本
android.api = 33
android.minapi = 21

# 架构支持
android.arch = armeabi-v7a,arm64-v8a
```

### Android特定配置

在 `config_android.yaml` 中：

```yaml
android:
  immersive_mode: true          # 沉浸式模式
  keep_screen_on: true          # 保持屏幕常亮
  orientation: sensor           # 屏幕方向
  battery_optimization: true    # 电池优化
  
graphics:
  width: 1080                   # 默认屏幕宽度
  height: 1920                  # 默认屏幕高度
  fullscreen: true              # 全屏模式
  effects_quality: balanced     # 特效质量
  
performance:
  target_fps: 60                # 目标帧率
  adaptive_quality: true        # 自适应质量
  power_save_mode: false        # 省电模式
```

## 性能优化

### 1. 渲染优化
```python
# 在AndroidRendererAdapter中
class AndroidRendererAdapter:
    def optimize_render_settings(self):
        # 根据设备性能动态调整
        if self.is_low_end_device():
            self.target_fps = 30
            self.max_particles = 500
        else:
            self.target_fps = 60
            self.max_particles = 2000
```

### 2. 资源管理
```python
# 纹理压缩
def compress_textures(self):
    if self.battery_level < 30:
        self.texture_compression = True
        self.resolution_scaling = 0.75
```

### 3. 内存优化
```python
# 及时释放未使用资源
def cleanup_unused_resources(self):
    # 清理纹理缓存
    # 释放模型数据
    # 回收GPU资源
    pass
```

## 输入处理

### 触摸事件处理
```python
# 在AndroidTouchHandler中
class AndroidTouchHandler:
    def handle_touch_event(self, event_type, touch_id, x, y):
        # 多点触控支持
        # 手势识别
        # 事件转换为标准输入
        pass
```

### 手势识别
支持的手势类型：
- 单击 (Tap)
- 双击 (Double Tap)
- 滑动 (Swipe)
- 长按 (Long Press)
- 捏合缩放 (Pinch)

## 调试和测试

### 1. 日志查看
```bash
# 查看应用日志
adb logcat | grep "SceneWeaver"

# 查看Python日志
adb logcat | grep "python"
```

### 2. 性能分析
```bash
# 启用详细日志
adb shell setprop log.tag.SceneWeaver VERBOSE

# 查看帧率统计
adb shell dumpsys gfxinfo com.scene.weaver
```

### 3. 内存监控
```bash
# 监控内存使用
adb shell dumpsys meminfo com.scene.weaver

# 查看GPU内存
adb shell dumpsys gfxinfo com.scene.weaver
```

## 常见问题解决

### 1. 构建失败
```bash
# 清理构建缓存
buildozer android clean

# 重新下载依赖
rm -rf .buildozer
buildozer android debug
```

### 2. 运行时错误
```bash
# 检查权限
adb shell pm grant com.scene.weaver android.permission.CAMERA

# 查看详细错误
adb logcat -v threadtime | grep -i error
```

### 3. 性能问题
```python
# 启用性能监控
config['performance']['monitor_enabled'] = True

# 降低渲染质量
config['graphics']['effects_quality'] = 'low'
```

## 发布准备

### 1. 签名配置
```bash
# 生成签名密钥
keytool -genkey -v -keystore scene-weaver.keystore \
    -alias scene-weaver -keyalg RSA -keysize 2048 -validity 10000

# 构建签名APK
buildozer android release
```

### 2. Google Play发布
- 准备应用截图和描述
- 配置应用内购买(如需要)
- 设置测试轨道
- 提交审核

## 最佳实践

### 1. 代码组织
```python
# 遵循单一职责原则
# 分离平台特定代码
# 使用适配器模式
# 保持向后兼容
```

### 2. 资源管理
```python
# 及时释放资源
# 使用资源池
# 实现缓存机制
# 优化资源加载
```

### 3. 错误处理
```python
# 全面的异常捕获
# 优雅的降级处理
# 详细的日志记录
# 用户友好的错误提示
```

## 未来扩展

### 计划功能
- [ ] 原生UI组件集成
- [ ] Google Play Services集成
- [ ] ARCore支持
- [ ] 多窗口模式支持
- [ ] 深度链接支持

### 性能优化方向
- [ ] Vulkan图形API支持
- [ ] 更智能的资源预加载
- [ ] 动态分辨率调整
- [ ] 后台任务优化

---

**版本**: 1.0.0  
**最后更新**: 2026年2月  
**作者**: SceneWeaver开发团队