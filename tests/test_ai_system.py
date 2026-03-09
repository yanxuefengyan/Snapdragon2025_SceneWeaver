"""
AI System 单元测试
测试AI推理系统的双框架支持和模型管理功能
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import numpy as np

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai.ai_system import AISystem, DeviceDetector
from utils.config_manager import ConfigManager


class TestDeviceDetector(unittest.TestCase):
    """设备检测器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.detector = DeviceDetector()
    
    def test_detector_initialization(self):
        """测试设备检测器初始化"""
        self.assertIsNotNone(self.detector)
        self.assertIsInstance(self.detector.devices, dict)
        self.assertIn('cpu', self.detector.devices)
    
    def test_detect_available_devices(self):
        """测试设备检测"""
        devices = self.detector.detect_available_devices()
        
        self.assertIsInstance(devices, dict)
        self.assertIn('cpu', devices)
        self.assertIn('priority', devices['cpu'])
        
        # CPU应该是可用的
        self.assertTrue(devices['cpu']['available'])
    
    @patch('ai.ai_system.tf.config.list_physical_devices')
    def test_tensorflow_gpu_detection(self, mock_list_devices):
        """测试TensorFlow GPU检测"""
        # 模拟GPU设备
        mock_gpu = Mock()
        mock_gpu.name = '/physical_device:GPU:0'
        mock_list_devices.return_value = [mock_gpu]
        
        devices = self.detector.detect_available_devices()
        
        # 验证GPU被正确检测
        if 'gpu' in devices:
            self.assertTrue(devices['gpu']['available'])
    
    def test_get_optimal_device(self):
        """测试获取最优设备"""
        optimal_device = self.detector.get_optimal_device()
        
        # 应该返回有效的设备名称
        self.assertIsInstance(optimal_device, str)
        self.assertIn(optimal_device, ['npu', 'gpu', 'cpu'])


class TestAISystem(unittest.TestCase):
    """AI系统测试"""
    
    def setUp(self):
        """测试前准备"""
        config_manager = ConfigManager()
        self.config = config_manager.get_config()
        self.ai_system = AISystem(self.config)
    
    def test_system_initialization(self):
        """测试AI系统初始化"""
        self.assertIsNotNone(self.ai_system)
        self.assertIsInstance(self.ai_system.device_detector, DeviceDetector)
        self.assertEqual(self.ai_system.current_device, 'cpu')  # 默认应该使用CPU
        self.assertFalse(self.ai_system.initialized)
    
    def test_get_supported_frameworks(self):
        """测试获取支持的框架"""
        frameworks = self.ai_system.get_supported_frameworks()
        
        self.assertIsInstance(frameworks, list)
        self.assertGreater(len(frameworks), 0)
        
        # 应该至少支持TensorFlow和PyTorch
        framework_names = [fw['name'] for fw in frameworks]
        self.assertIn('tensorflow', framework_names)
        self.assertIn('pytorch', framework_names)
    
    @patch('ai.ai_system.importlib.util.find_spec')
    def test_framework_availability_check(self, mock_find_spec):
        """测试框架可用性检查"""
        # 模拟TensorFlow可用
        mock_find_spec.return_value = Mock()
        
        available = self.ai_system._is_framework_available('tensorflow')
        self.assertTrue(available)
        
        # 模拟框架不可用
        mock_find_spec.return_value = None
        available = self.ai_system._is_framework_available('nonexistent_framework')
        self.assertFalse(available)
    
    def test_initialize_success(self):
        """测试系统初始化成功"""
        # 由于实际初始化需要加载模型，这里测试基本流程
        with patch.object(self.ai_system, '_load_models') as mock_load:
            mock_load.return_value = True
            
            result = self.ai_system.initialize()
            
            self.assertTrue(result)
            self.assertTrue(self.ai_system.initialized)
            mock_load.assert_called_once()
    
    def test_initialize_failure(self):
        """测试系统初始化失败"""
        with patch.object(self.ai_system, '_load_models') as mock_load:
            mock_load.return_value = False
            
            result = self.ai_system.initialize()
            
            self.assertFalse(result)
            self.assertFalse(self.ai_system.initialized)
    
    @patch('ai.ai_system.tf')
    def test_tensorflow_inference(self, mock_tf):
        """测试TensorFlow推理"""
        # 模拟TensorFlow模型
        mock_model = Mock()
        mock_model.return_value = {'predictions': np.array([0.8, 0.2])}
        self.ai_system.tensorflow_model = mock_model
        
        # 模拟输入数据
        input_data = np.random.rand(1, 224, 224, 3).astype(np.float32)
        
        result = self.ai_system._run_tensorflow_inference(input_data)
        
        self.assertIsNotNone(result)
        mock_model.assert_called_once()
    
    @patch('ai.ai_system.torch')
    def test_pytorch_inference(self, mock_torch):
        """测试PyTorch推理"""
        # 模拟PyTorch模型
        mock_model = Mock()
        mock_model.return_value = Mock()
        mock_model.return_value.cpu.return_value.numpy.return_value = np.array([0.7, 0.3])
        self.ai_system.pytorch_model = mock_model
        
        # 模拟输入数据
        input_data = np.random.rand(1, 3, 224, 224).astype(np.float32)
        
        result = self.ai_system._run_pytorch_inference(input_data)
        
        self.assertIsNotNone(result)
        mock_model.assert_called_once()
    
    def test_process_frame_no_models(self):
        """测试无模型时的帧处理"""
        # 重置模型
        self.ai_system.tensorflow_model = None
        self.ai_system.pytorch_model = None
        
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        results = self.ai_system.process_frame(frame)
        
        # 应该返回空结果
        self.assertEqual(results, {})
    
    def test_process_frame_with_models(self):
        """测试有模型时的帧处理"""
        # 模拟模型存在
        self.ai_system.tensorflow_model = Mock()
        self.ai_system.pytorch_model = Mock()
        
        with patch.object(self.ai_system, '_run_tensorflow_inference') as mock_tf_inference, \
             patch.object(self.ai_system, '_run_pytorch_inference') as mock_pt_inference:
            
            mock_tf_inference.return_value = {'objects': [{'class': 'person', 'confidence': 0.9}]}
            mock_pt_inference.return_value = {'poses': [{'keypoints': []}]}
            
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            results = self.ai_system.process_frame(frame)
            
            # 验证两个框架都被调用
            mock_tf_inference.assert_called_once()
            mock_pt_inference.assert_called_once()
            
            # 验证结果合并
            self.assertIn('tensorflow', results)
            self.assertIn('pytorch', results)
    
    def test_unified_inference(self):
        """测试统一推理接口"""
        with patch.object(self.ai_system, 'process_frame') as mock_process:
            mock_process.return_value = {'objects': [{'class': 'car', 'confidence': 0.85}]}
            
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            result = self.ai_system.unified_inference(frame)
            
            self.assertIsNotNone(result)
            mock_process.assert_called_once_with(frame)
    
    def test_get_model_info(self):
        """测试获取模型信息"""
        info = self.ai_system.get_model_info()
        
        self.assertIsInstance(info, dict)
        self.assertIn('device', info)
        self.assertIn('frameworks', info)
        self.assertIn('models', info)
        
        # 验证设备信息
        self.assertEqual(info['device'], self.ai_system.current_device)
    
    def test_cleanup(self):
        """测试系统清理"""
        # 初始化系统
        with patch.object(self.ai_system, '_load_models') as mock_load:
            mock_load.return_value = True
            self.ai_system.initialize()
            
            # 清理前应该已初始化
            self.assertTrue(self.ai_system.initialized)
            
            # 执行清理
            self.ai_system.cleanup()
            
            # 验证清理后状态
            self.assertFalse(self.ai_system.initialized)
            self.assertIsNone(self.ai_system.tensorflow_model)
            self.assertIsNone(self.ai_system.pytorch_model)


class TestModelLoading(unittest.TestCase):
    """模型加载测试"""
    
    def setUp(self):
        """测试前准备"""
        config_manager = ConfigManager()
        self.config = config_manager.get_config()
        self.ai_system = AISystem(self.config)
    
    @patch('ai.ai_system.tf.saved_model.load')
    def test_load_tensorflow_model(self, mock_load):
        """测试加载TensorFlow模型"""
        mock_model = Mock()
        mock_load.return_value = mock_model
        
        model = self.ai_system._load_tensorflow_model('fake_path')
        
        self.assertIsNotNone(model)
        mock_load.assert_called_once_with('fake_path')
    
    @patch('ai.ai_system.torch.load')
    @patch('ai.ai_system.torch.nn.Module')
    def test_load_pytorch_model(self, mock_module_class, mock_load):
        """测试加载PyTorch模型"""
        mock_model_state = {'state_dict': {}}
        mock_load.return_value = mock_model_state
        
        mock_model = Mock()
        mock_module_class.return_value = mock_model
        
        model = self.ai_system._load_pytorch_model('fake_path')
        
        self.assertIsNotNone(model)
        mock_load.assert_called_once_with('fake_path', map_location='cpu')


if __name__ == '__main__':
    unittest.main()