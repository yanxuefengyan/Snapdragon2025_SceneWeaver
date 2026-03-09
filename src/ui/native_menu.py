"""
Native Menu - 原生 Pygame 菜单系统
使用原生 pygame 绘制中文菜单，避免 pygame_gui 兼容性问题
"""

import pygame
import logging
from typing import Dict, List, Callable, Optional, Tuple
from pathlib import Path


class NativeMenu:
    """原生菜单类"""
    
    # Windows 中文字体
    CHINESE_FONTS = [
        "simhei",      # 黑体
        "simsun",      # 宋体
        "msyh",        # 微软雅黑
        "simkai",      # 楷体
    ]
    
    def __init__(self, screen, position: Tuple[int, int], menu_items: List[str]):
        self.screen = screen
        self.position = position
        self.menu_items = menu_items
        self.logger = logging.getLogger(__name__)
        
        # 菜单样式
        self.bg_color = (30, 34, 39)  # 深色背景
        self.hover_color = (46, 50, 55)  # 悬停背景
        self.text_color = (255, 255, 255)  # 白色文字
        self.separator_color = (60, 60, 60)  # 分隔线颜色
        
        # 字体初始化
        self.font = self._load_chinese_font(16)
        
        # 菜单状态
        self.hovered_index = -1
        self.visible = True
        
        # 计算菜单尺寸
        self.item_height = 30
        self.separator_height = 10
        self.menu_width = 150
        self.menu_height = self._calculate_height()
        
        # 菜单矩形区域
        self.rect = pygame.Rect(
            position[0],
            position[1],
            self.menu_width,
            self.menu_height
        )
        
        # 回调函数
        self.callbacks: Dict[int, Callable] = {}
        
        self.logger.info(f"NativeMenu 初始化完成，项目数：{len(menu_items)}")
    
    def _load_chinese_font(self, size: int):
        """加载中文字体"""
        # 尝试加载系统字体
        for font_name in self.CHINESE_FONTS:
            try:
                font = pygame.font.SysFont(font_name, size)
                # 测试中文字符
                test_surface = font.render("测试", True, (255, 255, 255))
                return font
            except Exception as e:
                continue
        
        # 如果系统字体都失败，使用默认字体
        self.logger.warning("未找到中文字体，使用默认字体")
        return pygame.font.Font(None, size)
    
    def _calculate_height(self) -> int:
        """计算菜单总高度"""
        height = 0
        for item in self.menu_items:
            if item == '-':  # 分隔线
                height += self.separator_height
            else:
                height += self.item_height
        return height + 6  # 上下边距
    
    def _calculate_item_rects(self) -> List[pygame.Rect]:
        """计算每个菜单项的矩形区域"""
        rects = []
        y_offset = 3
        
        for item in self.menu_items:
            if item == '-':
                # 分隔线
                rect = pygame.Rect(
                    5,
                    self.position[1] + y_offset,
                    self.menu_width - 10,
                    1
                )
                y_offset += self.separator_height
            else:
                # 菜单项
                rect = pygame.Rect(
                    self.position[0],
                    self.position[1] + y_offset,
                    self.menu_width,
                    self.item_height
                )
                y_offset += self.item_height
            
            rects.append(rect)
        
        return rects
    
    def handle_event(self, event) -> Optional[int]:
        """处理事件，返回选中的菜单项索引"""
        if event.type == pygame.MOUSEMOTION:
            # 更新悬停状态
            mouse_pos = pygame.mouse.get_pos()
            item_rects = self._calculate_item_rects()
            
            self.hovered_index = -1
            for i, rect in enumerate(item_rects):
                if rect.collidepoint(mouse_pos) and self.menu_items[i] != '-':
                    self.hovered_index = i
                    break
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                mouse_pos = pygame.mouse.get_pos()
                item_rects = self._calculate_item_rects()
                
                for i, rect in enumerate(item_rects):
                    if rect.collidepoint(mouse_pos) and self.menu_items[i] != '-':
                        self.logger.info(f"菜单项点击：{self.menu_items[i]}")
                        if i in self.callbacks:
                            self.callbacks[i]()
                        return i
        
        return None
    
    def draw(self):
        """绘制菜单"""
        if not self.visible:
            return
        
        # 绘制菜单背景
        pygame.draw.rect(self.screen, self.bg_color, self.rect, border_radius=4)
        pygame.draw.rect(self.screen, (60, 60, 60), self.rect, 1, border_radius=4)
        
        # 绘制菜单项
        item_rects = self._calculate_item_rects()
        
        for i, (item, rect) in enumerate(zip(self.menu_items, item_rects)):
            if item == '-':
                # 绘制分隔线
                pygame.draw.line(
                    self.screen,
                    self.separator_color,
                    (rect.x, rect.y),
                    (rect.x + rect.width, rect.y)
                )
            else:
                # 绘制悬停背景
                if i == self.hovered_index:
                    hover_rect = pygame.Rect(
                        rect.x + 3,
                        rect.y,
                        rect.width - 6,
                        self.item_height
                    )
                    pygame.draw.rect(self.screen, self.hover_color, hover_rect, border_radius=3)
                
                # 绘制文本
                text_surface = self.font.render(item, True, self.text_color)
                text_rect = text_surface.get_rect(
                    x=rect.x + 10,
                    centery=rect.centery
                )
                self.screen.blit(text_surface, text_rect)
    
    def set_callback(self, index: int, callback: Callable):
        """设置菜单项回调"""
        self.callbacks[index] = callback
    
    def show(self):
        """显示菜单"""
        self.visible = True
    
    def hide(self):
        """隐藏菜单"""
        self.visible = False


class NativeMenuBar:
    """原生菜单栏类"""
    
    def __init__(self, screen, screen_size: Tuple[int, int]):
        self.screen = screen
        self.screen_width, self.screen_height = screen_size
        self.logger = logging.getLogger(__name__)
        
        # 菜单栏样式
        self.bg_color = (30, 34, 39)
        self.hover_color = (46, 50, 55)
        self.text_color = (255, 255, 255)
        
        # 字体
        self.font = self._load_chinese_font(16)
        
        # 菜单定义
        self.menus = {
            '文件': ['新建', '打开', '保存', '另存为', '-', '退出'],
            '编辑': ['撤销', '重做', '-', '剪切', '复制', '粘贴'],
            '视图': ['全屏', '重置视图', '-', '显示 FPS', '显示控制台'],
            '工具': ['设置', '插件管理', '-', '文件浏览器'],
            '帮助': ['关于', '使用指南', '-', '检查更新']
        }
        
        self.menu_names = list(self.menus.keys())
        
        # 计算位置和尺寸
        self.menu_height = 30
        self.menu_width = 80
        
        # 菜单栏矩形
        self.rect = pygame.Rect(0, 0, self.screen_width, self.menu_height)
        
        # 状态
        self.hovered_index = -1
        self.active_menu: Optional[NativeMenu] = None
        self.active_menu_index = -1
        
        # 回调
        self.callbacks: Dict[str, Dict[int, Callable]] = {}
        
        self.logger.info(f"NativeMenuBar 初始化完成")
    
    def _load_chinese_font(self, size: int):
        """加载中文字体"""
        for font_name in ['simhei', 'simsun', 'msyh']:
            try:
                font = pygame.font.SysFont(font_name, size)
                test_surface = font.render("测试", True, (255, 255, 255))
                return font
            except:
                continue
        
        return pygame.font.Font(None, size)
    
    def handle_event(self, event):
        """处理事件"""
        # 先处理活动菜单的事件
        if self.active_menu:
            result = self.active_menu.handle_event(event)
            if result is not None:
                # 菜单项被选中
                self._close_menu()
                return True  # 表示事件已处理
        
        # 检查是否点击了菜单栏
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                # 计算点击的菜单项
                x = mouse_pos[0]
                index = (x - 10) // (self.menu_width + 5)
                if 0 <= index < len(self.menu_names):
                    self._toggle_menu(index)
                    return True  # 表示事件已处理
        
        return False  # 表示事件未处理
    
    def _toggle_menu(self, index: int):
        """切换菜单显示"""
        if self.active_menu_index == index:
            self._close_menu()
        else:
            self._open_menu(index)
    
    def _open_menu(self, index: int):
        """打开菜单"""
        self.active_menu_index = index
        menu_name = self.menu_names[index]
        menu_items = self.menus[menu_name]
        
        # 计算菜单位置
        x = 10 + index * (self.menu_width + 5)
        y = self.menu_height
        
        # 创建菜单
        self.active_menu = NativeMenu(self.screen, (x, y), menu_items)
        
        # 设置已注册的回调
        if menu_name in self.callbacks:
            for item_index, callback in self.callbacks[menu_name].items():
                self.active_menu.set_callback(item_index, callback)
        
        self.logger.info(f"打开菜单：{menu_name}")
    
    def _close_menu(self):
        """关闭菜单"""
        self.active_menu = None
        self.active_menu_index = -1
    
    def set_callback(self, menu_name: str, item_index: int, callback: Callable):
        """设置菜单项回调"""
        if menu_name not in self.menus:
            self.logger.warning(f"尝试设置不存在的菜单回调: {menu_name}")
            return
            
        if item_index < 0 or item_index >= len(self.menus[menu_name]):
            self.logger.warning(f"无效的菜单项索引: {menu_name}[{item_index}]")
            return
            
        if self.menus[menu_name][item_index] == '-':
            self.logger.warning(f"不能为分隔线设置回调: {menu_name}[{item_index}]")
            return
            
        if menu_name not in self.callbacks:
            self.callbacks[menu_name] = {}
        self.callbacks[menu_name][item_index] = callback
        
        # 如果菜单已创建，立即更新回调
        if self.active_menu and self.menu_names[self.active_menu_index] == menu_name:
            self.active_menu.set_callback(item_index, callback)
    
    def draw(self):
        """绘制菜单栏"""
        # 绘制背景
        pygame.draw.rect(self.screen, self.bg_color, self.rect)
        pygame.draw.line(
            self.screen,
            (60, 60, 60),
            (0, self.menu_height - 1),
            (self.screen_width, self.menu_height - 1)
        )
        
        # 绘制菜单项
        for i, name in enumerate(self.menu_names):
            x = 10 + i * (self.menu_width + 5)
            
            # 绘制悬停效果
            if i == self.hovered_index or (self.active_menu and i == self.active_menu_index):
                hover_rect = pygame.Rect(x, 5, self.menu_width - 5, self.menu_height - 10)
                pygame.draw.rect(self.screen, self.hover_color, hover_rect, border_radius=3)
            
            # 绘制文本
            text_surface = self.font.render(name, True, self.text_color)
            text_rect = text_surface.get_rect(
                x=x + 10,
                centery=self.menu_height // 2
            )
            self.screen.blit(text_surface, text_rect)
        
        # 绘制活动菜单
        if self.active_menu:
            self.active_menu.draw()
    
    def update(self):
        """更新状态"""
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            x = mouse_pos[0]
            self.hovered_index = int((x - 10) // (self.menu_width + 5))
            if self.hovered_index < 0 or self.hovered_index >= len(self.menu_names):
                self.hovered_index = -1
        else:
            self.hovered_index = -1