"""
Object Detection System - 目标检测子系统
"""
import logging
import numpy as np
from typing import Dict, Any, List


class ObjectDetectionSystem:
    """目标检测系统"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.enabled = True
        
        # 加载YOLOv5模型
        self.model = None
        self._load_model()
        
        # 性能统计
        self.detection_times = []
        self.max_history = 100
    
    def _load_model(self):
        """加载目标检测模型"""
        try:
            import torch
            # 使用torch.hub加载预训练的YOLOv5s模型
            self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
            self.model.eval()  # 设置为评估模式
            self.logger.info("目标检测模型 (YOLOv5) 加载成功")
        except Exception as e:
            self.logger.error(f"目标检测模型加载失败: {e}")
            self.model = None
    
    def initialize(self) -> bool:
        """
        初始化目标检测系统
        
        Returns:
            bool: 是否初始化成功
        """
        if self.model is not None:
            self.logger.info("目标检测系统初始化完成")
            return True
        else:
            self.logger.warning("目标检测系统初始化失败，模型未加载")
            return False
    
    def process_frame(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        处理单帧图像进行目标检测
        
        Args:
            frame: 输入的BGR图像帧
            
        Returns:
            List[Dict]: 检测到的对象列表
        """
        if not self.enabled or self.model is None:
            return []
        
        try:
            import time
            start_time = time.time()
            
            # 将OpenCV的BGR帧转换为RGB，并使用模型进行推理
            # YOLOv5模型会自动处理图像的预处理（归一化、调整大小等）
            results = self.model(frame[..., ::-1])  # BGR to RGB
            
            # 解析结果
            detections = []
            for det in results.xyxy[0]:  # 获取第一个图像的结果 (x1, y1, x2, y2, confidence, class)
                x1, y1, x2, y2, conf, cls_id = det.tolist()
                detections.append({
                    'class': self.model.names[int(cls_id)],
                    'confidence': conf,
                    'bbox': [int(x1), int(y1), int(x2), int(y2)]
                })
            
            # 记录检测时间
            inference_time = time.time() - start_time
            self._record_inference_time(inference_time)
            
            return detections
            
        except Exception as e:
            self.logger.error(f"目标检测处理出错: {e}")
            return []
    
    def _record_inference_time(self, time_taken: float):
        """记录单次检测耗时"""
        self.detection_times.append(time_taken)
        if len(self.detection_times) > self.max_history:
            self.detection_times.pop(0)
    
    def get_statistics(self) -> Dict[str, float]:
        """
        获取目标检测的性能统计数据
        
        Returns:
            Dict: 包含平均、最小、最大和标准差的字典
        """
        if not self.detection_times:
            return {}
        
        return {
            'avg_detection_time': np.mean(self.detection_times),
            'min_detection_time': np.min(self.detection_times),
            'max_detection_time': np.max(self.detection_times),
            'std_detection_time': np.std(self.detection_times)
        }
    
    def set_enabled(self, enabled: bool):
        """启用或禁用目标检测"""
        self.enabled = enabled
    
    def cleanup(self):
        """清理资源"""
        self.model = None
        self.detection_times.clear()
        self.logger.info("目标检测系统资源已清理")
"""
AI System - AI系统管理
使用修复版目标检测器
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional
from pathlib import Path

# 优先使用修复版的目标检测器
try:
    from .object_detection_fixed import ObjectDetectionSystem as FixedObjectDetectionSystem
    USE_FIXED_DETECTOR = True
except ImportError:
    from .object_detection import ObjectDetectionSystem
    USE_FIXED_DETECTOR = False


class AISystem:
    """AI系统管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化AI系统
        
        Args:
            config: AI配置字典
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # AI子系统
        self.object_detection = None
        
        # 设备配置
        self.device = config.get('device', 'auto')
        self.detection_enabled = config.get('detection_enabled', True)
        
        # 本地模型配置
        self.local_models_dir = config.get('local_models_dir', 'models')
        self.use_local_models = config.get('use_local_models', False)
        
        self.logger.info(f"AI系统初始化完成，使用设备: {self.device}")
        if USE_FIXED_DETECTOR:
            self.logger.info("使用修复版目标检测器")
        else:
            self.logger.info("使用标准目标检测器")
    
    def _detect_optimal_device(self) -> str:
        """
        检测最优计算设备
        
        Returns:
            str: 设备名称 ('npu'/'gpu'/'cpu')
        """
        # 优先级: NPU > GPU > CPU
        if self._has_npu_support():
            return 'npu'
        elif torch.cuda.is_available():
            return 'gpu'
        else:
            return 'cpu'
    
    def _has_npu_support(self) -> bool:
        """检测NPU支持"""
        try:
            # 检查高通SNPE或其他NPU SDK
            import snpe  # 高通SNPE SDK
            return True
        except ImportError:
            try:
                # 检查其他NPU支持
                import qti  # 高通QTI
                return True
            except ImportError:
                return False
    
    def initialize(self) -> bool:
        """初始化AI系统"""
        try:
            self.logger.info("开始初始化AI子系统...")
            
            # 只有当检测功能启用时才初始化目标检测系统
            if self.detection_enabled:
                self.logger.info("检测功能已启用，开始初始化目标检测系统...")
                detection_config = self.config.get('object_detection', {})
                
                # 如果启用了本地模型，更新配置
                if self.use_local_models:
                    detection_config['local_models_dir'] = self.local_models_dir
                    self.logger.info(f"启用本地模型模式，目录: {self.local_models_dir}")
                
                from .object_detection import ObjectDetectionSystem
                self.object_detection = ObjectDetectionSystem(detection_config)
                if not self.object_detection.initialize():
                    self.logger.error("目标检测系统初始化失败")
                    return False
                self.logger.info("目标检测系统初始化成功")
            else:
                self.logger.info("检测功能已禁用，跳过目标检测系统初始化")
            
            self.logger.info("AI系统初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"AI系统初始化失败: {e}")
            return False
    
    def load_model(self, model_path: str, framework: str = 'auto') -> bool:
        """
        加载AI模型
        
        Args:
            model_path: 模型文件路径
            framework: 框架类型 ('tensorflow'/'pytorch'/'auto')
            
        Returns:
            bool: 加载是否成功
        """
        try:
            if framework == 'auto':
                framework = self._detect_framework(model_path)
            
            if framework == 'tensorflow':
                return self._load_tensorflow_model(model_path)
            elif framework == 'pytorch':
                return self._load_pytorch_model(model_path)
            else:
                self.logger.error(f"不支持的框架: {framework}")
                return False
                
        except Exception as e:
            self.logger.error(f"模型加载失败: {e}")
            return False
    
    def _detect_framework(self, model_path: str) -> str:
        """自动检测模型框架"""
        if model_path.endswith(('.pb', '.h5', '.keras')):
            return 'tensorflow'
        elif model_path.endswith(('.pt', '.pth')):
            return 'pytorch'
        else:
            return self.framework
    
    def _load_tensorflow_model(self, model_path: str) -> bool:
        """加载TensorFlow模型"""
        try:
            if model_path.endswith('.pb'):
                # 加载SavedModel格式
                self.model = tf.saved_model.load(model_path)
            else:
                # 加载Keras模型
                self.model = tf.keras.models.load_model(model_path)
            
            self.framework = 'tensorflow'
            self.logger.info(f"TensorFlow模型加载成功: {model_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"TensorFlow模型加载失败: {e}")
            return False
    
    def _load_pytorch_model(self, model_path: str) -> bool:
        """加载PyTorch模型"""
        try:
            # 根据设备选择加载方式
            if self.device == 'gpu':
                self.model = torch.load(model_path, map_location='cuda')
            elif self.device == 'npu':
                # NPU特殊加载方式
                self.model = self._load_for_npu(model_path)
            else:
                self.model = torch.load(model_path, map_location='cpu')
            
            # 设置为评估模式
            if hasattr(self.model, 'eval'):
                self.model.eval()
            
            self.framework = 'pytorch'
            self.logger.info(f"PyTorch模型加载成功: {model_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"PyTorch模型加载失败: {e}")
            return False
    
    def _load_for_npu(self, model_path: str):
        """为NPU加载模型"""
        try:
            # 这里应该使用具体的NPU SDK
            # 示例使用SNPE (Snapdragon Neural Processing Engine)
            import snpe
            runtime = snpe.Runtime()  # 这是示意代码
            model = runtime.load_model(model_path)
            return model
        except ImportError:
            self.logger.warning("NPU SDK未安装，使用CPU回退")
            return torch.load(model_path, map_location='cpu')
    
    def process_frame(self, frame_data: Any, delta_time: float = 0.0) -> Dict[str, Any]:
        """
        处理视频帧
        
        Args:
            frame_data: 帧数据
            delta_time: 时间增量
            
        Returns:
            处理结果字典
        """
        results = {
            'timestamp': delta_time,
            'detections': [],
            'tracking': [],
            'features': {}
        }
        
        try:
            # 只有当检测功能启用且检测系统存在时才进行处理
            if self.object_detection and self.detection_enabled:
                # 处理不同类型的输入数据
                if hasattr(frame_data, 'shape'):  # numpy array
                    detections = self.object_detection.process_frame(frame_data)
                else:  # 其他类型的数据
                    import numpy as np
                    # 创建一个简单的测试图像
                    dummy_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
                    detections = self.object_detection.process_frame(dummy_frame)
                
                # 转换检测结果格式
                converted_detections = []
                for det in detections:
                    converted_detections.append({
                        'bbox': det.bbox,
                        'label': det.label,
                        'confidence': det.confidence,
                        'class_id': det.class_id
                    })
                
                results['detections'] = converted_detections
                
                # 简单的跟踪模拟
                tracked_objects = []
                for i, det in enumerate(converted_detections):
                    tracked_obj = {
                        'track_id': i,
                        'bbox': det['bbox'],
                        'label': det['label'],
                        'confidence': det['confidence'],
                        'frames_tracked': 1
                    }
                    tracked_objects.append(tracked_obj)
                
                results['tracking'] = tracked_objects
            
            return results
            
        except Exception as e:
            self.logger.error(f"帧处理失败: {e}")
            return results
    
    def get_model_status(self) -> Dict[str, Any]:
        """获取模型状态信息"""
        status = {
            'device': self.device,
            'detection_enabled': self.detection_enabled,
            'use_local_models': self.use_local_models,
            'local_models_dir': self.local_models_dir,
            'models': {},
            'using_fixed_detector': USE_FIXED_DETECTOR
        }
        
        if self.object_detection:
            try:
                status['models'] = self.object_detection.get_model_info()
            except AttributeError:
                # 标准版本可能没有get_model_info方法
                status['models'] = {'status': 'initialized'}
        
        return status
    
    def _record_inference_time(self, time_taken: float):
        """记录推理时间"""
        self.inference_times.append(time_taken)
        if len(self.inference_times) > self.max_history:
            self.inference_times.pop(0)
    
    def get_performance_stats(self) -> Dict[str, float]:
        """
        获取性能统计信息
        
        Returns:
            Dict[str, float]: 性能统计数据
        """
        if not self.inference_times:
            return {}
        
        return {
            'avg_inference_time': np.mean(self.inference_times),
            'min_inference_time': np.min(self.inference_times),
            'max_inference_time': np.max(self.inference_times),
            'std_inference_time': np.std(self.inference_times)
        }
    
    def switch_model(self, model_name: str) -> bool:
        """切换检测模型"""
        if not self.object_detection:
            return False
        
        try:
            return self.object_detection.switch_model(model_name)
        except Exception as e:
            self.logger.error(f"模型切换失败: {e}")
            return False
    
    def cleanup(self):
        """清理AI系统资源"""
        if self.object_detection:
            self.object_detection.cleanup()
        
        self.logger.info("AI系统资源清理完成")
"""
AI System - AI系统管理
使用修复版目标检测器
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional
from pathlib import Path

# 优先使用修复版的目标检测器
try:
    from .object_detection_fixed import ObjectDetectionSystem as FixedObjectDetectionSystem
    USE_FIXED_DETECTOR = True
except ImportError:
    from .object_detection import ObjectDetectionSystem
    USE_FIXED_DETECTOR = False


class AISystem:
    """AI系统管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化AI系统
        
        Args:
            config: AI配置字典
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # AI子系统
        self.object_detection = None
        
        # 设备配置
        self.device = config.get('device', 'auto')
        self.detection_enabled = config.get('detection_enabled', True)
        
        # 本地模型配置
        self.local_models_dir = config.get('local_models_dir', 'models')
        self.use_local_models = config.get('use_local_models', False)
        
        self.logger.info(f"AI系统初始化完成，使用设备: {self.device}")
        if USE_FIXED_DETECTOR:
            self.logger.info("使用修复版目标检测器")
        else:
            self.logger.info("使用标准目标检测器")
    
    def _detect_optimal_device(self) -> str:
        """
        检测最优计算设备
        
        Returns:
            str: 设备名称 ('npu'/'gpu'/'cpu')
        """
        # 优先级: NPU > GPU > CPU
        if self._has_npu_support():
            return 'npu'
        elif torch.cuda.is_available():
            return 'gpu'
        else:
            return 'cpu'
    
    def _has_npu_support(self) -> bool:
        """检测NPU支持"""
        try:
            # 检查高通SNPE或其他NPU SDK
            import snpe  # 高通SNPE SDK
            return True
        except ImportError:
            try:
                # 检查其他NPU支持
                import qti  # 高通QTI
                return True
            except ImportError:
                return False
    
    def initialize(self) -> bool:
        """初始化AI系统"""
        try:
            self.logger.info("开始初始化AI子系统...")
            
            # 只有当检测功能启用时才初始化目标检测系统
            if self.detection_enabled:
                self.logger.info("检测功能已启用，开始初始化目标检测系统...")
                detection_config = self.config.get('object_detection', {})
                
                # 如果启用了本地模型，更新配置
                if self.use_local_models:
                    detection_config['local_models_dir'] = self.local_models_dir
                    self.logger.info(f"启用本地模型模式，目录: {self.local_models_dir}")
                
                from .object_detection import ObjectDetectionSystem
                self.object_detection = ObjectDetectionSystem(detection_config)
                if not self.object_detection.initialize():
                    self.logger.error("目标检测系统初始化失败")
                    return False
                self.logger.info("目标检测系统初始化成功")
            else:
                self.logger.info("检测功能已禁用，跳过目标检测系统初始化")
            
            self.logger.info("AI系统初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"AI系统初始化失败: {e}")
            return False
    
    def load_model(self, model_path: str, framework: str = 'auto') -> bool:
        """
        加载AI模型
        
        Args:
            model_path: 模型文件路径
            framework: 框架类型 ('tensorflow'/'pytorch'/'auto')
            
        Returns:
            bool: 加载是否成功
        """
        try:
            if framework == 'auto':
                framework = self._detect_framework(model_path)
            
            if framework == 'tensorflow':
                return self._load_tensorflow_model(model_path)
            elif framework == 'pytorch':
                return self._load_pytorch_model(model_path)
            else:
                self.logger.error(f"不支持的框架: {framework}")
                return False
                
        except Exception as e:
            self.logger.error(f"模型加载失败: {e}")
            return False
    
    def _detect_framework(self, model_path: str) -> str:
        """自动检测模型框架"""
        if model_path.endswith(('.pb', '.h5', '.keras')):
            return 'tensorflow'
        elif model_path.endswith(('.pt', '.pth')):
            return 'pytorch'
        else:
            return self.framework
    
    def _load_tensorflow_model(self, model_path: str) -> bool:
        """加载TensorFlow模型"""
        try:
            if model_path.endswith('.pb'):
                # 加载SavedModel格式
                self.model = tf.saved_model.load(model_path)
            else:
                # 加载Keras模型
                self.model = tf.keras.models.load_model(model_path)
            
            self.framework = 'tensorflow'
            self.logger.info(f"TensorFlow模型加载成功: {model_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"TensorFlow模型加载失败: {e}")
            return False
    
    def _load_pytorch_model(self, model_path: str) -> bool:
        """加载PyTorch模型"""
        try:
            # 根据设备选择加载方式
            if self.device == 'gpu':
                self.model = torch.load(model_path, map_location='cuda')
            elif self.device == 'npu':
                # NPU特殊加载方式
                self.model = self._load_for_npu(model_path)
            else:
                self.model = torch.load(model_path, map_location='cpu')
            
            # 设置为评估模式
            if hasattr(self.model, 'eval'):
                self.model.eval()
            
            self.framework = 'pytorch'
            self.logger.info(f"PyTorch模型加载成功: {model_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"PyTorch模型加载失败: {e}")
            return False
    
    def _load_for_npu(self, model_path: str):
        """为NPU加载模型"""
        try:
            # 这里应该使用具体的NPU SDK
            # 示例使用SNPE (Snapdragon Neural Processing Engine)
            import snpe
            runtime = snpe.Runtime()  # 这是示意代码
            model = runtime.load_model(model_path)
            return model
        except ImportError:
            self.logger.warning("NPU SDK未安装，使用CPU回退")
            return torch.load(model_path, map_location='cpu')
    
    def process_frame(self, frame_data: Any, delta_time: float = 0.0) -> Dict[str, Any]:
        """
        处理视频帧
        
        Args:
            frame_data: 帧数据
            delta_time: 时间增量
            
        Returns:
            处理结果字典
        """
        results = {
            'timestamp': delta_time,
            'detections': [],
            'tracking': [],
            'features': {}
        }
        
        try:
            # 只有当检测功能启用且检测系统存在时才进行处理
            if self.object_detection and self.detection_enabled:
                # 处理不同类型的输入数据
                if hasattr(frame_data, 'shape'):  # numpy array
                    detections = self.object_detection.process_frame(frame_data)
                else:  # 其他类型的数据
                    import numpy as np
                    # 创建一个简单的测试图像
                    dummy_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
                    detections = self.object_detection.process_frame(dummy_frame)
                
                # 转换检测结果格式
                converted_detections = []
                for det in detections:
                    converted_detections.append({
                        'bbox': det.bbox,
                        'label': det.label,
                        'confidence': det.confidence,
                        'class_id': det.class_id
                    })
                
                results['detections'] = converted_detections
                
                # 简单的跟踪模拟
                tracked_objects = []
                for i, det in enumerate(converted_detections):
                    tracked_obj = {
                        'track_id': i,
                        'bbox': det['bbox'],
                        'label': det['label'],
                        'confidence': det['confidence'],
                        'frames_tracked': 1
                    }
                    tracked_objects.append(tracked_obj)
                
                results['tracking'] = tracked_objects
            
            return results
            
        except Exception as e:
            self.logger.error(f"帧处理失败: {e}")
            return results
    
    def get_model_status(self) -> Dict[str, Any]:
        """获取模型状态信息"""
        status = {
            'device': self.device,
            'detection_enabled': self.detection_enabled,
            'use_local_models': self.use_local_models,
            'local_models_dir': self.local_models_dir,
            'models': {},
            'using_fixed_detector': USE_FIXED_DETECTOR
        }
        
        if self.object_detection:
            try:
                status['models'] = self.object_detection.get_model_info()
            except AttributeError:
                # 标准版本可能没有get_model_info方法
                status['models'] = {'status': 'initialized'}
        
        return status
    
    def _record_inference_time(self, time_taken: float):
        """记录推理时间"""
        self.inference_times.append(time_taken)
        if len(self.inference_times) > self.max_history:
            self.inference_times.pop(0)
    
    def get_performance_stats(self) -> Dict[str, float]:
        """
        获取性能统计信息
        
        Returns:
            Dict[str, float]: 性能统计数据
        """
        if not self.inference_times:
            return {}
        
        return {
            'avg_inference_time': np.mean(self.inference_times),
            'min_inference_time': np.min(self.inference_times),
            'max_inference_time': np.max(self.inference_times),
            'std_inference_time': np.std(self.inference_times)
        }
    
    def switch_model(self, model_name: str) -> bool:
        """切换检测模型"""
        if not self.object_detection:
            return False
        
        try:
            return self.object_detection.switch_model(model_name)
        except Exception as e:
            self.logger.error(f"模型切换失败: {e}")
            return False
    
    def cleanup(self):
        """清理AI系统资源"""
        if self.object_detection:
            self.object_detection.cleanup()
        
        self.logger.info("AI系统资源清理完成")
