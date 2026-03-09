"""
GUI System - 图形用户界面系统
提供直观的图形化操作界面
"""

import logging
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from enum import Enum

try:
    import pygame
    import pygame_gui
    from pygame_gui.elements import UIButton, UILabel, UIPanel, UISlider
    from pygame_gui.core import UIElement
except ImportError as e:
    print(f"GUI依赖导入失败: {e}")
    # 创建模拟类以便程序能运行
    class MockPygameGUI:
        def __init__(self, *args, **kwargs):
            pass
    pygame_gui = MockPygameGUI()


class UIElementType(Enum):
    """UI元素类型枚举"""
    BUTTON = "button"
    SLIDER = "slider"
    LABEL = "label"
    PANEL = "panel"
    TEXT_INPUT = "text_input"


@dataclass
class UIEvent:
    """UI事件数据类"""
    type: str
    element_id: str
    data: Any = None


class BaseUIElement:
    """UI元素基类"""
    
    def __init__(self, element_id: str, rect, manager):
        self.element_id = element_id
        self.rect = rect
        self.manager = manager
        self.visible = True
        self.enabled = True
        self.element = None
    
    def show(self):
        """显示元素"""
        self.visible = True
        if self.element:
            self.element.show()
    
    def hide(self):
        """隐藏元素"""
        self.visible = False
        if self.element:
            self.element.hide()
    
    def enable(self):
        """启用元素"""
        self.enabled = True
        if self.element:
            self.element.enable()
    
    def disable(self):
        """禁用元素"""
        self.enabled = False
        if self.element:
            self.element.disable()
    
    def destroy(self):
        """销毁元素"""
        if self.element:
            self.element.kill()
            self.element = None


class UIButtonElement(BaseUIElement):
    """按钮UI元素"""
    
    def __init__(self, element_id: str, rect, text: str, manager):
        super().__init__(element_id, rect, manager)
        self.text = text
        self.callbacks: List[Callable] = []
        
        self.element = pygame_gui.elements.UIButton(
            relative_rect=rect,
            text=text,
            manager=manager,
            object_id=element_id
        )
    
    def add_callback(self, callback: Callable):
        """添加点击回调"""
        self.callbacks.append(callback)
    
    def handle_event(self, event):
        """处理事件"""
        if (event.type == pygame_gui.UI_BUTTON_PRESSED and 
            event.ui_element == self.element):
            for callback in self.callbacks:
                callback()


class UISliderElement(BaseUIElement):
    """滑块UI元素"""
    
    def __init__(self, element_id: str, rect, start_value: float, 
                 value_range: tuple, manager):
        super().__init__(element_id, rect, manager)
        self.start_value = start_value
        self.value_range = value_range
        self.callbacks: List[Callable] = []
        
        self.element = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=rect,
            start_value=start_value,
            value_range=value_range,
            manager=manager,
            object_id=element_id
        )
    
    def get_value(self) -> float:
        """获取当前值"""
        return self.element.get_current_value()
    
    def set_value(self, value: float):
        """设置值"""
        self.element.set_current_value(value)
    
    def add_callback(self, callback: Callable):
        """添加值改变回调"""
        self.callbacks.append(callback)
    
    def handle_event(self, event):
        """处理事件"""
        if (event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED and 
            event.ui_element == self.element):
            value = self.element.get_current_value()
            for callback in self.callbacks:
                callback(value)


class UILabelElement(BaseUIElement):
    """标签UI元素"""
    
    def __init__(self, element_id: str, rect, text: str, manager):
        super().__init__(element_id, rect, manager)
        self.text = text
        
        self.element = pygame_gui.elements.UILabel(
            relative_rect=rect,
            text=text,
            manager=manager,
            object_id=element_id
        )
    
    def set_text(self, text: str):
        """设置文本"""
        self.text = text
        self.element.set_text(text)


class UIPanelElement(BaseUIElement):
    """面板UI元素"""
    
    def __init__(self, element_id: str, rect, manager, title: str = ""):
        super().__init__(element_id, rect, manager)
        self.title = title
        self.elements: Dict[str, BaseUIElement] = {}
        
        self.element = pygame_gui.elements.UIPanel(
            relative_rect=rect,
            manager=manager,
            object_id=element_id,
            title=title
        )
    
    def add_element(self, element: BaseUIElement):
        """添加子元素"""
        self.elements[element.element_id] = element
    
    def remove_element(self, element_id: str):
        """移除子元素"""
        if element_id in self.elements:
            self.elements[element_id].destroy()
            del self.elements[element_id]


class GUIManager:
    """GUI管理器"""
    
    def __init__(self, screen_size: tuple, theme_file: str = None):
        self.screen_width, self.screen_height = screen_size
        self.logger = logging.getLogger(__name__)
        
        # 初始化UI管理器
        try:
            self.manager = pygame_gui.UIManager(
                (self.screen_width, self.screen_height),
                theme_file
            )
        except Exception as e:
            self.logger.warning(f"UI管理器初始化失败: {e}")
            self.manager = None
        
        # UI元素容器
        self.elements: Dict[str, BaseUIElement] = {}
        self.panels: Dict[str, UIPanelElement] = {}
        
        # 事件回调
        self.event_callbacks: Dict[str, List[Callable]] = {}
        
        # 默认主题
        self.default_theme = {
            'defaults': {
                'colours': {
                    'normal_bg': '#202020',
                    'hovered_bg': '#303030',
                    'disabled_bg': '#101010',
                    'normal_text': '#FFFFFF',
                    'hovered_text': '#CCCCCC',
                    'disabled_text': '#808080'
                }
            }
        }
        
        self.logger.info("GUIManager初始化完成")
    
    def create_button(self, element_id: str, rect, text: str) -> UIButtonElement:
        """创建按钮"""
        if not self.manager:
            return None
            
        button = UIButtonElement(element_id, rect, text, self.manager)
        self.elements[element_id] = button
        return button
    
    def create_slider(self, element_id: str, rect, start_value: float, 
                     value_range: tuple) -> UISliderElement:
        """创建滑块"""
        if not self.manager:
            return None
            
        slider = UISliderElement(element_id, rect, start_value, value_range, self.manager)
        self.elements[element_id] = slider
        return slider
    
    def create_label(self, element_id: str, rect, text: str) -> UILabelElement:
        """创建标签"""
        if not self.manager:
            return None
            
        label = UILabelElement(element_id, rect, text, self.manager)
        self.elements[element_id] = label
        return label
    
    def create_panel(self, element_id: str, rect, title: str = "") -> UIPanelElement:
        """创建面板"""
        if not self.manager:
            return None
            
        panel = UIPanelElement(element_id, rect, self.manager, title)
        self.panels[element_id] = panel
        self.elements[element_id] = panel
        return panel
    
    def add_event_callback(self, event_type: str, callback: Callable):
        """添加事件回调"""
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        self.event_callbacks[event_type].append(callback)
    
    def remove_event_callback(self, event_type: str, callback: Callable):
        """移除事件回调"""
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type].remove(callback)
    
    def process_events(self, event):
        """处理Pygame事件"""
        if not self.manager:
            return
            
        # 让UI管理器处理事件
        self.manager.process_events(event)
        
        # 处理自定义事件
        for element in self.elements.values():
            if hasattr(element, 'handle_event'):
                element.handle_event(event)
        
        # 触发注册的回调
        event_type = getattr(event, 'type', None)
        if event_type and event_type in self.event_callbacks:
            for callback in self.event_callbacks[event_type]:
                callback(event)
    
    def update(self, time_delta: float):
        """更新UI"""
        if self.manager:
            self.manager.update(time_delta)
    
    def draw(self, screen):
        """绘制UI"""
        if self.manager:
            self.manager.draw_ui(screen)
    
    def get_element(self, element_id: str) -> Optional[BaseUIElement]:
        """获取UI元素"""
        return self.elements.get(element_id)
    
    def remove_element(self, element_id: str):
        """移除UI元素"""
        if element_id in self.elements:
            self.elements[element_id].destroy()
            del self.elements[element_id]
            
            # 如果是面板，也要从面板字典中移除
            if element_id in self.panels:
                del self.panels[element_id]
    
    def show_all(self):
        """显示所有元素"""
        for element in self.elements.values():
            element.show()
    
    def hide_all(self):
        """隐藏所有元素"""
        for element in self.elements.values():
            element.hide()
    
    def cleanup(self):
        """清理UI资源"""
        # 销毁所有元素
        for element in self.elements.values():
            element.destroy()
        
        self.elements.clear()
        self.panels.clear()
        self.event_callbacks.clear()
        
        if self.manager:
            self.manager.clear_and_reset()
        
        self.logger.info("GUIManager资源清理完成")


class ControlPanel:
    """控制面板"""
    
    def __init__(self, gui_manager: GUIManager, position: tuple = (10, 10)):
        self.gui_manager = gui_manager
        self.position = position
        self.panel = None
        self.logger = logging.getLogger(__name__)
        
        self._create_panel()
        self._setup_controls()
    
    def _create_panel(self):
        """创建控制面板"""
        panel_width = 250
        panel_height = 400
        
        rect = pygame.Rect(
            self.position[0], 
            self.position[1], 
            panel_width, 
            panel_height
        )
        
        self.panel = self.gui_manager.create_panel(
            'control_panel',
            rect,
            '控制面板'
        )
    
    def _setup_controls(self):
        """设置控制元素"""
        if not self.panel:
            return
        
        # 性能控制组
        self._add_performance_controls()
        
        # 粒子效果控制组
        self._add_particle_controls()
        
        # AI控制组
        self._add_ai_controls()
    
    def _add_performance_controls(self):
        """添加性能控制"""
        # FPS显示
        fps_label = self.gui_manager.create_label(
            'fps_label',
            pygame.Rect(10, 10, 200, 20),
            'FPS: 60'
        )
        
        # 目标FPS滑块
        fps_slider = self.gui_manager.create_slider(
            'target_fps_slider',
            pygame.Rect(10, 40, 200, 20),
            60,  # 默认值
            (30, 120)  # 范围
        )
        
        # 添加到面板
        self.panel.add_element(fps_label)
        self.panel.add_element(fps_slider)
    
    def _add_particle_controls(self):
        """添加粒子效果控制"""
        # 粒子效果开关
        particle_toggle = self.gui_manager.create_button(
            'particle_toggle',
            pygame.Rect(10, 80, 200, 30),
            '粒子效果: 开启'
        )
        
        # 粒子密度滑块
        density_slider = self.gui_manager.create_slider(
            'particle_density_slider',
            pygame.Rect(10, 120, 200, 20),
            50,  # 默认值
            (10, 100)  # 范围
        )
        
        # 特效按钮
        explosion_btn = self.gui_manager.create_button(
            'explosion_btn',
            pygame.Rect(10, 150, 90, 30),
            '爆炸'
        )
        
        sparkle_btn = self.gui_manager.create_button(
            'sparkle_btn',
            pygame.Rect(110, 150, 90, 30),
            '闪光'
        )
        
        # 添加到面板
        self.panel.add_element(particle_toggle)
        self.panel.add_element(density_slider)
        self.panel.add_element(explosion_btn)
        self.panel.add_element(sparkle_btn)
    
    def _add_ai_controls(self):
        """添加AI控制"""
        # AI开关
        ai_toggle = self.gui_manager.create_button(
            'ai_toggle',
            pygame.Rect(10, 200, 200, 30),
            'AI检测: 开启'
        )
        
        # 检测置信度滑块
        confidence_slider = self.gui_manager.create_slider(
            'confidence_slider',
            pygame.Rect(10, 240, 200, 20),
            0.5,  # 默认值
            (0.1, 0.9)  # 范围
        )
        
        # 添加到面板
        self.panel.add_element(ai_toggle)
        self.panel.add_element(confidence_slider)
    
    def update_fps_display(self, fps: float):
        """更新FPS显示"""
        fps_label = self.gui_manager.get_element('fps_label')
        if fps_label:
            fps_label.set_text(f'FPS: {fps:.1f}')
    
    def get_target_fps(self) -> int:
        """获取目标FPS"""
        slider = self.gui_manager.get_element('target_fps_slider')
        return int(slider.get_value()) if slider else 60
    
    def is_particles_enabled(self) -> bool:
        """检查粒子效果是否启用"""
        toggle = self.gui_manager.get_element('particle_toggle')
        # 这里需要根据按钮文本判断状态
        return True  # 简化实现
    
    def get_particle_density(self) -> int:
        """获取粒子密度"""
        slider = self.gui_manager.get_element('particle_density_slider')
        return int(slider.get_value()) if slider else 50
    
    def is_ai_enabled(self) -> bool:
        """检查AI是否启用"""
        toggle = self.gui_manager.get_element('ai_toggle')
        return True  # 简化实现
    
    def get_confidence_threshold(self) -> float:
        """获取检测置信度阈值"""
        slider = self.gui_manager.get_element('confidence_slider')
        return slider.get_value() if slider else 0.5
    
    def get_control_values(self) -> Dict[str, Any]:
        """获取所有控制值"""
        return {
            'target_fps': self.get_target_fps(),
            'particles_enabled': self.is_particles_enabled(),
            'particle_density': self.get_particle_density(),
            'ai_enabled': self.is_ai_enabled(),
            'confidence_threshold': self.get_confidence_threshold()
        }


class StatusBar:
    """状态栏"""
    
    def __init__(self, gui_manager: GUIManager, screen_size: tuple):
        self.gui_manager = gui_manager
        self.screen_width, self.screen_height = screen_size
        self.status_bar = None
        self.logger = logging.getLogger(__name__)
        
        self._create_status_bar()
    
    def _create_status_bar(self):
        """创建状态栏"""
        bar_height = 30
        rect = pygame.Rect(
            0,
            self.screen_height - bar_height,
            self.screen_width,
            bar_height
        )
        
        self.status_bar = self.gui_manager.create_panel(
            'status_bar',
            rect,
            ''
        )
        
        # 添加状态信息
        self._add_status_labels()
    
    def _add_status_labels(self):
        """添加状态标签"""
        # 系统状态
        system_label = self.gui_manager.create_label(
            'system_status',
            pygame.Rect(10, 5, 150, 20),
            '系统: 运行中'
        )
        
        # 内存使用
        memory_label = self.gui_manager.create_label(
            'memory_status',
            pygame.Rect(170, 5, 150, 20),
            '内存: 150MB'
        )
        
        # AI状态
        ai_label = self.gui_manager.create_label(
            'ai_status',
            pygame.Rect(330, 5, 150, 20),
            'AI: 就绪'
        )
        
        # 添加到状态栏
        self.status_bar.add_element(system_label)
        self.status_bar.add_element(memory_label)
        self.status_bar.add_element(ai_label)
    
    def update_system_status(self, status: str):
        """更新系统状态"""
        label = self.gui_manager.get_element('system_status')
        if label:
            label.set_text(f'系统: {status}')
    
    def update_memory_status(self, memory_mb: float):
        """更新内存状态"""
        label = self.gui_manager.get_element('memory_status')
        if label:
            label.set_text(f'内存: {memory_mb:.0f}MB')
    
    def update_ai_status(self, status: str):
        """更新AI状态"""
        label = self.gui_manager.get_element('ai_status')
        if label:
            label.set_text(f'AI: {status}')


class GUISystem:
    """图形用户界面系统"""
    
    def __init__(self, screen_size: tuple, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 初始化GUI管理器
        self.gui_manager = GUIManager(screen_size)
        
        # 创建主要UI组件
        self.control_panel = ControlPanel(self.gui_manager)
        self.status_bar = StatusBar(self.gui_manager, screen_size)
        
        # 事件处理
        self.event_handlers = {}
        
        self.logger.info("GUISystem初始化完成")
    
    def initialize(self) -> bool:
        """初始化GUI系统"""
        try:
            # 设置默认事件处理
            self._setup_event_handlers()
            return True
        except Exception as e:
            self.logger.error(f"GUI系统初始化失败: {e}")
            return False
    
    def _setup_event_handlers(self):
        """设置事件处理器"""
        # 按钮点击事件
        def handle_button_click(event):
            button_id = event.ui_element.object_ids[-1] if event.ui_element.object_ids else ""
            self.logger.info(f"按钮点击: {button_id}")
            
            # 特殊按钮处理
            if button_id == 'explosion_btn':
                self.trigger_callback('effect_trigger', 'explosion')
            elif button_id == 'sparkle_btn':
                self.trigger_callback('effect_trigger', 'sparkle')
        
        # 滑块变化事件
        def handle_slider_change(event):
            slider_id = event.ui_element.object_ids[-1] if event.ui_element.object_ids else ""
            value = event.value
            self.logger.info(f"滑块变化: {slider_id} = {value}")
            
            if slider_id == 'target_fps_slider':
                self.trigger_callback('fps_change', int(value))
            elif slider_id == 'particle_density_slider':
                self.trigger_callback('density_change', int(value))
            elif slider_id == 'confidence_slider':
                self.trigger_callback('confidence_change', value)
        
        # 注册事件处理器
        self.gui_manager.add_event_callback(pygame_gui.UI_BUTTON_PRESSED, handle_button_click)
        self.gui_manager.add_event_callback(pygame_gui.UI_HORIZONTAL_SLIDER_MOVED, handle_slider_change)
    
    def process_events(self, event):
        """处理事件"""
        self.gui_manager.process_events(event)
    
    def update(self, time_delta: float, performance_data: Dict[str, Any] = None):
        """更新GUI"""
        self.gui_manager.update(time_delta)
        
        # 更新性能数据显示
        if performance_data:
            self._update_performance_display(performance_data)
    
    def _update_performance_display(self, data: Dict[str, Any]):
        """更新性能显示"""
        if 'fps' in data:
            self.control_panel.update_fps_display(data['fps'])
        
        if 'memory_mb' in data:
            self.status_bar.update_memory_status(data['memory_mb'])
    
    def draw(self, screen):
        """绘制GUI"""
        self.gui_manager.draw(screen)
    
    def add_callback(self, event_type: str, callback: Callable):
        """添加回调函数"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(callback)
    
    def trigger_callback(self, event_type: str, data=None):
        """触发回调"""
        if event_type in self.event_handlers:
            for callback in self.event_handlers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"回调执行出错: {e}")
    
    def get_control_values(self) -> Dict[str, Any]:
        """获取控制面板的当前值"""
        return {
            'target_fps': self.control_panel.get_target_fps(),
            'particles_enabled': self.control_panel.is_particles_enabled(),
            'particle_density': self.control_panel.get_particle_density(),
            'ai_enabled': self.control_panel.is_ai_enabled(),
            'confidence_threshold': self.control_panel.get_confidence_threshold()
        }
    
    def cleanup(self):
        """清理GUI系统"""
        self.gui_manager.cleanup()
        self.event_handlers.clear()
        self.logger.info("GUISystem资源清理完成")