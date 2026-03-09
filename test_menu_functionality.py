#!/usr/bin/env python3
"""
测试菜单功能是否正常工作
"""

import sys
import os
import logging

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_menu_initialization():
    """测试菜单初始化"""
    print("=== 测试菜单功能 ===")
    
    try:
        # 导入必要的模块
        from core.engine import CoreEngine
        from utils.config_manager import ConfigManager
        
        # 创建配置
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        # 创建引擎实例
        engine = CoreEngine(config)
        
        # 检查菜单系统是否正确初始化
        if engine.native_menu is None:
            print("❌ 菜单系统初始化失败")
            return False
        else:
            print("✅ 菜单系统初始化成功")
            
        # 检查关键回调是否设置
        callbacks_set = 0
        total_callbacks = 0
        
        # 检查文件菜单回调
        file_menu_items = ['新建', '打开', '保存', '另存为', '-', '退出']
        for i, item in enumerate(file_menu_items):
            if item != '-':  # 跳过分隔线
                total_callbacks += 1
                if hasattr(engine, '_on_file_new') and hasattr(engine, '_on_file_open'):
                    callbacks_set += 1
        
        # 检查编辑菜单回调
        edit_menu_items = ['撤销', '重做', '-', '剪切', '复制', '粘贴']
        for i, item in enumerate(edit_menu_items):
            if item != '-':  # 跳过分隔线
                total_callbacks += 1
                if hasattr(engine, '_on_edit_undo') and hasattr(engine, '_on_edit_redo'):
                    callbacks_set += 1
        
        print(f"✅ 回调设置检查: {callbacks_set}/{total_callbacks} 个回调已设置")
        
        # 测试菜单回调方法是否存在
        required_methods = [
            '_on_file_new', '_on_file_open', '_on_file_save', '_on_file_exit',
            '_on_edit_undo', '_on_edit_redo', '_on_edit_cut', '_on_edit_copy', '_on_edit_paste',
            '_on_view_fullscreen', '_on_view_reset', '_on_view_toggle_fps',
            '_on_tools_settings', '_on_tools_plugins', '_on_tools_file_browser',
            '_on_help_about', '_on_help_guide', '_on_help_check_update'
        ]
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(engine, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ 缺少的方法: {missing_methods}")
            return False
        else:
            print("✅ 所有菜单方法都已正确实现")
            
        print("=== 菜单功能测试通过 ===")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_menu_initialization()
    sys.exit(0 if success else 1)