"""
Font Manager - 字体管理器
处理中文字体加载和配置
"""

import pygame
import os
import logging
from pathlib import Path


class FontManager:
    """字体管理器"""
    
    # 常见中文字体路径（Windows）
    CHINESE_FONTS = [
        "C:/Windows/Fonts/simsun.ttc",      # 宋体
        "C:/Windows/Fonts/simhei.ttf",       # 黑体
        "C:/Windows/Fonts/msyh.ttc",         # 微软雅黑
        "C:/Windows/Fonts/simkai.ttf",       # 楷体
        "C:/Windows/Fonts/simfang.ttf",      # 仿宋
        "C:/Windows/Fonts/STSONG.TTF",       # 华文宋体
    ]
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.fonts = {}
        self.default_font = None
        self.chinese_font = None
        
        self._initialize_fonts()
    
    def _initialize_fonts(self):
        """初始化字体"""
        try:
            # 初始化 pygame 字体
            pygame.font.init()
            
            # 尝试加载默认字体
            self.default_font = pygame.font.Font(None, 24)
            self.logger.info("默认字体加载成功")
            
            # 查找并加载中文字体
            self.chinese_font = self._find_chinese_font()
            
            if self.chinese_font:
                self.logger.info(f"中文字体加载成功：{self.chinese_font}")
            else:
                self.logger.warning("未找到中文字体，将使用默认字体")
                self.chinese_font = self.default_font
                
        except Exception as e:
            self.logger.error(f"字体初始化失败：{e}")
            self.default_font = pygame.font.Font(None, 24)
            self.chinese_font = self.default_font
    
    def _find_chinese_font(self):
        """查找可用的中文字体"""
        for font_path in self.CHINESE_FONTS:
            if os.path.exists(font_path):
                try:
                    # 尝试加载字体
                    font = pygame.font.Font(font_path, 24)
                    # 测试中文字符
                    test_text = "中文"
                    font.render(test_text, True, (255, 255, 255))
                    return font_path
                except Exception as e:
                    self.logger.debug(f"字体加载失败 {font_path}: {e}")
                    continue
        
        # 如果指定的字体都不可用，尝试系统默认中文字体
        try:
            # 使用 pygame 的字体查找
            font_names = pygame.font.get_fonts()
            for name in ['simhei', 'simsun', 'msyh', 'microsoft yahei']:
                if name in font_names:
                    font_path = pygame.font.match_font(name)
                    if font_path:
                        return font_path
        except Exception as e:
            self.logger.debug(f"系统字体查找失败：{e}")
        
        return None
    
    def get_font(self, size=24, chinese=True):
        """获取指定大小的字体"""
        cache_key = f"{size}_{chinese}"
        
        if cache_key in self.fonts:
            return self.fonts[cache_key]
        
        try:
            if chinese and self.chinese_font:
                font = pygame.font.Font(self.chinese_font, size)
            else:
                font = pygame.font.Font(None, size)
            
            self.fonts[cache_key] = font
            return font
        except Exception as e:
            self.logger.error(f"获取字体失败：{e}")
            return self.default_font
    
    def render_text(self, text, font_size=24, color=(255, 255, 255), 
                   bg_color=None, chinese=True):
        """渲染文本"""
        try:
            font = self.get_font(font_size, chinese)
            
            if bg_color:
                return font.render(text, True, color, bg_color)
            else:
                return font.render(text, True, color)
        except Exception as e:
            self.logger.error(f"文本渲染失败：{e}")
            # 返回一个错误文本表面
            surface = pygame.Surface((100, 20))
            surface.fill((255, 0, 0))
            return surface
    
    def get_font_path(self):
        """获取中文字体路径"""
        return self.chinese_font if self.chinese_font else None


# 全局字体管理器实例
_font_manager = None


def get_font_manager():
    """获取全局字体管理器"""
    global _font_manager
    if _font_manager is None:
        _font_manager = FontManager()
    return _font_manager


def render_chinese_text(text, size=24, color=(255, 255, 255)):
    """便捷函数：渲染中文文本"""
    manager = get_font_manager()
    return manager.render_text(text, size, color)