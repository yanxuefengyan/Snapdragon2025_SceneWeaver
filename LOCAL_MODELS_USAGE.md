# SceneWeaver 本地模型使用指南

## 📖 概述

SceneWeaver支持将AI模型文件下载到本地使用，这样可以：
- 提高模型加载速度
- 减少网络依赖
- 支持离线使用
- 便于模型版本管理

## 🚀 快速开始

### 1. 下载模型文件

使用提供的下载工具：

```bash
# 查看可用模型
python download_models.py list

# 下载特定模型
python download_models.py download --model yolov5s

# 批量下载多个模型
python download_models.py download --model yolov5s
python download_models.py download --model yolov5m

# 强制重新下载
python download_models.py download --model yolov5s --force
```

### 2. 配置使用本地模型

修改 `config.yaml` 配置文件：

```yaml
ai:
  use_local_models: true  # 启用本地模型
  local_models_dir: "models"  # 模型存储目录
  
  object_detection:
    use_local_model: true  # 目标检测使用本地模型
    model_name: "yolov5s"
```

### 3. 运行程序

```bash
# 正常运行（会自动使用本地模型）
python src/main.py

# 或者使用命令行参数
python src/main.py --config config.yaml
```

## 📁 目录结构

```
scene-weaver/
├── models/                 # 本地模型存储目录
│   ├── yolov5s.pt         # YOLOv5s模型
│   ├── yolov5m.pt         # YOLOv5m模型
│   └── ssd_mobilenet_v2/  # SSD模型目录
├── download_models.py     # 模型下载工具
└── config.yaml           # 配置文件
```

## 🛠️ 详细使用说明

### 支持的模型

| 模型名称 | 类型 | 大小 | 用途 |
|---------|------|------|------|
| yolov5s | YOLO | 14.1 MB | 轻量级目标检测 |
| yolov5m | YOLO | 48.2 MB | 中等精度检测 |
| ssd_mobilenet_v2 | SSD | 197.8 MB | TensorFlow SSD |

### 下载工具功能

```bash
# 列出所有可用模型
python download_models.py list

# 下载模型
python download_models.py download --model <model_name>

# 验证模型完整性
python download_models.py verify --model <model_name>

# 清理下载的模型
python download_models.py cleanup
```

### 配置选项说明

```yaml
ai:
  # 全局本地模型设置
  use_local_models: true          # 是否启用本地模型功能
  local_models_dir: "models"      # 本地模型存储目录
  
  # 目标检测本地模型设置
  object_detection:
    use_local_model: true         # 是否使用本地模型进行目标检测
    model_name: "yolov5s"         # 模型名称
    confidence_threshold: 0.5     # 置信度阈值
```

## 🔧 高级用法

### 自定义模型目录

```yaml
ai:
  local_models_dir: "/path/to/your/models"
  object_detection:
    use_local_model: true
```

### 混合使用模式

```yaml
ai:
  use_local_models: true          # 启用本地模型功能
  object_detection:
    use_local_model: false        # 但仍从网络加载目标检测模型
```

### 程序中动态切换

```python
# 在代码中切换模型
ai_system = AISystem(config)
ai_system.switch_model('yolov5m')  # 切换到不同的本地模型

# 获取模型状态
status = ai_system.get_model_status()
print(f"使用本地模型: {status['use_local_models']}")
```

## 📊 性能对比

| 方式 | 首次加载时间 | 后续加载时间 | 网络依赖 |
|------|-------------|-------------|----------|
| 在线加载 | 30-60秒 | 1-2秒 | 需要 |
| 本地加载 | 5-10秒 | <1秒 | 不需要 |

## 🔍 故障排除

### 常见问题

1. **模型文件不存在**
   ```
   错误: 本地模型文件不存在
   解决: 运行 download_models.py 下载对应模型
   ```

2. **模型校验失败**
   ```
   错误: 模型文件校验失败
   解决: 使用 --force 参数重新下载模型
   ```

3. **权限问题**
   ```
   错误: 无法写入模型目录
   解决: 确保对 models 目录有写入权限
   ```

### 调试信息

启用详细日志查看模型加载过程：

```yaml
logging:
  level: "DEBUG"
```

## 📱 移动端适配

对于Android/iOS平台，建议：
1. 预先打包常用模型到APK/IPA中
2. 使用较小的模型版本（如yolov5s）
3. 启用模型压缩优化

## 🤝 贡献和支持

如有问题或建议，请：
1. 查看完整文档
2. 提交GitHub issue
3. 联系技术支持

---
*SceneWeaver - 让AI创作更简单*