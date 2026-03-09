"""
Android Touch Input - Android触摸输入处理
处理Android平台的触摸屏输入和手势识别
"""

import logging
from typing import Dict, List, Tuple, Any, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TouchEventType(Enum):
    """触摸事件类型"""
    DOWN = "down"
    MOVE = "move"
    UP = "up"
    CANCEL = "cancel"


class GestureType(Enum):
    """手势类型"""
    TAP = "tap"
    DOUBLE_TAP = "double_tap"
    SWIPE = "swipe"
    PINCH = "pinch"
    LONG_PRESS = "long_press"


@dataclass
class TouchPoint:
    """触摸点数据"""
    id: int
    x: float
    y: float
    pressure: float
    timestamp: float


@dataclass
class GestureEvent:
    """手势事件数据"""
    gesture_type: GestureType
    points: List[TouchPoint]
    velocity: Tuple[float, float] = (0.0, 0.0)
    scale: float = 1.0


class AndroidTouchHandler:
    """Android触摸输入处理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 触摸状态
        self.active_touches: Dict[int, TouchPoint] = {}
        self.touch_history: List[TouchPoint] = []
        
        # 手势识别参数
        self.tap_threshold = config.get('tap_threshold', 50)  # 像素
        self.swipe_threshold = config.get('swipe_threshold', 100)  # 像素
        self.long_press_duration = config.get('long_press_duration', 1.0)  # 秒
        self.double_tap_interval = config.get('double_tap_interval', 0.3)  # 秒
        
        # 回调函数
        self.touch_callbacks: List[Callable] = []
        self.gesture_callbacks: List[Callable] = []
        
        # 手势识别状态
        self.pending_gestures: Dict[str, Any] = {}
        self.last_tap_time = 0.0
        
    def initialize(self) -> bool:
        """初始化触摸处理器"""
        try:
            self.logger.info("Android触摸输入处理器初始化")
            return True
        except Exception as e:
            self.logger.error(f"触摸处理器初始化失败: {e}")
            return False
    
    def handle_touch_event(self, event_type: TouchEventType, touch_id: int, 
                          x: float, y: float, pressure: float = 1.0):
        """处理触摸事件"""
        import time
        current_time = time.time()
        
        touch_point = TouchPoint(
            id=touch_id,
            x=x,
            y=y,
            pressure=pressure,
            timestamp=current_time
        )
        
        if event_type == TouchEventType.DOWN:
            self._handle_touch_down(touch_point)
        elif event_type == TouchEventType.MOVE:
            self._handle_touch_move(touch_point)
        elif event_type == TouchEventType.UP:
            self._handle_touch_up(touch_point)
        elif event_type == TouchEventType.CANCEL:
            self._handle_touch_cancel(touch_point)
        
        # 触发回调
        self._trigger_touch_callbacks(event_type, touch_point)
    
    def _handle_touch_down(self, touch_point: TouchPoint):
        """处理触摸按下事件"""
        self.active_touches[touch_point.id] = touch_point
        self.touch_history.append(touch_point)
        
        # 开始手势识别
        self._start_gesture_recognition(touch_point)
        
        self.logger.debug(f"触摸按下: ID={touch_point.id}, 位置=({touch_point.x}, {touch_point.y})")
    
    def _handle_touch_move(self, touch_point: TouchPoint):
        """处理触摸移动事件"""
        if touch_point.id in self.active_touches:
            self.active_touches[touch_point.id] = touch_point
            self.touch_history.append(touch_point)
            
            # 更新手势识别
            self._update_gesture_recognition(touch_point)
    
    def _handle_touch_up(self, touch_point: TouchPoint):
        """处理触摸抬起事件"""
        if touch_point.id in self.active_touches:
            del self.active_touches[touch_point.id]
            self.touch_history.append(touch_point)
            
            # 完成手势识别
            self._complete_gesture_recognition(touch_point)
    
    def _handle_touch_cancel(self, touch_point: TouchPoint):
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
            'start_time': touch_point.timestamp
        }
    
    def _update_gesture_recognition(self, touch_point: TouchPoint):
        """更新手势识别"""
        if touch_point.id in self.pending_gestures:
            gesture_data = self.pending_gestures[touch_point.id]
            gesture_data['points'].append(touch_point)
    
    def _complete_gesture_recognition(self, touch_point: TouchPoint):
        """完成手势识别"""
        if touch_point.id not in self.pending_gestures:
            return
            
        gesture_data = self.pending_gestures[touch_point.id]
        start_point = gesture_data['start_point']
        points = gesture_data['points']
        start_time = gesture_data['start_time']
        
        # 识别手势类型
        gesture = self._recognize_gesture(start_point, touch_point, points, start_time)
        
        if gesture:
            self._trigger_gesture_callbacks(gesture)
        
        del self.pending_gestures[touch_point.id]
    
    def _cancel_gesture_recognition(self, touch_point: TouchPoint):
        """取消手势识别"""
        if touch_point.id in self.pending_gestures:
            del self.pending_gestures[touch_point.id]
    
    def _recognize_gesture(self, start_point: TouchPoint, end_point: TouchPoint,
                          points: List[TouchPoint], start_time: float) -> Optional[GestureEvent]:
        """识别手势类型"""
        import time
        current_time = time.time()
        duration = current_time - start_time
        
        dx = end_point.x - start_point.x
        dy = end_point.y - start_point.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        # 单击手势
        if duration < 0.5 and distance < self.tap_threshold:
            # 检查是否为双击
            if current_time - self.last_tap_time < self.double_tap_interval:
                gesture_type = GestureType.DOUBLE_TAP
                self.last_tap_time = 0  # 重置双击状态
            else:
                gesture_type = GestureType.TAP
                self.last_tap_time = current_time
            
            return GestureEvent(
                gesture_type=gesture_type,
                points=[start_point, end_point]
            )
        
        # 长按手势
        elif duration >= self.long_press_duration and distance < self.tap_threshold:
            return GestureEvent(
                gesture_type=GestureType.LONG_PRESS,
                points=[start_point]
            )
        
        # 滑动手势
        elif distance >= self.swipe_threshold:
            velocity_x = dx / duration if duration > 0 else 0
            velocity_y = dy / duration if duration > 0 else 0
            
            return GestureEvent(
                gesture_type=GestureType.SWIPE,
                points=[start_point, end_point],
                velocity=(velocity_x, velocity_y)
            )
        
        return None
    
    def _trigger_touch_callbacks(self, event_type: TouchEventType, touch_point: TouchPoint):
        """触发触摸回调"""
        for callback in self.touch_callbacks:
            try:
                callback(event_type, touch_point)
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
        self.logger.info("Android触摸输入处理器清理完成")