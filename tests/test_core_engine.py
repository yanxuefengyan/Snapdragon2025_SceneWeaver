"""
Core Engine 单元测试
"""

import unittest
import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.engine import CoreEngine
from utils.config_manager import ConfigManager


class TestCoreEngine(unittest.TestCase):
    """CoreEngine测试类"""
    
    def setUp(self):
        """测试前准备"""
        config_manager = ConfigManager()
        self.config = config_manager.get_config()
        self.engine = CoreEngine(self.config)
    
    def test_engine_initialization(self):
        """测试引擎初始化"""
        self.assertIsNotNone(self.engine)
        self.assertEqual(self.engine.target_fps, 60)
        self.assertFalse(self.engine.running)
    
    def test_config_loading(self):
        """测试配置加载"""
        self.assertIn('graphics', self.config)
        self.assertIn('ai', self.config)
        self.assertIn('input', self.config)
    
    def tearDown(self):
        """测试后清理"""
        pass


if __name__ == '__main__':
    unittest.main()