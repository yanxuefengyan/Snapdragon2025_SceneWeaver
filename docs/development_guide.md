# SceneWeaver 开发指南

## 项目概述

SceneWeaver是一个基于Python的端侧实时混合现实创作系统，专为高通骁龙X Elite平台优化设计。本指南详细介绍项目的架构、开发流程和技术要点。

## 最新更新 (2026年2月)

### 新增功能模块
1. **粒子系统** - 丰富的视觉特效实现
2. **目标检测** - 实时物体识别能力
3. **图形界面** - 直观的用户交互界面
4. **综合测试** - 完整的功能验证体系

### 技术架构演进
- 从OpenGL转向Pygame渲染引擎
- 双AI框架支持(TensorFlow + PyTorch)
- 模块化GUI系统设计
- 完善的配置管理系统

## 技术架构更新

### 当前技术栈 (2026年)

由于Windows ARM64环境下OpenGL兼容性问题，项目采用了更适合的技术栈：

#### 核心技术组件
- **图形渲染**: Pygame 2.6+ (替代OpenGL)
- **AI框架**: TensorFlow 2.20 + PyTorch 2.4 (双框架支持)
- **配置管理**: PyYAML 6.0
- **性能监控**: psutil 7.2 + 自研监控器
- **GUI系统**: pygame-gui 0.6+ (新增)

#### 技术选型优势
1. **更好的兼容性**: Pygame在ARM64环境下表现稳定
2. **更低的学习成本**: 相比OpenGL更易上手
3. **更快的开发速度**: 丰富的内置功能
4. **更强的跨平台性**: 支持Windows/Linux/macOS

### 系统分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                    应用层 (Application Layer)                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   主程序    │  │  配置管理   │  │   日志系统   │          │
│  │  main.py    │  │ ConfigMgr   │  │   Logger    │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    引擎层 (Engine Core)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  核心引擎   │  │  场景管理   │  │  资源管理   │          │
│  │ CoreEngine  │  │SceneManager │  │ResourceManager│         │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                   子系统层 (Subsystem Layer)                  │
│  ├─ GraphicsSystem 图形系统          │
│  ├─ ParticleSystem 粒子系统         │  (新增)
│  ├─ ObjectDetection 目标检测        │  (新增)
│  ├─ GUISystem 图形界面              │  (新增)
│  ├─ AISystem AI系统                 │
│  ├─ InputSystem 输入系统             │
│  └─ AudioSystem 音频系统            │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    平台层 (Platform Layer)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  Pygame API │  │  AI框架     │  │ Python标准库 │          │
│  │ (2D/3D渲染) │  │ TF/PyTorch  │  │   Std Lib   │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## 核心模块详解

### 1. Core Engine (核心引擎)
**文件**: `src/core/engine.py`

负责协调各个子系统的运行，管理主循环和系统生命周期。

```python
class CoreEngine:
    def __init__(self, config: Dict[str, Any]):
        """初始化核心引擎"""
        pass
    
    def initialize(self) -> bool:
        """初始化所有子系统"""
        pass
    
    def run(self):
        """主循环"""
        pass
    
    def handle_events(self):
        """处理系统事件"""
        pass
    
    def update(self, delta_time: float):
        """更新游戏逻辑"""
        pass
    
    def render(self):
        """渲染画面"""
        pass

## 开发环境搭建

### 系统要求
- **操作系统**: Windows 10/11 (x64/ARM64) 或 Linux/macOS
- **Python版本**: 3.12+
- **开发工具**: VS Code / PyCharm
- **构建工具**: pip / poetry

### 依赖安装
```bash
# 克隆项目
git clone https://github.com/scene-weaver/scene-weaver.git
cd scene-weaver

# 安装依赖
pip install -r requirements.txt

# 或使用poetry
poetry install
```

### 环境验证
```bash
# 运行环境检查
python check_environment.py

# 运行单元测试
python -m pytest tests/

# 运行基础功能测试
python test_basic.py

# 运行综合测试
python test_comprehensive.py

## 编码规范

### Python代码规范
遵循PEP 8标准，关键要点：

```python
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class Camera:
    """摄像机配置类"""
    position: np.ndarray
    target: np.ndarray
    fov: float = 45.0

class ExampleClass:
    """示例类文档字符串"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化方法
        
        Args:
            config: 配置字典，包含必要的初始化参数
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._initialized = False
    
    def example_method(self, param: str, timeout: Optional[float] = None) -> bool:
        """
        示例方法说明
        
        Args:
            param: 参数说明，类型为字符串
            timeout: 超时时间，可选参数，默认为None
            
        Returns:
            bool: 成功返回True，失败返回False
            
        Raises:
            ValueError: 当参数无效时抛出
        """
        try:
            if not param:
                raise ValueError("参数不能为空")
            
            # 方法实现
            self.logger.info(f"处理参数: {param}")
            result = self._internal_process(param, timeout)
            
            return result
            
        except Exception as e:
            self.logger.error(f"方法执行出错: {e}")
            raise
    
    def _internal_process(self, data: str, timeout: Optional[float]) -> bool:
        """内部处理方法"""
        # 私有方法实现
        return True
```

## 性能优化指南

### 1. 渲染性能优化
```python
# 使用Surface缓存减少重复绘制
class OptimizedRenderer(Renderer):
    def __init__(self, config):
        super().__init__(config)
        self.cache_surfaces = {}
        self.dirty_rects = []
    
    def render_cached_object(self, obj_id, surface):
        """缓存渲染对象"""
        if obj_id not in self.cache_surfaces:
            self.cache_surfaces[obj_id] = surface.copy()
        # 只在需要时重新绘制
```

### 2. AI推理优化
```python
# 批处理推理提高效率
class BatchAISystem(AISystem):
    def __init__(self, config):
        super().__init__(config)
        self.batch_queue = []
        self.batch_size = config.get('batch_size', 8)
    
    def queue_inference(self, data):
        """队列推理请求"""
        self.batch_queue.append(data)
        if len(self.batch_queue) >= self.batch_size:
            return self.process_batch()
```

### 3. 内存管理优化
```python
# 及时释放不需要的资源
class MemoryEfficientSystem:
    def __init__(self):
        self.resource_pool = {}
        self.max_cache_size = 100
    
    def cleanup_unused_resources(self):
        """清理未使用的资源"""
        current_time = time.time()
        expired_keys = [
            key for key, (resource, timestamp) 
            in self.resource_pool.items() 
            if current_time - timestamp > 300  # 5分钟超时
        ]
        
        for key in expired_keys:
            del self.resource_pool[key]
```

## 调试技巧

### 1. 日志调试
```python
import logging
import logging.config

# 配置日志级别
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 不同级别的日志使用
logger.debug("详细调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")
```

### 2. 性能分析
```python
import cProfile
import pstats
from pstats import SortKey

def profile_function(func, *args, **kwargs):
    """性能分析装饰器"""
    profiler = cProfile.Profile()
    profiler.enable()
    
    result = func(*args, **kwargs)
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats(SortKey.CUMULATIVE)
    stats.print_stats(20)  # 显示前20个最耗时的函数
    
    return result
```

### 3. 内存分析
```python
import tracemalloc
import psutil

def monitor_memory_usage():
    """监控内存使用情况"""
    # 内存快照
    tracemalloc.start()
    
    # 获取进程内存信息
    process = psutil.Process()
    memory_info = process.memory_info()
    
    print(f"RSS内存: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS内存: {memory_info.vms / 1024 / 1024:.2f} MB")
    
    # 获取内存分配详情
    current, peak = tracemalloc.get_traced_memory()
    print(f"当前内存使用: {current / 1024 / 1024:.2f} MB")
    print(f"峰值内存使用: {peak / 1024 / 1024:.2f} MB")
    
    tracemalloc.stop()
```

## 测试策略

### 1. 单元测试
```python
import unittest
from unittest.mock import Mock, patch

class TestRenderer(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        self.config = {'width': 800, 'height': 600}
        self.renderer = Renderer(self.config)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.renderer.width, 800)
        self.assertEqual(self.renderer.height, 600)
    
    @patch('pygame.display.set_mode')
    def test_display_initialization(self, mock_set_mode):
        """测试显示初始化"""
        mock_surface = Mock()
        mock_set_mode.return_value = mock_surface
        
        result = self.renderer.initialize()
        
        self.assertTrue(result)
        mock_set_mode.assert_called_once_with((800, 600))
    
    def tearDown(self):
        """测试后清理"""
        if hasattr(self.renderer, 'screen') and self.renderer.screen:
            self.renderer.cleanup()

if __name__ == '__main__':
    unittest.main()

### 2. 集成测试
```python
def test_full_rendering_pipeline():
    """测试完整渲染流水线"""
    # 初始化系统
    config = {
        'graphics': {'width': 1280, 'height': 720},
        'ai': {'device': 'cpu'}
    }
    
    engine = CoreEngine(config)
    assert engine.initialize(), "引擎初始化失败"
    
    # 运行几个渲染周期
    for i in range(10):
        engine.handle_events()
        engine.update(1/60)
        engine.render()
    
    # 验证性能指标
    perf_metrics = engine.perf_monitor.get_current_metrics()
    assert perf_metrics.fps > 30, f"FPS过低: {perf_metrics.fps}"
    assert perf_metrics.frame_time < 0.05, f"帧时间过长: {perf_metrics.frame_time}"
```

## 部署指南

### 1. 打包发布
```bash
# 安装打包工具
pip install build twine

# 创建发行版
python -m build

# 上传到PyPI
twine upload dist/*
```

### 2. Docker部署
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 复制项目文件
COPY . .

# 安装依赖
RUN pip install -r requirements.txt

# 暴露端口
EXPOSE 8000

# 启动应用
CMD ["python", "src/main.py"]
```

### 3. 性能基准测试
```python
# benchmarks/run_benchmarks.py
import time
import statistics
from src.core.engine import CoreEngine

def benchmark_rendering_performance():
    """渲染性能基准测试"""
    config = {'graphics': {'width': 1920, 'height': 1080}}
    engine = CoreEngine(config)
    engine.initialize()
    
    # 预热
    for _ in range(100):
        engine.update(1/60)
        engine.render()
    
    # 正式测试
    frame_times = []
    for _ in range(1000):
        start = time.time()
        engine.update(1/60)
        engine.render()
        frame_times.append(time.time() - start)
    
    # 统计结果
    avg_fps = 1.0 / statistics.mean(frame_times)
    min_fps = 1.0 / max(frame_times)
    max_fps = 1.0 / min(frame_times)
    
    print(f"平均FPS: {avg_fps:.2f}")
    print(f"最小FPS: {min_fps:.2f}")
    print(f"最大FPS: {max_fps:.2f}")

if __name__ == "__main__":
    benchmark_rendering_performance()
```

## 常见问题解决

### 1. Pygame初始化失败
```python
# 解决方案：检查显示环境
import os
os.environ['SDL_VIDEODRIVER'] = 'windib'  # Windows
# 或
os.environ['SDL_VIDEODRIVER'] = 'x11'     # Linux
```

### 2. AI模型加载缓慢
```python
# 解决方案：启用模型缓存
class CachedModelLoader:
    def __init__(self):
        self.model_cache = {}
    
    def load_model(self, model_path):
        if model_path in self.model_cache:
            return self.model_cache[model_path]
        
        # 加载模型
        model = self._load_from_disk(model_path)
        self.model_cache[model_path] = model
        return model
```

### 3. 内存泄漏问题
```python
# 解决方案：定期垃圾回收
import gc

class MemoryManagedSystem:
    def __init__(self):
        self.allocation_counter = 0
        self.gc_threshold = 1000
    
    def allocate_resource(self):
        self.allocation_counter += 1
        if self.allocation_counter >= self.gc_threshold:
            gc.collect()
            self.allocation_counter = 0

## 贡献指南

### 1. 代码提交流程
```bash
# Fork项目并克隆
git clone https://github.com/your-username/scene-weaver.git
cd scene-weaver

# 创建功能分支
git checkout -b feature/new-feature

# 开发并测试
# ... 编写代码 ...

# 运行测试
python -m pytest tests/

# 提交代码
git add .
git commit -m "Add new feature: detailed description"

# 推送到远程
git push origin feature/new-feature
```

### 2. Pull Request要求
- ✅ 通过所有现有测试
- ✅ 包含相应的单元测试
- ✅ 更新相关文档
- ✅ 遵循编码规范
- ✅ 提供清晰的变更说明

### 3. 版本发布流程
```bash
# 更新版本号
# 修改 pyproject.toml 和 __init__.py

# 创建发布标签
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0

# 发布到PyPI
python -m build
twine upload dist/*