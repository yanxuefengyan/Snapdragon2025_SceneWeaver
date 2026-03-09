#!/usr/bin/env python3
"""
Menu Demo - 菜单系统演示
展示 SceneWeaver 的完整菜单功能
"""

import sys
import os
import logging
from pathlib import Path

# 添加 src目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from utils.logger import setup_logger


def demo_menu_structure():
    """演示菜单结构"""
    print("=" * 60)
    print("🎨 SceneWeaver 菜单系统结构")
    print("=" * 60)
    
    menu_structure = {
        '文件': ['新建', '打开', '保存', '另存为', '-', '退出'],
        '编辑': ['撤销', '重做', '-', '剪切', '复制', '粘贴'],
        '视图': ['全屏', '重置视图', '-', '显示 FPS', '显示控制台'],
        '工具': ['设置', '插件管理', '-', '文件浏览器'],
        '帮助': ['关于', '使用指南', '-', '检查更新']
    }
    
    for menu_name, items in menu_structure.items():
        print(f"\n📁 {menu_name} 菜单:")
        for item in items:
            if item == '-':
                print("   ──────────────")
            else:
                print(f"   • {item}")
    
    print("\n" + "=" * 60)


def demo_menu_features():
    """演示菜单功能特性"""
    print("\n✨ 菜单系统主要特性:")
    print("-" * 60)
    
    features = [
        ("菜单栏", "顶部水平菜单栏，包含所有主要功能分类"),
        ("下拉菜单", "点击菜单项弹出下拉子菜单"),
        ("快捷键支持", "常用功能支持键盘快捷键"),
        ("分隔线", "相关功能分组显示"),
        ("图标支持", "可为菜单项添加图标"),
        ("状态指示", "当前状态通过勾选标记显示"),
        ("禁用/启用", "可根据上下文动态控制菜单可用性"),
        ("自定义回调", "每个菜单项可绑定自定义处理函数")
    ]
    
    for feature, description in features:
        print(f"  ✓ {feature:15} - {description}")


def demo_menu_actions():
    """演示菜单动作"""
    print("\n🎯 主要菜单动作说明:")
    print("-" * 60)
    
    actions = {
        '文件 > 新建': '创建新项目或场景',
        '文件 > 打开': '打开现有项目或媒体文件',
        '文件 > 保存': '保存当前项目',
        '文件 > 退出': '退出应用程序',
        
        '编辑 > 撤销/重做': '撤销或重做上一步操作',
        '编辑 > 复制/粘贴': '复制和粘贴选中的内容',
        
        '视图 > 全屏': '切换全屏/窗口模式',
        '视图 > 显示 FPS': '显示或隐藏 FPS 计数器',
        
        '工具 > 设置': '打开应用程序设置',
        '工具 > 文件浏览器': '打开文件浏览器选择文件',
        
        '帮助 > 关于': '显示应用程序信息',
        '帮助 > 使用指南': '打开用户手册和使用说明'
    }
    
    for action, description in actions.items():
        print(f"  📌 {action:20} → {description}")


def demo_keyboard_shortcuts():
    """演示键盘快捷键"""
    print("\n⌨️  推荐键盘快捷键:")
    print("-" * 60)
    
    shortcuts = {
        'Ctrl + N': '新建项目',
        'Ctrl + O': '打开文件',
        'Ctrl + S': '保存项目',
        'Ctrl + Q': '退出程序',
        'Ctrl + Z': '撤销',
        'Ctrl + Y': '重做',
        'Ctrl + C': '复制',
        'Ctrl + V': '粘贴',
        'F11': '切换全屏',
        'F1': '显示帮助'
    }
    
    for shortcut, action in shortcuts.items():
        print(f"  ⌨️  {shortcut:12} → {action}")


def demo_integration_guide():
    """演示集成指南"""
    print("\n🔧 菜单系统集成指南:")
    print("-" * 60)
    
    print("""
1. 导入菜单系统:
   from ui.menu_system import MenuSystem, MenuActions

2. 初始化菜单:
   menu_system = MenuSystem(screen_size)
   menu_system.initialize(gui_manager)

3. 设置菜单回调:
   menu_actions = MenuActions(engine, gui_system)
   menu_system.set_callback('文件', '打开', menu_actions.on_file_open)

4. 在主循环中处理菜单事件:
   for event in pygame.event.get():
       menu_system.process_events(event)
""")


def main():
    """主函数"""
    print("\n🚀 SceneWeaver 菜单系统演示\n")
    
    # 设置日志
    setup_logger({'console_output': True}, logging.INFO)
    
    try:
        # 演示各个部分
        demo_menu_structure()
        demo_menu_features()
        demo_menu_actions()
        demo_keyboard_shortcuts()
        demo_integration_guide()
        
        print("\n" + "=" * 60)
        print("✅ 菜单系统演示完成!")
        print("=" * 60)
        
        print("\n💡 提示:")
        print("  - 菜单系统已集成到主程序中")
        print("  - 运行 'python src/main.py' 启动完整应用")
        print("  - 按 F1 键可查看关于对话框")
        print("  - 文件菜单支持打开和保存项目")
        print("  - 工具菜单可访问文件浏览器功能")
        
    except KeyboardInterrupt:
        print("\n\n👋 用户中断演示")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()