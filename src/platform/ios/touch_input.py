"""
iOS Touch Input - iOS触摸输入处理
处理iOS平台的触摸屏输入和手势识别
"""

import logging
from typing import Dict, List, Tuple, Any, Callable
from dataclasses import dataclass
from enum import Enum
import time

logger = logging.getLogger(__name__)


class TouchEventType(Enum):
    """触摸事件类型"""
    BEGAN = "began"
    MOVED = "moved"
    ENDED = "ended"
    CANCELLED = "cancelled"


class GestureType(Enum):
    """手势类型"""
    TAP = "tap"
    DOUBLE_TAP = "double_tap"
    SWIPE = "swipe"
    PINCH = "pinch"
    ROTATION = "rotation"
    LONG_PRESS = "long_press"
    PAN = "pan"


@dataclass
class TouchPoint:
    """触摸点数据"""
    id: int
    x: float
    y: float
    force: float
    timestamp: float
    phase: TouchEventType


@dataclass
class GestureEvent:
    """手势事件数据"""
    gesture_type: GestureType
    points: List[TouchPoint]
    velocity: Tuple[float, float] = (0.0, 0.0)
    scale: float = 1.0
    rotation: float = 0.0
    centroid: Tuple[float, float] = (0.0, 0.0)


class IOSTouchHandler:
    """iOS触摸输入处理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 触摸状态
        self.active_touches: Dict[int, TouchPoint] = {}
        self.touch_history: List[TouchPoint] = []
        
        # 手势识别参数
        self.tap_threshold = config.get('tap_threshold', 30)  # 像素
        self.swipe_threshold = config.get('swipe_threshold', 80)  # 像素
        self.long_press_duration = config.get('long_press_duration', 0.5)  # 秒
        self.double_tap_interval = config.get('double_tap_interval', 0.3)  # 秒
        self.pinch_threshold = config.get('pinch_threshold', 0.1)  # 缩放比例变化
        self.rotation_threshold = config.get('rotation_threshold', 5.0)  # 角度变化
        
        # 回调函数
        self.touch_callbacks: List[Callable] = []
        self.gesture_callbacks: List[Callable] = []
        
        # 手势识别状态
        self.pending_gestures: Dict[str, Any] = {}
        self.last_tap_time = 0.0
        self.last_tap_position = (0.0, 0.0)
        
        # Haptic反馈支持
        self.haptic_feedback_enabled = config.get('haptic_feedback', True)
        
    def initialize(self) -> bool:
        """初始化触摸处理器"""
        try:
            self.logger.info("iOS触摸输入处理器初始化")
            return True
        except Exception as e:
            self.logger.error(f"触摸处理器初始化失败: {e}")
            return False
    
    def handle_touch_event(self, touch_id: int, x: float, y: float, 
                          force: float, phase: TouchEventType):
        """处理触摸事件"""
        current_time = time.time()
        
        touch_point = TouchPoint(
            id=touch_id,
            x=x,
            y=y,
            force=force,
            timestamp=current_time,
            phase=phase
        )
        
        if phase == TouchEventType.BEGAN:
            self._handle_touch_began(touch_point)
        elif phase == TouchEventType.MOVED:
            self._handle_touch_moved(touch_point)
        elif phase == TouchEventType.ENDED:
            self._handle_touch_ended(touch_point)
        elif phase == TouchEventType.CANCELLED:
            self._handle_touch_cancelled(touch_point)
        
        # 触发回调
        self._trigger_touch_callbacks(touch_point)
    
    def _handle_touch_began(self, touch_point: TouchPoint):
        """处理触摸开始事件"""
        self.active_touches[touch_point.id] = touch_point
        self.touch_history.append(touch_point)
        
        # 开始手势识别
        self._start_gesture_recognition(touch_point)
        
        self.logger.debug(f"触摸开始: ID={touch_point.id}, 位置=({touch_point.x}, {touch_point.y})")
    
    def _handle_touch_moved(self, touch_point: TouchPoint):
        """处理触摸移动事件"""
        if touch_point.id in self.active_touches:
            old_point = self.active_touches[touch_point.id]
            self.active_touches[touch_point.id] = touch_point
            self.touch_history.append(touch_point)
            
            # 更新手势识别
            self._update_gesture_recognition(old_point, touch_point)
    
    def _handle_touch_ended(self, touch_point: TouchPoint):
        """处理触摸结束事件"""
        if touch_point.id in self.active_touches:
            del self.active_touches[touch_point.id]
            self.touch_history.append(touch_point)
            
            # 完成手势识别
            self._complete_gesture_recognition(touch_point)
    
    def _handle_touch_cancelled(self, touch_point: TouchPoint):
        """处理触摸取消事件"""
        if touch_point.id in self.active_touches:
            del self.active_touches[touch_point.id]
            # 取消手势识别
            self._cancel_gesture_recognition(touch_point)
    
    def _start_gesture_recognition(self, touch_point: TouchPoint):
        """开始手势识别"""
        self.pending_gestures[touch_point.id] = {
            'start_point': touch_point,
            'points': [touch_point],
            'start_time': touch_point.timestamp,
            'max_distance': 0.0,
            'total_movement': 0.0
        }
    
    def _update_gesture_recognition(self, old_point: TouchPoint, new_point: TouchPoint):
        """更新手势识别"""
        if new_point.id in self.pending_gestures:
            gesture_data = self.pending_gestures[new_point.id]
            gesture_data['points'].append(new_point)
            
            # 计算移动距离
            dx = new_point.x - old_point.x
            dy = new_point.y - old_point.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            
            gesture_data['total_movement'] += distance
            gesture_data['max_distance'] = max(
                gesture_data['max_distance'], 
                ((new_point.x - gesture_data['start_point'].x) ** 2 + 
                 (new_point.y - gesture_data['start_point'].y) ** 2) ** 0.5
            )
    
    def _complete_gesture_recognition(self, touch_point: TouchPoint):
        """完成手势识别"""
        if touch_point.id not in self.pending_gestures:
            return
            
        gesture_data = self.pending_gestures[touch_point.id]
        start_point = gesture_data['start_point']
        points = gesture_data['points']
        start_time = gesture_data['start_time']
        max_distance = gesture_data['max_distance']
        total_movement = gesture_data['total_movement']
        
        # 识别手势类型
        gesture = self._recognize_gesture(
            start_point, touch_point, points, start_time, 
            max_distance, total_movement
        )
        
        if gesture:
            self._trigger_gesture_callbacks(gesture)
            self._provide_haptic_feedback(gesture.gesture_type)
        
        del self.pending_gestures[touch_point.id]
    
    def _cancel_gesture_recognition(self, touch_point: TouchPoint):
        """取消手势识别"""
        if touch_point.id in self.pending_gestures:
            del self.pending_gestures[touch_point.id]
    
    def _recognize_gesture(self, start_point: TouchPoint, end_point: TouchPoint,
                          points: List[TouchPoint], start_time: float,
                          max_distance: float, total_movement: float) -> Optional[GestureEvent]:
        """识别手势类型"""
        current_time = time.time()
        duration = current_time - start_time
        
        dx = end_point.x - start_point.x
        dy = end_point.y - start_point.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        # 单击手势
        if (duration < 0.3 and max_distance < self.tap_threshold and 
            len(self.active_touches) == 0):
            
            # 检查是否为双击
            time_since_last_tap = current_time - self.last_tap_time
            distance_from_last_tap = (
                (end_point.x - self.last_tap_position[0]) ** 2 +
                (end_point.y - self.last_tap_position[1]) ** 2
            ) ** 0.5
            
            if (time_since_last_tap < self.double_tap_interval and 
                distance_from_last_tap < self.tap_threshold * 2):
                gesture_type = GestureType.DOUBLE_TAP
                self.last_tap_time = 0  # 重置双击状态
            else:
                gesture_type = GestureType.TAP
                self.last_tap_time = current_time
                self.last_tap_position = (end_point.x, end_point.y)
            
            return GestureEvent(
                gesture_type=gesture_type,
                points=[start_point, end_point],
                centroid=(end_point.x, end_point.y)
            )
        
        # 长按手势
        elif (duration >= self.long_press_duration and 
              max_distance < self.tap_threshold and 
              len(points) <= 5):
            return GestureEvent(
                gesture_type=GestureType.LONG_PRESS,
                points=[start_point],
                centroid=(start_point.x, start_point.y)
            )
        
        # 滑动手势
        elif (distance >= self.swipe_threshold and 
              max_distance >= distance * 0.8 and
              duration < 0.5):
            velocity_x = dx / duration if duration > 0 else 0
            velocity_y = dy / duration if duration > 0 else 0
            
            return GestureEvent(
                gesture_type=GestureType.SWIPE,
                points=[start_point, end_point],
                velocity=(velocity_x, velocity_y),
                centroid=((start_point.x + end_point.x) / 2, 
                         (start_point.y + end_point.y) / 2)
            )
        
        # 平移手势（持续移动）
        elif (total_movement > self.swipe_threshold and 
              len(points) > 10 and
              max_distance > self.tap_threshold):
            velocity_x = dx / duration if duration > 0 else 0
            velocity_y = dy / duration if duration > 0 else 0
            
            return GestureEvent(
                gesture_type=GestureType.PAN,
                points=points,
                velocity=(velocity_x, velocity_y),
                centroid=((start_point.x + end_point.x) / 2, 
                         (start_point.y + end_point.y) / 2)
            )
        
        return None
    
    def _recognize_multi_touch_gestures(self):
        """识别多点触控手势（捏合、旋转）"""
        if len(self.active_touches) != 2:
            return
        
        # 获取两个触摸点
        touch_points = list(self.active_touches.values())
        point1, point2 = touch_points[0], touch_points[1]
        
        # 计算中心点和距离
        centroid_x = (point1.x + point2.x) / 2
        centroid_y = (point1.y + point2.y) / 2
        current_distance = (
            (point1.x - point2.x) ** 2 + 
            (point1.y - point2.y) ** 2
        ) ** 0.5
        
        # 这里应该实现连续的捏合和旋转检测
        # 暂时简化处理
        
    def _trigger_touch_callbacks(self, touch_point: TouchPoint):
        """触发触摸回调"""
        for callback in self.touch_callbacks:
            try:
                callback(touch_point)
            except Exception as e:
                self.logger.error(f"触摸回调执行失败: {e}")
    
    def _trigger_gesture_callbacks(self, gesture: GestureEvent):
        """触发手势回调"""
        self.logger.info(f"识别到手势: {gesture.gesture_type.value}")
        
        for callback in self.gesture_callbacks:
            try:
                callback(gesture)
            except Exception as e:
                self.logger.error(f"手势回调执行失败: {e}")
    
    def _provide_haptic_feedback(self, gesture_type: GestureType):
        """提供触觉反馈"""
        if not self.haptic_feedback_enabled:
            return
            
        try:
            from UIKit import UINotificationFeedbackGenerator
            
            feedback_generator = UINotificationFeedbackGenerator.new()
            feedback_generator.prepare()
            
            # 根据手势类型提供不同的反馈
            if gesture_type in [GestureType.TAP, GestureType.DOUBLE_TAP]:
                feedback_generator.notificationOccurred_(0)  # UINotificationFeedbackTypeSuccess
            elif gesture_type == GestureType.LONG_PRESS:
                feedback_generator.notificationOccurred_(1)  # UINotificationFeedbackTypeWarning
            elif gesture_type in [GestureType.SWIPE, GestureType.PAN]:
                feedback_generator.notificationOccurred_(0)  # UINotificationFeedbackTypeSuccess
                
        except Exception as e:
            self.logger.warning(f"触觉反馈失败: {e}")
    
    def add_touch_callback(self, callback: Callable):
        """添加触摸事件回调"""
        self.touch_callbacks.append(callback)
    
    def add_gesture_callback(self, callback: Callable):
        """添加手势事件回调"""
        self.gesture_callbacks.append(callback)
    
    def get_active_touch_count(self) -> int:
        """获取当前活动触摸点数量"""
        return len(self.active_touches)
    
    def get_touch_points(self) -> List[TouchPoint]:
        """获取当前所有触摸点"""
        return list(self.active_touches.values())
    
    def cleanup(self):
        """清理触摸处理器"""
        self.active_touches.clear()
        self.touch_history.clear()
        self.touch_callbacks.clear()
        self.gesture_callbacks.clear()
        self.pending_gestures.clear()
        self.logger.info("iOS触摸输入处理器清理完成")