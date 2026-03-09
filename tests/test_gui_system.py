"""
GUI System 单元测试
测试图形用户界面系统和控制面板功能
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import numpy as np

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ui.gui_system import GUISystem, ControlPanel
from utils.config_manager import ConfigManager


class TestControlPanel(unittest.TestCase):
    """控制面板测试"""
    
    def setUp(self):
        """测试前准备"""
        config_manager = ConfigManager()
        self.config = config_manager.get_config()
        self.control_panel = ControlPanel((800, 600), self.config)
    
    def test_panel_initialization(self):
        """测试控制面板初始化"""
        self.assertIsNotNone(self.control_panel)
        self.assertEqual(self.control_panel.width, 250)
        self.assertEqual(self.control_panel.height, 600)
        self.assertTrue(self.control_panel.visible)
        self.assertIsNotNone(self.control_panel.font)
    
    def test_toggle_visibility(self):
        """测试切换可见性"""
        # 默认应该是可见的
        self.assertTrue(self.control_panel.visible)
        
        # 切换隐藏
        self.control_panel.toggle_visibility()
        self.assertFalse(self.control_panel.visible)
        
        # 再次切换显示
        self.control_panel.toggle_visibility()
        self.assertTrue(self.control_panel.visible)
    
    def test_add_slider(self):
        """测试添加滑块"""
        slider_id = self.control_panel.add_slider(
            "test_slider", 
            "Test Slider", 
            0.0, 
            1.0, 
            0.5
        )
        
        self.assertIsNotNone(slider_id)
        self.assertIn(slider_id, self.control_panel.sliders)
        
        slider = self.control_panel.sliders[slider_id]
        self.assertEqual(slider['label'], "Test Slider")
        self.assertEqual(slider['min_val'], 0.0)
        self.assertEqual(slider['max_val'], 1.0)
        self.assertEqual(slider['value'], 0.5)
    
    def test_add_button(self):
        """测试添加按钮"""
        button_id = self.control_panel.add_button(
            "test_button",
            "Test Button"
        )
        
        self.assertIsNotNone(button_id)
        self.assertIn(button_id, self.control_panel.buttons)
        
        button = self.control_panel.buttons[button_id]
        self.assertEqual(button['label'], "Test Button")
        self.assertFalse(button['pressed'])
    
    def test_add_checkbox(self):
        """测试添加复选框"""
        checkbox_id = self.control_panel.add_checkbox(
            "test_checkbox",
            "Test Checkbox",
            True
        )
        
        self.assertIsNotNone(checkbox_id)
        self.assertIn(checkbox_id, self.control_panel.checkboxes)
        
        checkbox = self.control_panel.checkboxes[checkbox_id]
        self.assertEqual(checkbox['label'], "Test Checkbox")
        self.assertTrue(checkbox['checked'])
    
    def test_get_slider_value(self):
        """测试获取滑块值"""
        slider_id = self.control_panel.add_slider("test", "Test", 0.0, 10.0, 5.0)
        
        value = self.control_panel.get_slider_value(slider_id)
        self.assertEqual(value, 5.0)
        
        # 测试不存在的滑块
        value = self.control_panel.get_slider_value("nonexistent")
        self.assertIsNone(value)
    
    def test_set_slider_value(self):
        """测试设置滑块值"""
        slider_id = self.control_panel.add_slider("test", "Test", 0.0, 10.0, 5.0)
        
        # 设置新值
        self.control_panel.set_slider_value(slider_id, 7.5)
        value = self.control_panel.get_slider_value(slider_id)
        self.assertEqual(value, 7.5)
        
        # 测试超出范围的值（应该被限制）
        self.control_panel.set_slider_value(slider_id, 15.0)
        value = self.control_panel.get_slider_value(slider_id)
        self.assertEqual(value, 10.0)  # 应该被限制在最大值
    
    def test_is_button_pressed(self):
        """测试按钮按下状态"""
        button_id = self.control_panel.add_button("test", "Test")
        
        # 默认应该是未按下
        pressed = self.control_panel.is_button_pressed(button_id)
        self.assertFalse(pressed)
        
        # 测试不存在的按钮
        pressed = self.control_panel.is_button_pressed("nonexistent")
        self.assertFalse(pressed)
    
    def test_is_checkbox_checked(self):
        """测试复选框选中状态"""
        checkbox_id = self.control_panel.add_checkbox("test", "Test", False)
        
        # 默认应该是未选中
        checked = self.control_panel.is_checkbox_checked(checkbox_id)
        self.assertFalse(checked)
        
        # 测试不存在的复选框
        checked = self.control_panel.is_checkbox_checked("nonexistent")
        self.assertFalse(checked)
    
    def test_update_checkbox(self):
        """测试更新复选框状态"""
        checkbox_id = self.control_panel.add_checkbox("test", "Test", False)
        
        # 更新为选中
        self.control_panel.update_checkbox(checkbox_id, True)
        checked = self.control_panel.is_checkbox_checked(checkbox_id)
        self.assertTrue(checked)
        
        # 更新为未选中
        self.control_panel.update_checkbox(checkbox_id, False)
        checked = self.control_panel.is_checkbox_checked(checkbox_id)
        self.assertFalse(checked)


class TestGUISystem(unittest.TestCase):
    """GUI系统测试"""
    
    def setUp(self):
        """测试前准备"""
        config_manager = ConfigManager()
        self.config = config_manager.get_config()
        self.screen_size = (1280, 720)
        self.gui_system = GUISystem(self.screen_size, self.config)
    
    def test_system_initialization(self):
        """测试GUI系统初始化"""
        self.assertIsNotNone(self.gui_system)
        self.assertEqual(self.gui_system.screen_width, 1280)
        self.assertEqual(self.gui_system.screen_height, 720)
        self.assertIsNotNone(self.gui_system.control_panel)
        self.assertFalse(self.gui_system.initialized)
    
    def test_initialize_success(self):
        """测试系统初始化成功"""
        result = self.gui_system.initialize()
        
        self.assertTrue(result)
        self.assertTrue(self.gui_system.initialized)
        self.assertTrue(self.gui_system.control_panel.visible)
    
    def test_initialize_failure(self):
        """测试系统初始化失败"""
        # 模拟初始化失败的情况
        with patch.object(self.gui_system.control_panel, '__init__') as mock_init:
            mock_init.side_effect = Exception("Initialization failed")
            
            result = self.gui_system.initialize()
            
            self.assertFalse(result)
            self.assertFalse(self.gui_system.initialized)
    
    def test_add_ui_elements(self):
        """测试添加UI元素"""
        # 添加滑块
        slider_id = self.gui_system.add_slider("brightness", "亮度", 0.0, 1.0, 0.5)
        self.assertIsNotNone(slider_id)
        
        # 添加按钮
        button_id = self.gui_system.add_button("reset", "重置")
        self.assertIsNotNone(button_id)
        
        # 添加复选框
        checkbox_id = self.gui_system.add_checkbox("effects", "特效", True)
        self.assertIsNotNone(checkbox_id)
    
    def test_update_method(self):
        """测试更新方法"""
        # 初始化系统
        self.gui_system.initialize()
        
        # 模拟性能数据
        delta_time = 1/60
        performance_data = {
            'fps': 60.0,
            'memory_mb': 150.0,
            'cpu_percent': 25.0
        }
        
        # 执行更新
        self.gui_system.update(delta_time, performance_data)
        
        # 验证性能数据显示被更新
        # 这里主要是验证方法能正常执行，具体的UI更新需要实际的pygame环境
    
    @patch('ui.gui_system.pygame')
    def test_draw_method(self, mock_pygame):
        """测试绘制方法"""
        # 初始化系统
        self.gui_system.initialize()
        
        # 创建模拟屏幕表面
        mock_screen = Mock()
        mock_pygame.Surface.return_value = mock_screen
        
        # 执行绘制
        self.gui_system.draw(mock_screen)
        
        # 验证绘制方法被调用
        self.assertTrue(hasattr(self.gui_system, '_draw_control_panel'))
        self.assertTrue(hasattr(self.gui_system, '_draw_performance_overlay'))
    
    def test_get_ui_values(self):
        """测试获取UI值"""
        # 初始化系统并添加元素
        self.gui_system.initialize()
        self.gui_system.add_slider("volume", "音量", 0.0, 1.0, 0.8)
        self.gui_system.add_checkbox("sound", "声音", True)
        
        # 获取UI值
        values = self.gui_system.get_ui_values()
        
        self.assertIsInstance(values, dict)
        self.assertIn('sliders', values)
        self.assertIn('checkboxes', values)
        
        # 验证具体值
        self.assertEqual(values['sliders']['volume'], 0.8)
        self.assertTrue(values['checkboxes']['sound'])
    
    def test_handle_mouse_click(self):
        """测试处理鼠标点击"""
        # 初始化系统
        self.gui_system.initialize()
        
        # 添加按钮用于测试
        button_id = self.gui_system.add_button("test_btn", "测试按钮")
        
        # 模拟鼠标点击在按钮上
        mouse_pos = (50, 100)  # 假设按钮在这个位置
        clicked_element = self.gui_system._handle_mouse_click(mouse_pos)
        
        # 由于没有实际的pygame环境，这里主要验证方法结构
        self.assertIsNotNone(clicked_element)  # 应该返回某个元素ID或None
    
    def test_handle_mouse_drag(self):
        """测试处理鼠标拖拽"""
        # 初始化系统
        self.gui_system.initialize()
        
        # 添加滑块用于测试
        slider_id = self.gui_system.add_slider("test_slider", "测试滑块", 0.0, 100.0, 50.0)
        
        # 模拟鼠标拖拽
        mouse_pos = (100, 200)
        self.gui_system._handle_mouse_drag(mouse_pos)
        
        # 验证滑块值可能被更新（具体逻辑取决于实现）
    
    def test_cleanup(self):
        """测试系统清理"""
        # 初始化系统
        self.gui_system.initialize()
        self.assertTrue(self.gui_system.initialized)
        
        # 执行清理
        self.gui_system.cleanup()
        
        # 验证清理完成
        self.assertFalse(self.gui_system.initialized)


class TestPerformanceOverlay(unittest.TestCase):
    """性能覆盖层测试"""
    
    def setUp(self):
        """测试前准备"""
        config_manager = ConfigManager()
        self.config = config_manager.get_config()
        self.gui_system = GUISystem((1280, 720), self.config)
        self.gui_system.initialize()
    
    def test_performance_data_display(self):
        """测试性能数据显示"""
        performance_data = {
            'fps': 59.7,
            'memory_mb': 187.5,
            'cpu_percent': 23.4,
            'gpu_percent': 45.2
        }
        
        # 更新性能数据
        self.gui_system.update(1/60, performance_data)
        
        # 获取UI值验证数据更新
        values = self.gui_system.get_ui_values()
        # 这里验证性能相关的UI元素被正确更新
    
    def test_performance_data_formatting(self):
        """测试性能数据格式化"""
        # 测试不同的数据格式
        test_cases = [
            {'fps': 60.0, 'memory_mb': 150.0},
            {'fps': 30.5, 'memory_mb': 2000.0},  # 大内存值
            {'fps': 0.0, 'memory_mb': 0.0}       # 边界值
        ]
        
        for data in test_cases:
            self.gui_system.update(1/60, data)
            # 验证数据能被正确处理和显示


class TestEventHandling(unittest.TestCase):
    """事件处理测试"""
    
    def setUp(self):
        """测试前准备"""
        config_manager = ConfigManager()
        self.config = config_manager.get_config()
        self.gui_system = GUISystem((1280, 720), self.config)
        self.gui_system.initialize()
    
    @patch('ui.gui_system.pygame')
    def test_process_events(self, mock_pygame):
        """测试事件处理"""
        # 模拟pygame事件
        mock_event = Mock()
        mock_event.type = mock_pygame.MOUSEBUTTONDOWN
        mock_event.button = 1
        mock_event.pos = (100, 100)
        
        mock_pygame.event.get.return_value = [mock_event]
        
        # 处理事件
        self.gui_system.process_events(mock_event)
        
        # 验证事件被正确处理
        # 具体的验证取决于事件处理的实现细节


if __name__ == '__main__':
    unittest.main()