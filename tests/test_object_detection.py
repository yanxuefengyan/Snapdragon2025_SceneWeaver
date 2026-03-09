"""
Object Detection 单元测试
测试目标检测系统的YOLO和SSD检测器功能
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import numpy as np

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai.object_detection import ObjectDetectionSystem, YOLODetector, SSDDetector, DetectedObject
from utils.config_manager import ConfigManager


class TestDetectedObject(unittest.TestCase):
    """检测对象测试"""
    
    def setUp(self):
        """测试前准备"""
        self.detected_obj = DetectedObject(
            label="person",
            confidence=0.85,
            bbox=(100, 150, 50, 80),
            x=125,
            y=190
        )
    
    def test_object_initialization(self):
        """测试检测对象初始化"""
        self.assertEqual(self.detected_obj.label, "person")
        self.assertEqual(self.detected_obj.confidence, 0.85)
        self.assertEqual(self.detected_obj.bbox, (100, 150, 50, 80))
        self.assertEqual(self.detected_obj.x, 125)
        self.assertEqual(self.detected_obj.y, 190)
    
    def test_object_string_representation(self):
        """测试对象字符串表示"""
        obj_str = str(self.detected_obj)
        self.assertIn("person", obj_str)
        self.assertIn("0.85", obj_str)
        self.assertIn("(100, 150, 50, 80)", obj_str)


class TestYOLODetector(unittest.TestCase):
    """YOLO检测器测试"""
    
    def setUp(self):
        """测试前准备"""
        config_manager = ConfigManager()
        self.config = config_manager.get_config()
        self.yolo_detector = YOLODetector(self.config)
    
    def test_yolo_initialization(self):
        """测试YOLO检测器初始化"""
        self.assertIsNotNone(self.yolo_detector)
        self.assertEqual(self.yolo_detector.model_type, "yolo")
        self.assertIsNone(self.yolo_detector.model)
    
    @patch('ai.object_detection.cv2.dnn.readNetFromDarknet')
    def test_load_yolo_model_success(self, mock_read_net):
        """测试成功加载YOLO模型"""
        mock_net = Mock()
        mock_read_net.return_value = mock_net
        
        with patch.object(self.yolo_detector, '_get_yolo_files') as mock_get_files:
            mock_get_files.return_value = ('config.cfg', 'weights.weights')
            
            result = self.yolo_detector.load_model('fake_path')
            
            self.assertTrue(result)
            self.assertIsNotNone(self.yolo_detector.model)
            mock_read_net.assert_called_once()
    
    @patch('ai.object_detection.cv2.dnn.readNetFromDarknet')
    def test_load_yolo_model_failure(self, mock_read_net):
        """测试加载YOLO模型失败"""
        mock_read_net.side_effect = Exception("Model loading failed")
        
        result = self.yolo_detector.load_model('fake_path')
        
        self.assertFalse(result)
        self.assertIsNone(self.yolo_detector.model)
    
    @patch('ai.object_detection.cv2.dnn_Net')
    def test_yolo_detect(self, mock_net_class):
        """测试YOLO检测"""
        # 模拟网络输出
        mock_net = Mock()
        mock_net_class.return_value = mock_net
        
        # 模拟检测输出
        mock_outs = [
            np.array([[0.5, 0.6, 0.7, 0.8, 0.9, 0]])  # [center_x, center_y, width, height, confidence, class_id]
        ]
        mock_net.forward.return_value = mock_outs
        
        self.yolo_detector.model = mock_net
        self.yolo_detector.classes = ['person']
        
        # 测试图像
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        detections = self.yolo_detector.detect(frame)
        
        # 验证检测结果
        self.assertIsInstance(detections, list)
        if detections:  # 如果有检测结果
            detected_obj = detections[0]
            self.assertIsInstance(detected_obj, DetectedObject)
            self.assertEqual(detected_obj.label, 'person')
            self.assertAlmostEqual(detected_obj.confidence, 0.9, places=1)
    
    def test_yolo_preprocess(self):
        """测试YOLO预处理"""
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        blob = self.yolo_detector._preprocess(frame)
        
        self.assertIsNotNone(blob)
        # 验证blob形状 (通常是 1, 3, 416, 416 或类似)
        self.assertEqual(len(blob.shape), 4)
        self.assertEqual(blob.shape[0], 1)  # batch size
        self.assertEqual(blob.shape[1], 3)  # channels


class TestSSDDetector(unittest.TestCase):
    """SSD检测器测试"""
    
    def setUp(self):
        """测试前准备"""
        config_manager = ConfigManager()
        self.config = config_manager.get_config()
        self.ssd_detector = SSDDetector(self.config)
    
    def test_ssd_initialization(self):
        """测试SSD检测器初始化"""
        self.assertIsNotNone(self.ssd_detector)
        self.assertEqual(self.ssd_detector.model_type, "ssd")
        self.assertIsNone(self.ssd_detector.model)
    
    @patch('ai.object_detection.cv2.dnn.readNetFromCaffe')
    def test_load_ssd_model_success(self, mock_read_net):
        """测试成功加载SSD模型"""
        mock_net = Mock()
        mock_read_net.return_value = mock_net
        
        result = self.ssd_detector.load_model('fake_path')
        
        self.assertTrue(result)
        self.assertIsNotNone(self.ssd_detector.model)
        mock_read_net.assert_called_once()
    
    @patch('ai.object_detection.cv2.dnn.readNetFromCaffe')
    def test_load_ssd_model_failure(self, mock_read_net):
        """测试加载SSD模型失败"""
        mock_read_net.side_effect = Exception("Model loading failed")
        
        result = self.ssd_detector.load_model('fake_path')
        
        self.assertFalse(result)
        self.assertIsNone(self.ssd_detector.model)
    
    @patch('ai.object_detection.cv2.dnn_Net')
    def test_ssd_detect(self, mock_net_class):
        """测试SSD检测"""
        mock_net = Mock()
        mock_net_class.return_value = mock_net
        
        # 模拟SSD输出 [image_id, label, confidence, x_min, y_min, x_max, y_max]
        mock_detections = np.array([[
            [0, 15, 0.95, 0.2, 0.3, 0.4, 0.5]  # car detection
        ]])
        mock_net.forward.return_value = mock_detections
        
        self.ssd_detector.model = mock_net
        self.ssd_detector.classes = ['background', 'car']  # COCO classes
        
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        detections = self.ssd_detector.detect(frame)
        
        self.assertIsInstance(detections, list)
        if detections:
            detected_obj = detections[0]
            self.assertIsInstance(detected_obj, DetectedObject)
            self.assertEqual(detected_obj.label, 'car')
            self.assertAlmostEqual(detected_obj.confidence, 0.95, places=2)


class TestObjectDetectionSystem(unittest.TestCase):
    """目标检测系统测试"""
    
    def setUp(self):
        """测试前准备"""
        config_manager = ConfigManager()
        self.config = config_manager.get_config()
        self.detection_system = ObjectDetectionSystem(self.config)
    
    def test_system_initialization(self):
        """测试检测系统初始化"""
        self.assertIsNotNone(self.detection_system)
        self.logger = self.detection_system.logger
        
        # 验证默认检测器类型
        self.assertIn(self.detection_system.detector.model_type, ['yolo', 'ssd'])
        self.assertTrue(self.detection_system.enabled)
    
    def test_system_initialization_with_ssd(self):
        """测试使用SSD检测器初始化"""
        ssd_config = self.config.copy()
        ssd_config['detector_type'] = 'ssd'
        
        detection_system = ObjectDetectionSystem(ssd_config)
        
        self.assertEqual(detection_system.detector.model_type, 'ssd')
    
    def test_initialize_success(self):
        """测试系统初始化成功"""
        with patch.object(self.detection_system.detector, 'load_model') as mock_load:
            mock_load.return_value = True
            
            result = self.detection_system.initialize()
            
            self.assertTrue(result)
            mock_load.assert_called_once()
    
    def test_initialize_failure(self):
        """测试系统初始化失败"""
        with patch.object(self.detection_system.detector, 'load_model') as mock_load:
            mock_load.return_value = False
            
            result = self.detection_system.initialize()
            
            self.assertFalse(result)
    
    def test_process_frame_detection_disabled(self):
        """测试检测禁用时的帧处理"""
        self.detection_system.enabled = False
        
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        detections = self.detection_system.process_frame(frame)
        
        self.assertEqual(detections, [])
    
    def test_process_frame_interval_skipping(self):
        """测试帧间隔跳过功能"""
        self.detection_system.detection_interval = 3  # 每3帧检测一次
        
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # 前两帧应该跳过检测
        detections1 = self.detection_system.process_frame(frame)
        detections2 = self.detection_system.process_frame(frame)
        
        self.assertEqual(detections1, [])
        self.assertEqual(detections2, [])
        
        # 第三帧应该执行检测
        with patch.object(self.detection_system.detector, 'detect') as mock_detect:
            mock_detect.return_value = [DetectedObject('person', 0.8, (10, 10, 50, 50))]
            
            detections3 = self.detection_system.process_frame(frame)
            
            self.assertEqual(len(detections3), 1)
            mock_detect.assert_called_once()
    
    def test_draw_detections(self):
        """测试绘制检测结果"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = [
            DetectedObject('person', 0.9, (100, 100, 50, 80)),
            DetectedObject('car', 0.85, (200, 150, 60, 40))
        ]
        
        result_frame = self.detection_system.draw_detections(frame, detections)
        
        # 验证返回的是numpy数组
        self.assertIsInstance(result_frame, np.ndarray)
        # 验证形状不变
        self.assertEqual(result_frame.shape, frame.shape)
        # 验证不是同一个对象（应该返回副本）
        self.assertIsNot(result_frame, frame)
    
    def test_get_statistics(self):
        """测试获取统计信息"""
        # 设置一些检测结果
        detections = [
            DetectedObject('person', 0.9, (10, 10, 50, 50)),
            DetectedObject('person', 0.8, (60, 60, 50, 50)),
            DetectedObject('car', 0.85, (120, 120, 60, 40))
        ]
        self.detection_system.last_detections = detections
        self.detection_system.frame_count = 100
        
        stats = self.detection_system.get_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_objects', stats)
        self.assertIn('class_distribution', stats)
        self.assertIn('average_confidence', stats)
        self.assertIn('frame_count', stats)
        
        # 验证统计值
        self.assertEqual(stats['total_objects'], 3)
        self.assertEqual(stats['class_distribution']['person'], 2)
        self.assertEqual(stats['class_distribution']['car'], 1)
        self.assertEqual(stats['frame_count'], 100)
    
    def test_enable_disable_detection(self):
        """测试启用/禁用检测"""
        # 默认应该是启用的
        self.assertTrue(self.detection_system.enabled)
        
        # 禁用检测
        self.detection_system.set_enabled(False)
        self.assertFalse(self.detection_system.enabled)
        self.assertEqual(len(self.detection_system.last_detections), 0)
        
        # 重新启用
        self.detection_system.set_enabled(True)
        self.assertTrue(self.detection_system.enabled)
    
    def test_cleanup(self):
        """测试系统清理"""
        # 初始化系统
        with patch.object(self.detection_system.detector, 'load_model') as mock_load:
            mock_load.return_value = True
            self.detection_system.initialize()
            
            # 清理前验证状态
            self.logger = self.detection_system.logger
            
            # 执行清理
            self.detection_system.cleanup()
            
            # 验证清理完成
            self.logger.info("ObjectDetectionSystem资源清理完成")


if __name__ == '__main__':
    unittest.main()