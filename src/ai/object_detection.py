"""
Object Detection - 目标检测系统
集成预训练的目标检测模型，支持实时物体识别
"""

import logging
import numpy as np
import os
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod

try:
    import cv2
    import torch
    import torchvision
    from torchvision import transforms
except ImportError as e:
    print(f"AI依赖导入失败: {e}")


@dataclass
class DetectedObject:
    """检测到的对象数据类"""
    label: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    x: float  # 中心点x坐标
    y: float  # 中心点y坐标
    class_id: int


class BaseDetector(ABC):
    """目标检测器基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.device = self._setup_device()
        self.class_names = []
    
    def _setup_device(self) -> str:
        """设置计算设备"""
        if torch.cuda.is_available():
            return 'cuda'
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return 'mps'
        else:
            return 'cpu'
    
    @abstractmethod
    def load_model(self, model_path: str = None):
        """加载模型"""
        pass
    
    @abstractmethod
    def detect(self, image: np.ndarray) -> List[DetectedObject]:
        """执行检测"""
        pass
    
    def preprocess_image(self, image: np.ndarray) -> torch.Tensor:
        """预处理图像"""
        # 转换为RGB
        if len(image.shape) == 3 and image.shape[2] == 3:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = image
        
        # 调整大小
        input_size = self.config.get('input_size', 640)
        resized = cv2.resize(rgb_image, (input_size, input_size))
        
        # 转换为tensor
        tensor = torch.from_numpy(resized).float()
        tensor = tensor.permute(2, 0, 1)  # HWC to CHW
        tensor = tensor.unsqueeze(0)  # 添加batch维度
        tensor = tensor / 255.0  # 归一化到[0,1]
        
        return tensor.to(self.device)
    
    def postprocess_detections(self, detections, original_shape: Tuple[int, int]) -> List[DetectedObject]:
        """后处理检测结果"""
        objects = []
        threshold = self.config.get('confidence_threshold', 0.5)
        
        if detections is None or len(detections) == 0:
            return objects
        
        orig_h, orig_w = original_shape[:2]
        input_size = self.config.get('input_size', 640)
        
        # 缩放因子
        scale_x = orig_w / input_size
        scale_y = orig_h / input_size
        
        for detection in detections:
            if len(detection) >= 6:  # 确保有足够的元素
                x1, y1, x2, y2, conf, cls_id = detection[:6]
                
                if conf >= threshold:
                    # 转换坐标到原始图像尺寸
                    x1_orig = int(x1 * scale_x)
                    y1_orig = int(y1 * scale_y)
                    x2_orig = int(x2 * scale_x)
                    y2_orig = int(y2 * scale_y)
                    
                    width = x2_orig - x1_orig
                    height = y2_orig - y1_orig
                    center_x = (x1_orig + x2_orig) / 2
                    center_y = (y1_orig + y2_orig) / 2
                    
                    # 获取标签名称
                    label = self.class_names[int(cls_id)] if int(cls_id) < len(self.class_names) else f"class_{int(cls_id)}"
                    
                    obj = DetectedObject(
                        label=label,
                        confidence=float(conf),
                        bbox=(x1_orig, y1_orig, width, height),
                        x=center_x,
                        y=center_y,
                        class_id=int(cls_id)
                    )
                    objects.append(obj)
        
        return objects


class YOLODetector(BaseDetector):
    """YOLO目标检测器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # COCO数据集类别名称
        self.class_names = [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train',
            'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign',
            'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep',
            'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella',
            'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard',
            'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard',
            'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork',
            'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
            'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair',
            'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv',
            'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave',
            'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase',
            'scissors', 'teddy bear', 'hair drier', 'toothbrush'
        ]
        
        # 本地模型相关配置
        self.local_models_dir = config.get('local_models_dir')
        self.use_local_model = config.get('use_local_model', False)
        
        self.logger.info(f"YOLODetector初始化完成，使用设备: {self.device}")
    
    def _get_local_model_path(self) -> str:
        """获取本地模型文件路径"""
        if not self.local_models_dir or not self.use_local_model:
            return None
            
        import os
        model_filenames = {
            'yolov5s': 'yolov5s.pt',
            'yolov5m': 'yolov5m.pt',
            'yolov5l': 'yolov5l.pt',
            'yolov5x': 'yolov5x.pt'
        }
        
        model_name = self.config.get('model_name', 'yolov5s')
        filename = model_filenames.get(model_name, f"{model_name}.pt")
        local_path = os.path.join(self.local_models_dir, filename)
        
        return local_path if os.path.exists(local_path) else None
    
    def load_model(self, model_path: str = None):
        """加载YOLO模型，优先使用本地模型"""
        try:
            # 优先使用指定的模型路径
            if model_path and model_path.endswith('.pt'):
                if os.path.exists(model_path):
                    self.logger.info(f"加载指定的本地模型: {model_path}")
                    # 使用torch.hub的自定义模型加载方式
                    self.model = torch.hub.load(
                        'ultralytics/yolov5',
                        'custom',
                        path=model_path,
                        device=self.device
                    )
                    return True
                else:
                    self.logger.warning(f"指定的模型文件不存在: {model_path}")
            
            # 尝试加载本地目录中的模型
            local_model_path = self._get_local_model_path()
            if local_model_path:
                self.logger.info(f"加载本地模型: {local_model_path}")
                self.model = torch.hub.load(
                    'ultralytics/yolov5',
                    'custom',
                    path=local_model_path,
                    device=self.device
                )
            else:
                # 加载预训练模型
                model_name = self.config.get('model_name', 'yolov5s')
                self.logger.info(f"从网络加载预训练模型: {model_name}")
                self.model = torch.hub.load(
                    'ultralytics/yolov5', 
                    model_name, 
                    pretrained=True,
                    device=self.device
                )
            
            self.model.eval()
            self.logger.info("YOLO模型加载成功")
            return True
            
        except Exception as e:
            self.logger.error(f"YOLO模型加载失败: {e}")
            # 使用简化版本
            self._load_dummy_model()
            return False
    
    def _load_dummy_model(self):
        """加载简化模型（用于演示）"""
        self.logger.warning("使用简化检测模型")
        self.model = DummyYOLOModel()
    
    def detect(self, image: np.ndarray) -> List[DetectedObject]:
        """执行YOLO检测"""
        if self.model is None:
            return []
        
        try:
            # 预处理
            input_tensor = self.preprocess_image(image)
            
            # 推理
            with torch.no_grad():
                results = self.model(input_tensor)
            
            # 后处理
            if hasattr(results, 'xyxy'):  # YOLOv5格式
                detections = results.xyxy[0].cpu().numpy()
            elif isinstance(results, torch.Tensor):  # 简化模型格式
                detections = results.cpu().numpy()
            else:
                detections = []
            
            return self.postprocess_detections(detections, image.shape)
            
        except Exception as e:
            self.logger.error(f"检测过程出错: {e}")
            return []


class SSDDetector(BaseDetector):
    """SSD目标检测器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # 本地模型相关配置
        self.local_models_dir = config.get('local_models_dir')
        self.use_local_model = config.get('use_local_model', False)
        
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        # COCO类别
        self.class_names = [
            '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
            'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant',
            'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse',
            'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
            'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis',
            'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
            'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass',
            'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
            'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
            'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
            'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
            'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
            'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
            'hair drier', 'toothbrush'
        ]
    
    def _get_local_model_path(self) -> str:
        """获取本地模型文件路径"""
        if not self.local_models_dir or not self.use_local_model:
            return None
            
        import os
        model_filename = "ssd_model.pth"
        local_path = os.path.join(self.local_models_dir, model_filename)
        
        return local_path if os.path.exists(local_path) else None
    
    def load_model(self, model_path: str = None):
        """加载SSD模型，优先使用本地模型"""
        try:
            # 优先使用指定的模型路径
            if model_path and os.path.exists(model_path):
                self.logger.info(f"加载指定的本地模型: {model_path}")
                self.model = torch.load(model_path, map_location=self.device)
            else:
                # 尝试加载本地目录中的模型
                local_model_path = self._get_local_model_path()
                if local_model_path:
                    self.logger.info(f"加载本地SSD模型: {local_model_path}")
                    self.model = torch.load(local_model_path, map_location=self.device)
                else:
                    # 加载预训练模型
                    self.logger.info("加载预训练SSD模型")
                    self.model = torchvision.models.detection.ssd300_vgg16(
                        pretrained=True,
                        pretrained_backbone=True
                    )
            
            self.model.to(self.device)
            self.model.eval()
            self.logger.info("SSD模型加载成功")
            return True
            
        except Exception as e:
            self.logger.error(f"SSD模型加载失败: {e}")
            return False
    
    def detect(self, image: np.ndarray) -> List[DetectedObject]:
        """执行SSD检测"""
        if self.model is None:
            return []
        
        try:
            # 转换为RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 预处理
            pil_image = torchvision.transforms.functional.to_pil_image(rgb_image)
            tensor = self.transform(pil_image).unsqueeze(0).to(self.device)
            
            # 推理
            with torch.no_grad():
                predictions = self.model(tensor)
            
            # 后处理
            objects = []
            threshold = self.config.get('confidence_threshold', 0.5)
            
            boxes = predictions[0]['boxes'].cpu().numpy()
            labels = predictions[0]['labels'].cpu().numpy()
            scores = predictions[0]['scores'].cpu().numpy()
            
            h, w = image.shape[:2]
            
            for box, label, score in zip(boxes, labels, scores):
                if score >= threshold and label < len(self.class_names):
                    x1, y1, x2, y2 = box.astype(int)
                    width = x2 - x1
                    height = y2 - y1
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2
                    
                    obj = DetectedObject(
                        label=self.class_names[label],
                        confidence=float(score),
                        bbox=(x1, y1, width, height),
                        x=center_x,
                        y=center_y,
                        class_id=int(label)
                    )
                    objects.append(obj)
            
            return objects
            
        except Exception as e:
            self.logger.error(f"SSD检测出错: {e}")
            return []


class DummyYOLOModel:
    """简化YOLO模型（用于演示和测试）"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def __call__(self, x):
        """模拟YOLO推理"""
        batch_size = x.shape[0]
        # 生成一些假的检测结果
        # 格式: [x1, y1, x2, y2, confidence, class_id]
        dummy_detections = [
            [100, 100, 200, 200, 0.85, 0],  # person
            [300, 150, 400, 250, 0.75, 2],  # car
            [500, 200, 550, 300, 0.90, 15], # dog
        ]
        
        # 转换为tensor
        result = torch.tensor(dummy_detections, dtype=torch.float32)
        # 添加batch维度
        return result.unsqueeze(0).repeat(batch_size, 1, 1)


class ObjectDetectionSystem:
    """目标检测系统管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 选择检测器类型
        detector_type = config.get('detector_type', 'yolo').lower()
        
        # 创建对应类型的检测器
        if detector_type == 'ssd':
            self.detector = SSDDetector(config)
            self.logger.info(f"使用SSD检测器，本地模型支持: {config.get('use_local_model', False)}")
        elif detector_type == 'yolo':
            self.detector = YOLODetector(config)
            self.logger.info(f"使用YOLO检测器，本地模型支持: {config.get('use_local_model', False)}")
        else:
            self.logger.warning(f"未知检测器类型: {detector_type}，默认使用YOLO检测器")
            self.detector = YOLODetector(config)
        
        # 检测状态
        self.enabled = config.get('enabled', True)
        self.last_detections = []
        self.detection_interval = config.get('detection_interval', 1)  # 每N帧检测一次
        self.frame_count = 0
        
        self.logger.info(f"ObjectDetectionSystem初始化完成，检测器类型: {detector_type}")
    
    def initialize(self) -> bool:
        """初始化检测系统"""
        try:
            model_loaded = self.detector.load_model(
                self.config.get('model_path')
            )
            return model_loaded
        except Exception as e:
            self.logger.error(f"检测系统初始化失败: {e}")
            return False
    
    def process_frame(self, frame: np.ndarray) -> List[DetectedObject]:
        """处理视频帧"""
        if not self.enabled:
            return []
        
        self.frame_count += 1
        
        # 按间隔进行检测
        if self.frame_count % self.detection_interval != 0:
            return self.last_detections
        
        try:
            detections = self.detector.detect(frame)
            self.last_detections = detections
            return detections
        except Exception as e:
            self.logger.error(f"帧处理出错: {e}")
            return self.last_detections
    
    def draw_detections(self, frame: np.ndarray, detections: List[DetectedObject]) -> np.ndarray:
        """在图像上绘制检测结果"""
        if not detections:
            return frame
        
        result_frame = frame.copy()
        
        for obj in detections:
            x, y, w, h = obj.bbox
            
            # 绘制边界框
            cv2.rectangle(result_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # 绘制标签
            label = f"{obj.label}: {obj.confidence:.2f}"
            cv2.putText(result_frame, label, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # 绘制中心点
            cv2.circle(result_frame, (int(obj.x), int(obj.y)), 3, (255, 0, 0), -1)
        
        return result_frame
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取检测统计信息"""
        class_counts = {}
        total_confidence = 0.0
        
        for obj in self.last_detections:
            class_counts[obj.label] = class_counts.get(obj.label, 0) + 1
            total_confidence += obj.confidence
        
        avg_confidence = total_confidence / len(self.last_detections) if self.last_detections else 0.0
        
        return {
            'total_objects': len(self.last_detections),
            'class_distribution': class_counts,
            'average_confidence': avg_confidence,
            'frame_count': self.frame_count
        }
    
    def set_enabled(self, enabled: bool):
        """启用/禁用检测"""
        self.enabled = enabled
        if not enabled:
            self.last_detections = []
    
    def cleanup(self):
        """清理资源"""
        self.logger.info("ObjectDetectionSystem资源清理完成")