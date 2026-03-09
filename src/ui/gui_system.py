"""
GUI System - 图形用户界面系统
提供直观的图形化操作界面，包含菜单栏和文件输入功能
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from enum import Enum

try:
    import pygame
    import pygame_gui
    from pygame_gui.elements import UIButton, UILabel, UIPanel, UIHorizontalSlider, UIDropDownMenu
    from pygame_gui.core import UIElement
except ImportError as e:
    print(f"GUI 依赖导入失败：{e}")
    # 创建模拟类以便程序能运行
    class MockPygameGUI:

        def __init__(self, *args, **kwargs):
            pass
            
        class UIManager:
            def __init__(self, *args, **kwargs):
                pass
                
            def process_events(self, event):
                pass
                
            def update(self, time_delta):
                pass
                
            def draw_ui(self, screen):
                pass
                
            def clear_and_reset(self):
                pass
                
        class elements:
            class UIButton:
                def __init__(self, *args, **kwargs):
                    self.object_ids = []
                    
                def show(self):
                    pass
                    
                def hide(self):
                    pass
                    
                def enable(self):
                    pass
                    
                def disable(self):
                    pass
                    
                def kill(self):
                    pass
                    
            class UILabel:
                def __init__(self, *args, **kwargs):
                    self.object_ids = []
                    
                def show(self):
                    pass
                    
                def hide(self):
                    pass
                    
                def enable(self):
                    pass
                    
                def disable(self):
                    pass
                    
                def kill(self):
                    pass
                    
                def set_text(self, text):
                    pass
                    
            class UIPanel:
                def __init__(self, *args, **kwargs):
                    self.object_ids = []
                    
                def show(self):
                    pass
                    
                def hide(self):
                    pass
                    
                def enable(self):
                    pass
                    
                def disable(self):
                    pass
                    
                def kill(self):
                    pass
                    
            class UISlider:
                def __init__(self, *args, **kwargs):
                    self.object_ids = []
                    self.value = 0
                    
                def show(self):
                    pass
                    
                def hide(self):
                    pass
                    
                def enable(self):
                    pass
                    
                def disable(self):
                    pass
                    
                def kill(self):
                    pass
                    
                def get_current_value(self):
                    return self.value
                    
                def set_current_value(self, value):
                    self.value = value
                    
            class UIMenuBar:
                def __init__(self, *args, **kwargs):
                    self.object_ids = []
                    
                def show(self):
                    pass
                    
                def hide(self):
                    pass
                    
                def enable(self):
                    pass
                    
                def disable(self):
                    pass
                    
                def kill(self):
                    pass
                    
            class UIDropDownMenu:
                def __init__(self, *args, **kwargs):
                    self.object_ids = []
                    self.selected_option = ""
                    
                def show(self):
                    pass
                    
                def hide(self):
                    pass
                    
                def enable(self):
                    pass
                    
                def disable(self):
                    pass
                    
                def kill(self):
                    pass
                    
                def select_option_by_text(self, option):
                    self.selected_option = option
                    
            class UIHorizontalScrollBar:
                def __init__(self, *args, **kwargs):
                    self.object_ids = []
                    
                def show(self):
                    pass
                    
                def hide(self):
                    pass
                    
                def enable(self):
                    pass
                    
                def disable(self):
                    pass
                    
                def kill(self):
                    pass
                    
    # 添加必要的常量
    MockPygameGUI.UI_BUTTON_PRESSED = "UI_BUTTON_PRESSED"
    MockPygameGUI.UI_HORIZONTAL_SLIDER_MOVED = "UI_HORIZONTAL_SLIDER_MOVED"
    
    pygame_gui = MockPygameGUI()


class UIElementType(Enum):
    """UI 元素类型枚举"""
    BUTTON = "button"
    SLIDER = "slider"
    LABEL = "label"
    PANEL = "panel"
    TEXT_INPUT = "text_input"
    MENU_BAR = "menu_bar"
    DROP_DOWN = "drop_down"


@dataclass
class UIEvent:
    """UI 事件数据类"""
    type: str
    element_id: str
    data: Any = None


class BaseUIElement:
    """UI 元素基类"""
    
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
    """按钮 UI 元素"""
    
    def __init__(self, element_id: str, rect, text: str, manager):
        super().__init__(element_id, rect, manager)
        self.text = text
        self.callbacks: List[Callable] = []
        
        try:
            self.element = pygame_gui.elements.UIButton(
                relative_rect=rect,
                text=text,
                manager=manager,
                object_id=f'#{element_id}'
            )
        except Exception as e:
            logging.error(f"按钮创建失败：{e}")
    
    def add_callback(self, callback: Callable):
        """添加点击回调"""
        self.callbacks.append(callback)
    
    def trigger_callbacks(self):
        """触发所有回调"""
        for callback in self.callbacks:
            callback()


class UISliderElement(BaseUIElement):
    """滑块 UI 元素"""
    
    def __init__(self, element_id: str, rect, start_value: float, 
                 value_range: tuple, manager):
        super().__init__(element_id, rect, manager)
        self.start_value = start_value
        self.value_range = value_range
        self.callbacks: List[Callable] = []
        
        try:
            # 使用 UIHorizontalSlider 代替 UISlider
            self.element = UIHorizontalSlider(
                relative_rect=rect,
                start_value=start_value,
                value_range=value_range,
                manager=manager,
                object_id=f'#{element_id}'
            )
        except Exception as e:
            logging.error(f"滑块创建失败：{e}")
    
    def get_value(self) -> float:
        """获取滑块值"""
        return self.element.get_current_value() if self.element else self.start_value
    
    def set_value(self, value: float):
        """设置滑块值"""
        if self.element:
            self.element.set_current_value(value)
    
    def add_callback(self, callback: Callable):
        """添加值变化回调"""
        self.callbacks.append(callback)
    
    def trigger_callbacks(self, value: float):
        """触发所有回调"""
        for callback in self.callbacks:
            callback(value)


class UILabelElement(BaseUIElement):
    """标签 UI 元素"""
    
    def __init__(self, element_id: str, rect, text: str, manager):
        super().__init__(element_id, rect, manager)
        self.text = text
        
        try:
            self.element = pygame_gui.elements.UILabel(
                relative_rect=rect,
                text=text,
                manager=manager,
                object_id=f'#{element_id}'
            )
        except Exception as e:
            logging.error(f"标签创建失败：{e}")
    
    def set_text(self, text: str):
        """设置标签文本"""
        self.text = text
        if self.element:
            self.element.set_text(text)


class UIPanelElement(BaseUIElement):
    """面板 UI 元素"""
    
    def __init__(self, element_id: str, rect, manager, title: str = ""):
        super().__init__(element_id, rect, manager)
        self.title = title
        
        try:
            self.element = pygame_gui.elements.UIPanel(
                relative_rect=rect,
                manager=manager,
                object_id=f'#{element_id}',
                starting_height=0
            )
        except Exception as e:
            logging.error(f"面板创建失败：{e}")
    
    def add_element(self, element: BaseUIElement):
        """添加子元素"""
        if self.element and hasattr(element.element, 'container'):
            element.element.container = self.element


class UIMenuBarElement(BaseUIElement):
    """菜单栏 UI 元素"""
    
    def __init__(self, element_id: str, rect, menu_items: List[str], manager):
        super().__init__(element_id, rect, manager)
        self.menu_items = menu_items
        self.callbacks: Dict[str, Callable] = {}
        
        try:
            self.element = pygame_gui.elements.UIHorizontalScrollBar(
                relative_rect=rect,
                manager=manager,
                object_id=f'#{element_id}'
            )
            
            # 创建菜单项按钮
            self._create_menu_buttons(menu_items)
        except Exception as e:
            logging.error(f"菜单栏创建失败：{e}")
    
    def _create_menu_buttons(self, menu_items: List[str]):
        """创建菜单项按钮"""
        x_offset = 5
        for item in menu_items:
            btn = UIButtonElement(
                f'{self.element_id}_{item}',
                pygame.Rect(x_offset, 5, 80, 25),
                item,
                self.manager
            )
            setattr(self, f'btn_{item}', btn)
            x_offset += 85
    
    def add_callback(self, menu_item: str, callback: Callable):
        """添加菜单项回调"""
        self.callbacks[menu_item] = callback
    
    def trigger_callback(self, menu_item: str):
        """触发菜单项回调"""
        if menu_item in self.callbacks:
            self.callbacks[menu_item]()


class UIDropDownElement(BaseUIElement):
    """下拉菜单 UI 元素"""
    
    def __init__(self, element_id: str, rect, options_list: List[str], 
                 manager, starting_option: str = ""):
        super().__init__(element_id, rect, manager)
        self.options_list = options_list
        self.current_option = starting_option or (options_list[0] if options_list else "")
        self.callbacks: List[Callable] = []
        
        try:
            self.element = pygame_gui.elements.UIDropDownMenu(
                options_list=options_list,
                starting_option=self.current_option,
                relative_rect=rect,
                manager=manager,
                object_id=f'#{element_id}'
            )
        except Exception as e:
            logging.error(f"下拉菜单创建失败：{e}")
    
    def get_selected_option(self) -> str:
        """获取当前选项"""
        if self.element:
            return self.element.selected_option
        return self.current_option
    
    def set_selected_option(self, option: str):
        """设置当前选项"""
        if self.element:
            self.element.select_option_by_text(option)
        self.current_option = option
    
    def add_callback(self, callback: Callable):
        """添加选择变化回调"""
        self.callbacks.append(callback)
    
    def trigger_callbacks(self, option: str):
        """触发所有回调"""
        for callback in self.callbacks:
            callback(option)


class GUIManager:
    """GUI管理器"""
    
    def __init__(self, screen_size: tuple, theme_file: str = None):
        self.screen_width, self.screen_height = screen_size
        self.logger = logging.getLogger(__name__)
        
        # 查找主题文件
        if theme_file is None:
            # 使用默认主题路径
            theme_path = Path(__file__).parent / "theme.json"
            if theme_path.exists():
                theme_file = str(theme_path)
                self.logger.info(f"使用主题文件：{theme_file}")
            else:
                self.logger.warning("未找到主题文件，使用默认样式")
        
        # 初始化 UI管理器
        try:
            self.manager = pygame_gui.UIManager(
                (self.screen_width, self.screen_height),
                theme_file
            )
            self.logger.info("UI管理器初始化成功")
        except Exception as e:
            self.logger.warning(f"UI管理器初始化失败：{e}")
            try:
                # 尝试不使用主题文件
                self.manager = pygame_gui.UIManager(
                    (self.screen_width, self.screen_height)
                )
                self.logger.info("UI管理器使用默认配置初始化")
            except Exception as e2:
                self.logger.error(f"UI管理器初始化失败：{e2}")
                self.manager = None
        
        # UI 元素容器
        self.elements: Dict[str, BaseUIElement] = {}
        self.panels: Dict[str, UIPanelElement] = {}
        
        # 事件回调
        self.event_callbacks: Dict[str, List[Callable]] = {}
        
        self.logger.info("GUIManager 初始化完成")
    
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
    
    def create_menu_bar(self, element_id: str, rect, menu_items: List[str]) -> UIMenuBarElement:
        """创建菜单栏"""
        if not self.manager:
            return None
            
        menu_bar = UIMenuBarElement(element_id, rect, menu_items, self.manager)
        self.elements[element_id] = menu_bar
        return menu_bar
    
    def create_drop_down(self, element_id: str, rect, options_list: List[str], 
                        starting_option: str = "") -> UIDropDownElement:
        """创建下拉菜单"""
        if not self.manager:
            return None
            
        drop_down = UIDropDownElement(element_id, rect, options_list, self.manager, starting_option)
        self.elements[element_id] = drop_down
        return drop_down
    
    def get_element(self, element_id: str) -> Optional[BaseUIElement]:
        """获取 UI 元素"""
        return self.elements.get(element_id)
    
    def remove_element(self, element_id: str):
        """移除 UI 元素"""
        if element_id in self.elements:
            element = self.elements[element_id]
            element.destroy()
            del self.elements[element_id]
    
    def process_events(self, event):
        """处理事件"""
        if self.manager:
            self.manager.process_events(event)
            
            # 检查 UI 事件并触发回调
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    element_id = event.ui_element.object_ids[-1] if event.ui_element.object_ids else ""
                    element = self.get_element(element_id.replace('#', ''))
                    if element and hasattr(element, 'trigger_callbacks'):
                        element.trigger_callbacks()
    
    def update(self, time_delta: float):
        """更新 GUI"""
        if self.manager:
            self.manager.update(time_delta)
    
    def draw(self, screen):
        """绘制 GUI"""
        if self.manager:
            self.manager.draw_ui(screen)
    
    def add_event_callback(self, event_type: str, callback: Callable):
        """添加事件回调"""
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        self.event_callbacks[event_type].append(callback)
    
    def show_all(self):
        """显示所有元素"""
        for element in self.elements.values():
            element.show()
    
    def hide_all(self):
        """隐藏所有元素"""
        for element in self.elements.values():
            element.hide()
    
    def cleanup(self):
        """清理 UI 资源"""
        # 销毁所有元素
        for element in self.elements.values():
            element.destroy()
        
        self.elements.clear()
        self.panels.clear()
        self.event_callbacks.clear()
        
        if self.manager:
            self.manager.clear_and_reset()
        
        self.logger.info("GUIManager 资源清理完成")


class MenuBar:
    """菜单栏类"""
    
    def __init__(self, gui_manager: GUIManager):
        self.gui_manager = gui_manager
        self.menu_bar = None
        self.logger = logging.getLogger(__name__)
        
        self._create_menu_bar()
    
    def _create_menu_bar(self):
        """创建菜单栏"""
        # 创建顶部菜单栏
        menu_rect = pygame.Rect(0, 0, self.gui_manager.screen_width, 30)
        
        # 定义菜单项
        menu_items = [
            "文件",
            "编辑",
            "视图",
            "工具",
            "帮助"
        ]
        
        self.menu_bar = self.gui_manager.create_menu_bar('main_menu_bar', menu_rect, menu_items)
        
        # 设置菜单项回调
        if self.menu_bar:
            self.menu_bar.add_callback("文件", self._on_file_menu)
            self.menu_bar.add_callback("编辑", self._on_edit_menu)
            self.menu_bar.add_callback("视图", self._on_view_menu)
            self.menu_bar.add_callback("工具", self._on_tools_menu)
            self.menu_bar.add_callback("帮助", self._on_help_menu)
    
    def _on_file_menu(self):
        """文件菜单处理"""
        self.logger.info("文件菜单被点击")
        # 这里可以弹出下拉菜单或执行其他操作
    
    def _on_edit_menu(self):
        """编辑菜单处理"""
        self.logger.info("编辑菜单被点击")
    
    def _on_view_menu(self):
        """视图菜单处理"""
        self.logger.info("视图菜单被点击")
    
    def _on_tools_menu(self):
        """工具菜单处理"""
        self.logger.info("工具菜单被点击")
    
    def _on_help_menu(self):
        """帮助菜单处理"""
        self.logger.info("帮助菜单被点击")


class ControlPanel:
    """控制面板"""
    
    def __init__(self, gui_manager: GUIManager, position: tuple = (10, 40)):  # 调整 Y 坐标以避开菜单栏
        self.gui_manager = gui_manager
        self.position = position
        self.panel = None
        self.logger = logging.getLogger(__name__)
        
        self._create_panel()
        self._setup_controls()
    
    def _create_panel(self):
        """创建控制面板"""
        panel_width = 250
        panel_height = 500  # 增加高度以容纳文件输入控件
        
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
        
        # 文件输入控制组（新增）
        self._add_file_input_controls()
    
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
    
    def _add_file_input_controls(self):
        """添加文件输入控制（新增）"""
        # 文件输入标题
        file_title = self.gui_manager.create_label(
            'file_input_title',
            pygame.Rect(10, 280, 200, 20),
            '文件输入:'
        )
        
        # 图像文件选择
        image_file_btn = self.gui_manager.create_button(
            'image_file_btn',
            pygame.Rect(10, 305, 200, 30),
            '选择图像文件'
        )
        
        # 视频文件选择
        video_file_btn = self.gui_manager.create_button(
            'video_file_btn',
            pygame.Rect(10, 340, 200, 30),
            '选择视频文件'
        )
        
        # 配置文件选择
        config_file_btn = self.gui_manager.create_button(
            'config_file_btn',
            pygame.Rect(10, 375, 200, 30),
            '选择配置文件'
        )
        
        # 文件路径显示
        self.file_path_label = self.gui_manager.create_label(
            'selected_file_label',
            pygame.Rect(10, 410, 200, 60),
            '未选择文件'
        )
        
        # 添加到面板
        self.panel.add_element(file_title)
        self.panel.add_element(image_file_btn)
        self.panel.add_element(video_file_btn)
        self.panel.add_element(config_file_btn)
        self.panel.add_element(self.file_path_label)
    
    def update_selected_file(self, file_path: str):
        """更新选中的文件显示"""
        if self.file_path_label:
            # 截断长路径显示
            if len(file_path) > 30:
                display_path = "..." + file_path[-27:]
            else:
                display_path = file_path
            self.file_path_label.set_text(f"已选择:\n{display_path}")
    
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
        # 状态栏面板
        status_rect = pygame.Rect(0, self.screen_height - 30, self.screen_width, 30)
        self.status_bar = self.gui_manager.create_panel('status_bar', status_rect)
        
        # 状态文本
        self.status_label = self.gui_manager.create_label(
            'status_text',
            pygame.Rect(10, 5, 300, 20),
            '就绪'
        )
        
        # 文件状态
        self.file_status_label = self.gui_manager.create_label(
            'file_status',
            pygame.Rect(self.screen_width - 200, 5, 190, 20),
            '无文件'
        )
        
        # 添加到状态栏
        if self.status_bar:
            self.status_bar.add_element(self.status_label)
            self.status_bar.add_element(self.file_status_label)
    
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
    """GUI系统主类"""
    
    def __init__(self, screen_size: tuple, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 初始化GUI管理器
        self.gui_manager = GUIManager(screen_size)
        
        # 创建菜单栏
        self.menu_bar = MenuBar(self.gui_manager)
        
        # 创建主要 UI组件
        self.control_panel = ControlPanel(self.gui_manager)
        self.status_bar = StatusBar(self.gui_manager, screen_size)
        
        # 事件处理
        self.event_handlers = {}
        self.file_callbacks = {}  # 文件相关回调
        
        self.logger.info("GUISystem 初始化完成")
    
    def initialize(self) -> bool:
        """初始化GUI系统"""
        try:
            # 设置默认事件处理
            self._setup_event_handlers()
            self._setup_file_handlers()
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
    
    def _setup_file_handlers(self):
        """设置文件处理回调"""
        def handle_image_file_select():
            """处理图像文件选择"""
            self._select_file_and_process('image')
        
        def handle_video_file_select():
            """处理视频文件选择"""
            self._select_file_and_process('video')
        
        def handle_config_file_select():
            """处理配置文件选择"""
            self._select_file_and_process('config')
        
        # 注册文件选择按钮回调
        image_btn = self.gui_manager.get_element('image_file_btn')
        if image_btn:
            image_btn.add_callback(handle_image_file_select)
        
        video_btn = self.gui_manager.get_element('video_file_btn')
        if video_btn:
            video_btn.add_callback(handle_video_file_select)
        
        config_btn = self.gui_manager.get_element('config_file_btn')
        if config_btn:
            config_btn.add_callback(handle_config_file_select)
    
    def _select_file_and_process(self, file_type: str):
        """选择并处理文件"""
        try:
            # 这里应该调用实际的文件选择系统
            # 暂时使用模拟实现
            file_path = self._mock_file_selection(file_type)
            if file_path:
                self.control_panel.update_selected_file(file_path)
                self.status_bar.update_file_status(f"{file_type}已加载")
                
                # 触发文件处理回调
                self._trigger_file_callback(file_type, file_path)
        except Exception as e:
            self.logger.error(f"文件选择处理出错: {e}")
            self.status_bar.update_file_status("错误")
    
    def _mock_file_selection(self, file_type: str) -> str:
        """模拟文件选择（用于演示）"""
        mock_files = {
            'image': 'sample_image.png',
            'video': 'sample_video.mp4',
            'config': 'config.yaml'
        }
        return mock_files.get(file_type, f'sample_{file_type}.dat')
    
    def _trigger_file_callback(self, file_type: str, file_path: str):
        """触发文件回调"""
        callback_key = f'{file_type}_selected'
        if callback_key in self.file_callbacks:
            for callback in self.file_callbacks[callback_key]:
                try:
                    callback(file_path)
                except Exception as e:
                    self.logger.error(f"文件回调执行出错: {e}")
    
    def add_file_callback(self, file_type: str, callback: Callable):
        """添加文件处理回调"""
        callback_key = f'{file_type}_selected'
        if callback_key not in self.file_callbacks:
            self.file_callbacks[callback_key] = []
        self.file_callbacks[callback_key].append(callback)
    
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
        self.event_handlers.clear()
        self.file_callbacks.clear()
        self.gui_manager.cleanup()
        self.logger.info("GUISystem资源清理完成")