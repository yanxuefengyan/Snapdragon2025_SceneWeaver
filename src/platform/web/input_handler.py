"""
Web Input Handler - Web输入处理
处理Web平台的鼠标、键盘和触摸输入
"""

import logging
from typing import Dict, List, Tuple, Any, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class InputEventType(Enum):
    """输入事件类型"""
    MOUSE_DOWN = "mousedown"
    MOUSE_UP = "mouseup"
    MOUSE_MOVE = "mousemove"
    MOUSE_WHEEL = "wheel"
    KEY_DOWN = "keydown"
    KEY_UP = "keyup"
    TOUCH_START = "touchstart"
    TOUCH_MOVE = "touchmove"
    TOUCH_END = "touchend"
    TOUCH_CANCEL = "touchcancel"


class PointerType(Enum):
    """指针类型"""
    MOUSE = "mouse"
    TOUCH = "touch"
    PEN = "pen"


@dataclass
class InputEvent:
    """输入事件数据"""
    event_type: InputEventType
    x: float = 0.0
    y: float = 0.0
    button: int = 0  # 鼠标按键: 0=左键, 1=中键, 2=右键
    buttons: int = 0  # 按钮状态掩码
    key: str = ""  # 键盘按键
    keyCode: int = 0  # 键码
    delta_x: float = 0.0  # 鼠标滚轮或触摸移动
    delta_y: float = 0.0
    pointer_type: PointerType = PointerType.MOUSE
    touches: List[Dict] = None  # 触摸点信息
    timestamp: float = 0.0


class WebInputHandler:
    """Web输入处理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 输入状态
        self.mouse_position = (0.0, 0.0)
        self.mouse_buttons = 0
        self.key_states = {}
        self.touch_points = {}
        
        # 回调函数
        self.event_callbacks: List[Callable] = []
        self.mouse_callbacks: List[Callable] = []
        self.keyboard_callbacks: List[Callable] = []
        self.touch_callbacks: List[Callable] = []
        
        # 输入配置
        self.pointer_lock_enabled = config.get('pointer_lock', False)
        self.touch_emulation = config.get('touch_emulation', True)
        self.prevent_default = config.get('prevent_default', True)
        
        # Canvas引用
        self.canvas = None
        self.window = None
        self.document = None
        
    def initialize(self, canvas=None, window=None, document=None) -> bool:
        """初始化输入处理器"""
        try:
            # 设置DOM引用
            self.canvas = canvas
            self.window = window
            self.document = document
            
            # 绑定事件监听器
            if self.canvas:
                self._bind_canvas_events()
            
            if self.window:
                self._bind_window_events()
            
            self.logger.info("Web输入处理器初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"输入处理器初始化失败: {e}")
            return False
    
    def _bind_canvas_events(self):
        """绑定Canvas事件监听器"""
        try:
            # 鼠标事件
            self.canvas.addEventListener('mousedown', self._on_mouse_down)
            self.canvas.addEventListener('mouseup', self._on_mouse_up)
            self.canvas.addEventListener('mousemove', self._on_mouse_move)
            self.canvas.addEventListener('wheel', self._on_mouse_wheel)
            
            # 触摸事件
            self.canvas.addEventListener('touchstart', self._on_touch_start)
            self.canvas.addEventListener('touchmove', self._on_touch_move)
            self.canvas.addEventListener('touchend', self._on_touch_end)
            self.canvas.addEventListener('touchcancel', self._on_touch_cancel)
            
            # 键盘事件需要在window上监听
            if self.window:
                self.window.addEventListener('keydown', self._on_key_down)
                self.window.addEventListener('keyup', self._on_key_up)
            
            self.logger.info("Canvas事件监听器绑定成功")
            
        except Exception as e:
            self.logger.error(f"Canvas事件绑定失败: {e}")
    
    def _bind_window_events(self):
        """绑定窗口事件监听器"""
        try:
            # 窗口失去焦点时释放鼠标锁定
            self.window.addEventListener('blur', self._on_window_blur)
            
            # 页面可见性变化
            self.document.addEventListener('visibilitychange', self._on_visibility_change)
            
            self.logger.info("窗口事件监听器绑定成功")
            
        except Exception as e:
            self.logger.error(f"窗口事件绑定失败: {e}")
    
    def _on_mouse_down(self, event):
        """鼠标按下事件处理"""
        if self.prevent_default:
            event.preventDefault()
        
        input_event = InputEvent(
            event_type=InputEventType.MOUSE_DOWN,
            x=event.clientX,
            y=event.clientY,
            button=event.button,
            buttons=event.buttons,
            pointer_type=PointerType.MOUSE,
            timestamp=event.timeStamp
        )
        
        self.mouse_buttons = event.buttons
        self.mouse_position = (event.clientX, event.clientY)
        
        self._trigger_callbacks(input_event)
        self._trigger_mouse_callbacks(input_event)
    
    def _on_mouse_up(self, event):
        """鼠标抬起事件处理"""
        if self.prevent_default:
            event.preventDefault()
        
        input_event = InputEvent(
            event_type=InputEventType.MOUSE_UP,
            x=event.clientX,
            y=event.clientY,
            button=event.button,
            buttons=event.buttons,
            pointer_type=PointerType.MOUSE,
            timestamp=event.timeStamp
        )
        
        self.mouse_buttons = event.buttons
        self.mouse_position = (event.clientX, event.clientY)
        
        self._trigger_callbacks(input_event)
        self._trigger_mouse_callbacks(input_event)
    
    def _on_mouse_move(self, event):
        """鼠标移动事件处理"""
        if self.prevent_default:
            event.preventDefault()
        
        input_event = InputEvent(
            event_type=InputEventType.MOUSE_MOVE,
            x=event.clientX,
            y=event.clientY,
            buttons=event.buttons,
            pointer_type=PointerType.MOUSE,
            timestamp=event.timeStamp
        )
        
        self.mouse_position = (event.clientX, event.clientY)
        
        self._trigger_callbacks(input_event)
        self._trigger_mouse_callbacks(input_event)
        
        # 处理鼠标锁定
        if self.pointer_lock_enabled and hasattr(self.canvas, 'requestPointerLock'):
            self._handle_pointer_lock(event)
    
    def _on_mouse_wheel(self, event):
        """鼠标滚轮事件处理"""
        if self.prevent_default:
            event.preventDefault()
        
        input_event = InputEvent(
            event_type=InputEventType.MOUSE_WHEEL,
            x=event.clientX,
            y=event.clientY,
            delta_x=event.deltaX,
            delta_y=event.deltaY,
            pointer_type=PointerType.MOUSE,
            timestamp=event.timeStamp
        )
        
        self._trigger_callbacks(input_event)
        self._trigger_mouse_callbacks(input_event)
    
    def _on_key_down(self, event):
        """键盘按下事件处理"""
        if self.prevent_default and self._should_prevent_key(event):
            event.preventDefault()
        
        input_event = InputEvent(
            event_type=InputEventType.KEY_DOWN,
            key=event.key,
            keyCode=event.keyCode,
            timestamp=event.timeStamp
        )
        
        self.key_states[event.key] = True
        
        self._trigger_callbacks(input_event)
        self._trigger_keyboard_callbacks(input_event)
    
    def _on_key_up(self, event):
        """键盘抬起事件处理"""
        if self.prevent_default and self._should_prevent_key(event):
            event.preventDefault()
        
        input_event = InputEvent(
            event_type=InputEventType.KEY_UP,
            key=event.key,
            keyCode=event.keyCode,
            timestamp=event.timeStamp
        )
        
        self.key_states[event.key] = False
        
        self._trigger_callbacks(input_event)
        self._trigger_keyboard_callbacks(input_event)
    
    def _on_touch_start(self, event):
        """触摸开始事件处理"""
        if self.prevent_default:
            event.preventDefault()
        
        touches = self._extract_touch_data(event.touches)
        
        input_event = InputEvent(
            event_type=InputEventType.TOUCH_START,
            touches=touches,
            pointer_type=PointerType.TOUCH,
            timestamp=event.timeStamp
        )
        
        # 更新触摸点状态
        for touch in touches:
            self.touch_points[touch['identifier']] = touch
        
        self._trigger_callbacks(input_event)
        self._trigger_touch_callbacks(input_event)
    
    def _on_touch_move(self, event):
        """触摸移动事件处理"""
        if self.prevent_default:
            event.preventDefault()
        
        touches = self._extract_touch_data(event.touches)
        
        input_event = InputEvent(
            event_type=InputEventType.TOUCH_MOVE,
            touches=touches,
            pointer_type=PointerType.TOUCH,
            timestamp=event.timeStamp
        )
        
        # 更新触摸点状态
        for touch in touches:
            self.touch_points[touch['identifier']] = touch
        
        self._trigger_callbacks(input_event)
        self._trigger_touch_callbacks(input_event)
    
    def _on_touch_end(self, event):
        """触摸结束事件处理"""
        if self.prevent_default:
            event.preventDefault()
        
        touches = self._extract_touch_data(event.changedTouches)
        
        input_event = InputEvent(
            event_type=InputEventType.TOUCH_END,
            touches=touches,
            pointer_type=PointerType.TOUCH,
            timestamp=event.timeStamp
        )
        
        # 移除触摸点
        for touch in touches:
            if touch['identifier'] in self.touch_points:
                del self.touch_points[touch['identifier']]
        
        self._trigger_callbacks(input_event)
        self._trigger_touch_callbacks(input_event)
    
    def _on_touch_cancel(self, event):
        """触摸取消事件处理"""
        if self.prevent_default:
            event.preventDefault()
        
        touches = self._extract_touch_data(event.changedTouches)
        
        input_event = InputEvent(
            event_type=InputEventType.TOUCH_CANCEL,
            touches=touches,
            pointer_type=PointerType.TOUCH,
            timestamp=event.timeStamp
        )
        
        # 移除触摸点
        for touch in touches:
            if touch['identifier'] in self.touch_points:
                del self.touch_points[touch['identifier']]
        
        self._trigger_callbacks(input_event)
        self._trigger_touch_callbacks(input_event)
    
    def _on_window_blur(self, event):
        """窗口失去焦点处理"""
        # 释放所有按键状态
        self.key_states.clear()
        self.mouse_buttons = 0
        self.touch_points.clear()
        self.logger.info("窗口失去焦点，清空输入状态")
    
    def _on_visibility_change(self, event):
        """页面可见性变化处理"""
        if self.document.visibilityState == 'hidden':
            # 页面隐藏时清空输入状态
            self.key_states.clear()
            self.mouse_buttons = 0
            self.touch_points.clear()
            self.logger.info("页面隐藏，清空输入状态")
    
    def _extract_touch_data(self, touch_list):
        """提取触摸数据"""
        touches = []
        for touch in touch_list:
            touches.append({
                'identifier': touch.identifier,
                'clientX': touch.clientX,
                'clientY': touch.clientY,
                'pageX': touch.pageX,
                'pageY': touch.pageY,
                'screenX': touch.screenX,
                'screenY': touch.screenY,
                'radiusX': getattr(touch, 'radiusX', 1),
                'radiusY': getattr(touch, 'radiusY', 1),
                'rotationAngle': getattr(touch, 'rotationAngle', 0),
                'force': getattr(touch, 'force', 1)
            })
        return touches
    
    def _should_prevent_key(self, event):
        """判断是否应该阻止键盘事件默认行为"""
        # 防止方向键、空格键等影响页面滚动
        prevent_keys = ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' ', 'Spacebar']
        return event.key in prevent_keys
    
    def _handle_pointer_lock(self, event):
        """处理鼠标锁定"""
        if (event.buttons & 1) and not hasattr(self.canvas, 'pointerLockElement'):
            try:
                self.canvas.requestPointerLock()
            except Exception as e:
                self.logger.debug(f"鼠标锁定请求失败: {e}")
    
    def _trigger_callbacks(self, event: InputEvent):
        """触发通用事件回调"""
        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                self.logger.error(f"事件回调执行失败: {e}")
    
    def _trigger_mouse_callbacks(self, event: InputEvent):
        """触发鼠标事件回调"""
        for callback in self.mouse_callbacks:
            try:
                callback(event)
            except Exception as e:
                self.logger.error(f"鼠标回调执行失败: {e}")
    
    def _trigger_keyboard_callbacks(self, event: InputEvent):
        """触发键盘事件回调"""
        for callback in self.keyboard_callbacks:
            try:
                callback(event)
            except Exception as e:
                self.logger.error(f"键盘回调执行失败: {e}")
    
    def _trigger_touch_callbacks(self, event: InputEvent):
        """触发触摸事件回调"""
        for callback in self.touch_callbacks:
            try:
                callback(event)
            except Exception as e:
                self.logger.error(f"触摸回调执行失败: {e}")
    
    def add_event_callback(self, callback: Callable):
        """添加通用事件回调"""
        self.event_callbacks.append(callback)
    
    def add_mouse_callback(self, callback: Callable):
        """添加鼠标事件回调"""
        self.mouse_callbacks.append(callback)
    
    def add_keyboard_callback(self, callback: Callable):
        """添加键盘事件回调"""
        self.keyboard_callbacks.append(callback)
    
    def add_touch_callback(self, callback: Callable):
        """添加触摸事件回调"""
        self.touch_callbacks.append(callback)
    
    def get_mouse_position(self) -> Tuple[float, float]:
        """获取鼠标位置"""
        return self.mouse_position
    
    def is_mouse_button_pressed(self, button: int) -> bool:
        """检查鼠标按键是否按下"""
        return bool(self.mouse_buttons & (1 << button))
    
    def is_key_pressed(self, key: str) -> bool:
        """检查键盘按键是否按下"""
        return self.key_states.get(key, False)
    
    def get_active_touch_count(self) -> int:
        """获取当前活动触摸点数量"""
        return len(self.touch_points)
    
    def get_touch_points(self) -> Dict:
        """获取当前所有触摸点"""
        return self.touch_points.copy()
    
    def request_pointer_lock(self):
        """请求鼠标锁定"""
        if hasattr(self.canvas, 'requestPointerLock'):
            try:
                self.canvas.requestPointerLock()
            except Exception as e:
                self.logger.error(f"鼠标锁定请求失败: {e}")
    
    def exit_pointer_lock(self):
        """退出鼠标锁定"""
        if hasattr(self.document, 'exitPointerLock'):
            try:
                self.document.exitPointerLock()
            except Exception as e:
                self.logger.error(f"退出鼠标锁定失败: {e}")
    
    def cleanup(self):
        """清理输入处理器"""
        try:
            # 移除事件监听器
            if self.canvas:
                event_types = ['mousedown', 'mouseup', 'mousemove', 'wheel', 
                              'touchstart', 'touchmove', 'touchend', 'touchcancel']
                for event_type in event_types:
                    # 注意：需要保存原始的事件处理函数引用才能正确移除
                    pass
            
            if self.window:
                # 移除窗口事件监听器
                pass
            
            # 清理状态
            self.event_callbacks.clear()
            self.mouse_callbacks.clear()
            self.keyboard_callbacks.clear()
            self.touch_callbacks.clear()
            self.key_states.clear()
            self.touch_points.clear()
            
            self.logger.info("Web输入处理器清理完成")
            
        except Exception as e:
            self.logger.error(f"Web输入处理器清理失败: {e}")