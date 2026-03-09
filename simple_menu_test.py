#!/usr/bin/env python3
"""
简化版菜单功能测试
"""

import sys
import os
import logging

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_functionality():
    """测试基本功能"""
    print("=== 简单菜单功能测试 ===")
    
    try:
        # 导入必要的模块
        from ui.native_menu import NativeMenuBar
        import pygame
        
        # 初始化pygame
        pygame.init()
        
        # 创建一个简单的屏幕
        screen = pygame.display.set_mode((800, 600))
        
        # 创建菜单栏
        menu_bar = NativeMenuBar(screen, (800, 600))
        
        if menu_bar is None:
            print("❌ 菜单栏创建失败")
            return False
        else:
            print("✅ 菜单栏创建成功")
            
        # 检查菜单项是否存在
        expected_menus = ['文件', '编辑', '视图', '工具', '帮助']
        for menu_name in expected_menus:
            if menu_name in menu_bar.menus:
                print(f"✅ 菜单 '{menu_name}' 存在")
            else:
                print(f"❌ 菜单 '{menu_name}' 不存在")
                return False
        
        print("=== 基本功能测试通过 ===")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            pygame.quit()
        except:
            pass

if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)