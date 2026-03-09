"""
Menu System - 菜单系统
提供完整的菜单栏功能，包括文件、编辑、视图、工具和帮助菜单
"""

import logging
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass

try:
    import pygame
    import pygame_gui
except ImportError as e:
    print(f"GUI依赖导入失败：{e}")
    pygame = None
    pygame_gui = None


class MenuSystem:
    """菜单系统主类"""
    
    def __init__(self, screen_size: tuple):
        self.screen_width, self.screen_height = screen_size
        self.logger = logging.getLogger(__name__)
        
        # 菜单回调
        self.menu_callbacks: Dict[str, Callable] = {}
        
        # 菜单状态
        self.menu_enabled = True
        
        self.logger.info("MenuSystem 初始化完成")
    
    def initialize(self, manager) -> bool:
        """初始化菜单系统"""
        try:
            self.manager = manager
            
            # 创建菜单栏
            self._create_menu_bar()
            
            self.logger.info("菜单系统初始化成功")
            return True
        except Exception as e:
            self.logger.error(f"菜单系统初始化失败：{e}")
            return False
    
    def _create_menu_bar(self):
        """创建菜单栏"""
        if not self.manager:
            return
        
        # 菜单栏矩形区域
        menu_rect = pygame.Rect(0, 0, self.screen_width, 30)
        
        # 创建菜单栏背景面板
        self.menu_panel = pygame_gui.elements.UIPanel(
            relative_rect=menu_rect,
            manager=self.manager,
            object_id='#menu_panel'
        )
        
        # 定义菜单项
        self.menu_items = {
            '文件': ['新建', '打开', '保存', '另存为', '-', '退出'],
            '编辑': ['撤销', '重做', '-', '剪切', '复制', '粘贴'],
            '视图': ['全屏', '重置视图', '-', '显示 FPS', '显示控制台'],
            '工具': ['设置', '插件管理', '-', '文件浏览器'],
            '帮助': ['关于', '使用指南', '-', '检查更新']
        }
        
        # 创建菜单按钮
        self._create_menu_buttons()
    
    def _create_menu_buttons(self):
        """创建菜单按钮"""
        x_offset = 5
        button_width = 60
        button_height = 25
        
        for menu_name in self.menu_items.keys():
            btn_rect = pygame.Rect(x_offset, 3, button_width, button_height)
            button = pygame_gui.elements.UIButton(
                relative_rect=btn_rect,
                text=menu_name,
                manager=self.manager,
                parent=self.menu_panel,
                object_id=f'#menu_btn_{menu_name}'
            )
            setattr(self, f'btn_{menu_name}', button)
            x_offset += button_width + 5
    
    def set_callback(self, menu_item: str, submenu_item: str, callback: Callable):
        """设置菜单项回调"""
        key = f"{menu_item}.{submenu_item}"
        self.menu_callbacks[key] = callback
        self.logger.info(f"设置菜单回调：{key}")
    
    def handle_menu_click(self, menu_name: str, submenu_name: str):
        """处理菜单点击事件"""
        key = f"{menu_name}.{submenu_name}"
        if key in self.menu_callbacks:
            try:
                self.menu_callbacks[key]()
                self.logger.info(f"执行菜单回调：{key}")
            except Exception as e:
                self.logger.error(f"菜单回调执行失败 {key}: {e}")
        else:
            self.logger.info(f"菜单项被点击：{menu_name} > {submenu_name}")
    
    def enable_menu(self, menu_name: str):
        """启用菜单"""
        button = getattr(self, f'btn_{menu_name}', None)
        if button:
            button.enable()
    
    def disable_menu(self, menu_name: str):
        """禁用菜单"""
        button = getattr(self, f'btn_{menu_name}', None)
        if button:
            button.disable()
    
    def update(self, time_delta: float):
        """更新菜单系统"""
        pass
    
    def process_events(self, event):
        """处理菜单事件"""
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                button_id = event.ui_element.object_ids[-1] if event.ui_element.object_ids else ""
                
                # 检查是否是菜单按钮
                if button_id.startswith('#menu_btn_'):
                    menu_name = button_id.replace('#menu_btn_', '')
                    self.logger.info(f"菜单按钮点击：{menu_name}")
                    # 这里可以弹出下拉菜单
    
    def cleanup(self):
        """清理菜单系统"""
        self.menu_callbacks.clear()
        self.logger.info("MenuSystem 资源清理完成")


class MenuActions:
    """菜单动作集合"""
    
    def __init__(self, engine=None, gui_system=None):
        self.engine = engine
        self.gui_system = gui_system
        self.logger = logging.getLogger(__name__)
    
    # 文件菜单动作
    def on_file_new(self):
        """新建文件"""
        self.logger.info("新建文件")
    
    def on_file_open(self):
        """打开文件"""
        self.logger.info("打开文件")
        # 调用文件输入系统
        if self.gui_system and hasattr(self.gui_system, '_select_file_and_process'):
            self.gui_system._select_file_and_process('config')
    
    def on_file_save(self):
        """保存文件"""
        self.logger.info("保存文件")
    
    def on_file_save_as(self):
        """另存为文件"""
        self.logger.info("另存为文件")
    
    def on_file_exit(self):
        """退出程序"""
        self.logger.info("退出程序")
        if self.engine:
            self.engine.running = False
    
    # 编辑菜单动作
    def on_edit_undo(self):
        """撤销"""
        if hasattr(self.engine, 'command_history'):
            if len(self.engine.command_history) > 0:
                command = self.engine.command_history.pop()
                command.undo()
                self.engine.redo_stack.append(command)
                self.logger.info("撤销操作成功")
            else:
                self.logger.warning("没有可撤销的操作")
    
    def on_edit_redo(self):
        """重做"""
        if hasattr(self.engine, 'redo_stack'):
            if len(self.engine.redo_stack) > 0:
                command = self.engine.redo_stack.pop()
                command.execute()
                self.engine.command_history.append(command)
                self.logger.info("重做操作成功")
            else:
                self.logger.warning("没有可重做的操作")
    
    def on_edit_cut(self):
        """剪切"""
        self.logger.info("剪切")
    
    def on_edit_copy(self):
        """复制"""
        self.logger.info("复制")
    
    def on_edit_paste(self):
        """粘贴"""
        self.logger.info("粘贴")
    
    # 视图菜单动作
    def on_view_fullscreen(self):
        """切换全屏"""
        self.logger.info("切换全屏模式")
        if self.engine and hasattr(self.engine, 'renderer'):
            is_fullscreen = self.engine.renderer.toggle_fullscreen()
            # 更新菜单状态
            if hasattr(self.engine, 'native_menu'):
                self.engine.native_menu.fullscreen = is_fullscreen
    
    def on_view_reset(self):
        """重置视图"""
        self.logger.info("重置视图")
    
    def on_view_toggle_fps(self):
        """切换 FPS 显示"""
        if hasattr(self.engine, 'show_fps'):
            self.engine.show_fps = not self.engine.show_fps
            self.logger.info(f"FPS 显示: {'开启' if self.engine.show_fps else '关闭'}")
        else:
            self.engine.show_fps = True
            self.logger.info("FPS 显示: 开启")
    
    def on_view_toggle_console(self):
        """切换控制台"""
        self.logger.info("切换控制台")
    
    # 工具菜单动作
    def on_tools_settings(self):
        """打开设置"""
        self.logger.info("打开设置")
    
    def on_tools_plugins(self):
        """插件管理"""
        self.logger.info("插件管理")
    
    def on_tools_file_browser(self):
        """文件浏览器"""
        self.logger.info("打开文件浏览器")
        if self.gui_system and hasattr(self.gui_system, '_select_file_and_process'):
            self.gui_system._select_file_and_process('any')
    
    # 帮助菜单动作
    def on_help_about(self):
        """关于对话框"""
        self.logger.info("显示关于对话框")
        print("=" * 50)
        print("SceneWeaver - AIGC 实景导演系统")
        print("版本：1.0.0")
        print("开发者：SceneWeaver Team")
        print("=" * 50)
    
    def on_help_guide(self):
        """使用指南"""
        self.logger.info("显示使用指南")
    
    def on_help_check_update(self):
        """检查更新"""
        self.logger.info("检查更新")