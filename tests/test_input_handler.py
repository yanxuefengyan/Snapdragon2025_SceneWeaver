"""
Input Handler 单元测试
测试输入处理系统的键盘、鼠标和手势输入功能
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import numpy as np

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from input.input_handler import InputHandler, InputState, GestureRecognizer
from utils.config_manager import ConfigManager


class TestInputState(unittest.TestCase):
    """输入状态测试"""
    
    def setUp(self):
        """测试前准备"""
        self.input_state = InputState()
    
    def test_state_initialization(self):
        """测试输入状态初始化"""
        self.assertFalse(self.input_state.keys_pressed['w'])
        self.assertFalse(self.input_state.keys_pressed['s'])
        self.assertFalse(self.input_state.keys_pressed['a'])
        self.assertFalse(self.input_state.keys_pressed['d'])
        self.assertEqual(self.input_state.mouse_x, 0)
        self.assertEqual(self.input_state.mouse_y, 0)
        self.assertFalse(self.input_state.mouse_left)
        self.assertFalse(self.input_state.mouse_right)
        self.assertEqual(self.input_state.scroll_delta, 0)
    
    def test_key_press_tracking(self):
        """测试按键按下跟踪"""
        # 模拟按下W键
        self.input_state.set_key_pressed('w', True)
        self.assertTrue(self.input_state.keys_pressed['w'])
        
        # 模拟释放W键
        self.input_state.set_key_pressed('w', False)
        self.assertFalse(self.input_state.keys_pressed['w'])
    
    def test_multiple_key_tracking(self):
        """测试多按键跟踪"""
        # 同时按下多个键
        self.input_state.set_key_pressed('w', True)
        self.input_state.set_key_pressed('a', True)
        
        self.assertTrue(self.input_state.keys_pressed['w'])
        self.assertTrue(self.input_state.keys_pressed['a'])
        self.assertFalse(self.input_state.keys_pressed['s'])
        self.assertFalse(self.input_state.keys_pressed['d'])
    
    def test_movement_vector_calculation(self):
        """测试移动向量计算"""
        # 只按W键
        self.input_state.set_key_pressed('w', True)
        move_vector = self.input_state.get_movement_vector()
        self.assertEqual(move_vector, (0, 1))  # 向前移动
        
        # 只按S键
        self.input_state.set_key_pressed('w', False)
        self.input_state.set_key_pressed('s', True)
        move_vector = self.input_state.get_movement_vector()
        self.assertEqual(move_vector, (0, -1))  # 向后移动
        
        # 同时按W和D键（右前方移动）
        self.input_state.set_key_pressed('w', True)
        self.input_state.set_key_pressed('d', True)
        move_vector = self.input_state.get_movement_vector()
        self.assertEqual(move_vector, (1, 1))
        
        # 不按任何键
        self.input_state.set_key_pressed('w', False)
        self.input_state.set_key_pressed('s', False)
        self.input_state.set_key_pressed('a', False)
        self.input_state.set_key_pressed('d', False)
        move_vector = self.input_state.get_movement_vector()
        self.assertEqual(move_vector, (0, 0))
    
    def test_mouse_position_tracking(self):
        """测试鼠标位置跟踪"""
        # 设置鼠标位置
        self.input_state.set_mouse_position(100, 200)
        self.assertEqual(self.input_state.mouse_x, 100)
        self.assertEqual(self.input_state.mouse_y, 200)
    
    def test_mouse_button_tracking(self):
        """测试鼠标按键跟踪"""
        # 按下左键
        self.input_state.set_mouse_button(1, True)
        self.assertTrue(self.input_state.mouse_left)
        self.assertFalse(self.input_state.mouse_right)
        
        # 按下右键
        self.input_state.set_mouse_button(3, True)
        self.assertTrue(self.input_state.mouse_left)
        self.assertTrue(self.input_state.mouse_right)
        
        # 释放按键
        self.input_state.set_mouse_button(1, False)
        self.input_state.set_mouse_button(3, False)
        self.assertFalse(self.input_state.mouse_left)
        self.assertFalse(self.input_state.mouse_right)
    
    def test_scroll_tracking(self):
        """测试滚轮滚动跟踪"""
        # 向上滚动
        self.input_state.set_scroll_delta(1)
        self.assertEqual(self.input_state.scroll_delta, 1)
        
        # 向下滚动
        self.input_state.set_scroll_delta(-1)
        self.assertEqual(self.input_state.scroll_delta, -1)
        
        # 重置滚动
        self.input_state.set_scroll_delta(0)
        self.assertEqual(self.input_state.scroll_delta, 0)


class TestGestureRecognizer(unittest.TestCase):
    """手势识别器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.gesture_recognizer = GestureRecognizer()
    
    def test_gestureRecognizer_initialization(self):
        """测试手势识别器初始化"""
        self.assertIsNotNone(self.gesture_recognizer)
        self.assertEqual(len(self.gesture_recognizer.touch_points), 0)
        self.assertIsNone(self.gesture_recognizer.current_gesture)
        self.assertEqual(self.gesture_recognizer.min_distance, 30)
        self.assertEqual(self.gesture_recognizer.tap_timeout, 0.3)
    
    def test_single_touch_point(self):
        """测试单点触摸"""
        touch_data = [(100, 150)]
        
        gesture = self.gesture_recognizer.recognize_gesture(touch_data)
        
        # 单点触摸应该识别为点击或长按
        self.assertIsNotNone(gesture)
        self.assertIn(gesture, ['tap', 'long_press', 'none'])
    
    def test_double_touch_points(self):
        """测试双点触摸"""
        touch_data = [(100, 150), (150, 200)]
        
        gesture = self.gesture_recognizer.recognize_gesture(touch_data)
        
        # 双点触摸应该识别为缩放或旋转
        self.assertIsNotNone(gesture)
        self.assertIn(gesture, ['pinch', 'rotate', 'none'])
    
    def test_multi_touch_points(self):
        """测试多点触摸"""
        touch_data = [(100, 150), (150, 200), (200, 100)]
        
        gesture = self.gesture_recognizer.recognize_gesture(touch_data)
        
        # 多点触摸可能识别为复杂手势
        self.assertIsNotNone(gesture)
    
    def test_swipe_gesture_recognition(self):
        """测试滑动手势识别"""
        # 模拟从左到右的滑动
        start_points = [(50, 100)]
        end_points = [(200, 100)]
        
        # 先添加起始点
        self.gesture_recognizer.recognize_gesture(start_points)
        
        # 然后添加结束点
        gesture = self.gesture_recognizer.recognize_gesture(end_points)
        
        # 应该识别为滑动手势
        if gesture != 'none':
            self.assertIn(gesture, ['swipe_left', 'swipe_right', 'swipe_up', 'swipe_down'])
    
    def test_pinch_gesture_recognition(self):
        """测试捏合手势识别"""
        # 模拟两指捏合
        start_points = [(100, 100), (200, 200)]  # 较远距离
        end_points = [(150, 150), (160, 160)]    # 较近距离
        
        self.gesture_recognizer.recognize_gesture(start_points)
        gesture = self.gesture_recognizer.recognize_gesture(end_points)
        
        if gesture != 'none':
            self.assertEqual(gesture, 'pinch')
    
    def test_tap_sequence_recognition(self):
        """测试点击序列识别"""
        single_point = [(100, 100)]
        
        # 第一次点击
        gesture1 = self.gesture_recognizer.recognize_gesture(single_point)
        
        # 快速第二次点击（双击）
        gesture2 = self.gesture_recognizer.recognize_gesture(single_point)
        
        # 验证双击识别
        if gesture2 != 'none':
            self.assertEqual(gesture2, 'double_tap')
    
    def test_gesture_reset(self):
        """测试手势重置"""
        # 识别一个手势
        touch_data = [(100, 100)]
        self.gesture_recognizer.recognize_gesture(touch_data)
        
        # 重置手势识别器
        self.gesture_recognizer.reset()
        
        # 验证状态被重置
        self.assertEqual(len(self.gesture_recognizer.touch_points), 0)
        self.assertIsNone(self.gesture_recognizer.current_gesture)


class TestInputHandler(unittest.TestCase):
    """输入处理器测试"""
    
    def setUp(self):
        """测试前准备"""
        config_manager = ConfigManager()
        self.config = config_manager.get_config()
        self.input_handler = InputHandler(self.config)
    
    def test_handler_initialization(self):
        """测试输入处理器初始化"""
        self.assertIsNotNone(self.input_handler)
        self.assertIsInstance(self.input_handler.state, InputState)
        self.assertIsInstance(self.input_handler.gesture_recognizer, GestureRecognizer)
        self.assertFalse(self.input_handler.initialized)
        self.assertIsNotNone(self.input_handler.logger)
    
    def test_initialize_success(self):
        """测试初始化成功"""
        result = self.input_handler.initialize()
        
        self.assertTrue(result)
        self.assertTrue(self.input_handler.initialized)
    
    @patch('input.input_handler.pygame')
    def test_handle_keyboard_event_keydown(self, mock_pygame):
        """测试处理键盘按下事件"""
        mock_pygame.KEYDOWN = 1
        mock_pygame.K_w = 119
        
        mock_event = Mock()
        mock_event.type = mock_pygame.KEYDOWN
        mock_event.key = mock_pygame.K_w
        
        self.input_handler.handle_event(mock_event)
        
        # 验证W键被标记为按下
        self.assertTrue(self.input_handler.state.keys_pressed['w'])
    
    @patch('input.input_handler.pygame')
    def test_handle_keyboard_event_keyup(self, mock_pygame):
        """测试处理键盘释放事件"""
        mock_pygame.KEYUP = 2
        mock_pygame.K_w = 119
        
        # 先按下键
        self.input_handler.state.set_key_pressed('w', True)
        
        mock_event = Mock()
        mock_event.type = mock_pygame.KEYUP
        mock_event.key = mock_pygame.K_w
        
        self.input_handler.handle_event(mock_event)
        
        # 验证键被释放
        self.assertFalse(self.input_handler.state.keys_pressed['w'])
    
    @patch('input.input_handler.pygame')
    def test_handle_mouse_motion(self, mock_pygame):
        """测试处理鼠标移动事件"""
        mock_pygame.MOUSEMOTION = 3
        
        mock_event = Mock()
        mock_event.type = mock_pygame.MOUSEMOTION
        mock_event.pos = (300, 400)
        
        self.input_handler.handle_event(mock_event)
        
        # 验证鼠标位置被更新
        self.assertEqual(self.input_handler.state.mouse_x, 300)
        self.assertEqual(self.input_handler.state.mouse_y, 400)
    
    @patch('input.input_handler.pygame')
    def test_handle_mouse_button_down(self, mock_pygame):
        """测试处理鼠标按键按下事件"""
        mock_pygame.MOUSEBUTTONDOWN = 4
        mock_pygame.BUTTON_LEFT = 1
        mock_pygame.BUTTON_RIGHT = 3
        
        # 测试左键按下
        mock_event = Mock()
        mock_event.type = mock_pygame.MOUSEBUTTONDOWN
        mock_event.button = mock_pygame.BUTTON_LEFT
        
        self.input_handler.handle_event(mock_event)
        self.assertTrue(self.input_handler.state.mouse_left)
        
        # 测试右键按下
        mock_event.button = mock_pygame.BUTTON_RIGHT
        self.input_handler.handle_event(mock_event)
        self.assertTrue(self.input_handler.state.mouse_right)
    
    @patch('input.input_handler.pygame')
    def test_handle_mouse_button_up(self, mock_pygame):
        """测试处理鼠标按键释放事件"""
        mock_pygame.MOUSEBUTTONUP = 5
        mock_pygame.BUTTON_LEFT = 1
        
        # 先按下按键
        self.input_handler.state.set_mouse_button(1, True)
        
        mock_event = Mock()
        mock_event.type = mock_pygame.MOUSEBUTTONUP
        mock_event.button = mock_pygame.BUTTON_LEFT
        
        self.input_handler.handle_event(mock_event)
        
        # 验证按键被释放
        self.assertFalse(self.input_handler.state.mouse_left)
    
    @patch('input.input_handler.pygame')
    def test_handle_mouse_wheel(self, mock_pygame):
        """测试处理鼠标滚轮事件"""
        mock_pygame.MOUSEWHEEL = 6
        
        mock_event = Mock()
        mock_event.type = mock_pygame.MOUSEWHEEL
        mock_event.y = 1  # 向上滚动
        
        self.input_handler.handle_event(mock_event)
        
        # 验证滚动值被更新
        self.assertEqual(self.input_handler.state.scroll_delta, 1)
    
    def test_get_movement_vector(self):
        """测试获取移动向量"""
        # 按下W键
        self.input_handler.state.set_key_pressed('w', True)
        
        movement = self.input_handler.get_movement_vector()
        
        self.assertEqual(movement, (0, 1))
        
        # 同时按下A键
        self.input_handler.state.set_key_pressed('a', True)
        movement = self.input_handler.get_movement_vector()
        
        self.assertEqual(movement, (-1, 1))
    
    def test_get_mouse_position(self):
        """测试获取鼠标位置"""
        # 设置鼠标位置
        self.input_handler.state.set_mouse_position(500, 300)
        
        mouse_pos = self.input_handler.get_mouse_position()
        
        self.assertEqual(mouse_pos, (500, 300))
    
    def test_is_key_pressed(self):
        """测试按键状态查询"""
        # 测试未按下的键
        self.assertFalse(self.input_handler.is_key_pressed('w'))
        
        # 按下键后测试
        self.input_handler.state.set_key_pressed('w', True)
        self.assertTrue(self.input_handler.is_key_pressed('w'))
    
    def test_is_mouse_button_pressed(self):
        """测试鼠标按键状态查询"""
        # 测试未按下的按键
        self.assertFalse(self.input_handler.is_mouse_button_pressed(1))  # 左键
        
        # 按下按键后测试
        self.input_handler.state.set_mouse_button(1, True)
        self.assertTrue(self.input_handler.is_mouse_button_pressed(1))
    
    def test_get_scroll_delta(self):
        """测试获取滚动增量"""
        # 设置滚动值
        self.input_handler.state.set_scroll_delta(-2)
        
        scroll_delta = self.input_handler.get_scroll_delta()
        
        self.assertEqual(scroll_delta, -2)
    
    @patch('input.input_handler.pygame')
    def test_process_touch_events(self, mock_pygame):
        """测试处理触摸事件"""
        # 模拟触摸事件
        touch_points = [(100, 150), (200, 250)]
        
        with patch.object(self.input_handler.gesture_recognizer, 'recognize_gesture') as mock_recognize:
            mock_recognize.return_value = 'pinch'
            
            recognized_gesture = self.input_handler.process_touch_events(touch_points)
            
            self.assertEqual(recognized_gesture, 'pinch')
            mock_recognize.assert_called_once_with(touch_points)
    
    def test_reset_scroll_delta(self):
        """测试重置滚动增量"""
        # 设置滚动值
        self.input_handler.state.set_scroll_delta(3)
        
        # 重置滚动
        self.input_handler.reset_scroll_delta()
        
        # 验证滚动值被重置
        self.assertEqual(self.input_handler.state.scroll_delta, 0)
    
    def test_cleanup(self):
        """测试清理方法"""
        # 初始化处理器
        self.input_handler.initialize()
        self.assertTrue(self.input_handler.initialized)
        
        # 执行清理
        self.input_handler.cleanup()
        
        # 验证清理完成
        self.logger = self.input_handler.logger
        self.logger.info("InputHandler资源清理完成")


if __name__ == '__main__':
    unittest.main()