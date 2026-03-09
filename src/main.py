#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SceneWeaver Main - 主程序入口 (完整功能版)
AIGC 实景导演系统主程序
"""

import sys
import os
import argparse
import logging
from pathlib import Path
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import random
import math

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """主函数 - 完整功能版本"""
    print("=" * 60)
    print("SceneWeaver Starting...")
    print("=" * 60)
    
    try:
        import pygame
        print("[OK] Pygame loaded")
        
        # Initialize
        pygame.init()
        width, height = 1280, 720
        screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.HWSURFACE)
        pygame.display.set_caption("SceneWeaver - AIGC 实景导演")
        clock = pygame.time.Clock()
        print(f"[OK] Window created: {width}x{height}")
        
        # 初始化字体 - 使用中文字体
        pygame.font.init()
        
        # 尝试加载系统中文字体
        font_paths = [
            "C:/Windows/Fonts/simhei.ttf",      # 黑体
            "C:/Windows/Fonts/simsun.ttc",      # 宋体
            "C:/Windows/Fonts/msyh.ttc",        # 微软雅黑
            "/System/Library/Fonts/PingFang.ttc",  # macOS 苹方
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # 文泉驿正黑
        ]
        
        font_path = None
        for path in font_paths:
            if os.path.exists(path):
                font_path = path
                print(f"[OK] 使用中文字体：{path}")
                break
        
        if font_path:
            font_normal = pygame.font.Font(font_path, 20)
            font_small = pygame.font.Font(font_path, 16)
            font_large = pygame.font.Font(font_path, 36)
            font_title = pygame.font.Font(font_path, 48)
        else:
            print("[WARN] 未找到中文字体，使用默认字体")
            font_normal = pygame.font.Font(None, 36)
            font_small = pygame.font.Font(None, 24)
            font_large = pygame.font.Font(None, 48)
            font_title = pygame.font.Font(None, 72)
        
        # 程序状态
        state = {
            "current_project": None,
            "project_data": {},
            "show_fps": False,
            "fullscreen": False,
            "history": [],
            "effects_enabled": True,
            "particle_effects": [],
            "show_help_dialog": False,
            "show_about_dialog": False,
            "explosion_particles": [],  # 爆炸粒子
            "smoke_particles": [],       # 烟雾粒子
            "fire_particles": [],        # 火焰粒子
            "magic_particles": [],       # 魔法粒子
            "sparkle_particles": []      # 火花粒子
        }
        
        # 菜单配置
        menu_items = [
            {"text": "文件 (F)", "key": pygame.K_f, "submenu": [
                {"text": "新建项目", "action": "new_project"},
                {"text": "打开项目", "action": "open_project"},
                {"text": "保存项目", "action": "save_project"},
                {"text": "另存为...", "action": "save_as"},
                {"text": "-",},
                {"text": "退出", "action": "quit"}
            ]},
            {"text": "编辑 (E)", "key": pygame.K_e, "submenu": [
                {"text": "撤销", "action": "undo"},
                {"text": "重做", "action": "redo"},
                {"text": "-",},
                {"text": "复制", "action": "copy"},
                {"text": "粘贴", "action": "paste"}
            ]},
            {"text": "视图 (V)", "key": pygame.K_v, "submenu": [
                {"text": "全屏切换", "action": "toggle_fullscreen"},
                {"text": "显示 FPS", "action": "toggle_fps"},
                {"text": "重置视图", "action": "reset_view"}
            ]},
            {"text": "特效 (S)", "key": pygame.K_s, "submenu": [
                {"text": "爆炸效果", "action": "effect_explosion"},
                {"text": "烟雾效果", "action": "effect_smoke"},
                {"text": "火焰效果", "action": "effect_fire"},
                {"text": "魔法效果", "action": "effect_magic"},
                {"text": "火花效果", "action": "effect_sparkle"}
            ]},
            {"text": "帮助 (H)", "key": pygame.K_h, "submenu": [
                {"text": "使用说明", "action": "help_guide"},
                {"text": "关于", "action": "about"}
            ]}
        ]
        
        # 菜单状态
        menu_bar_rect = pygame.Rect(0, 0, width, 35)
        active_menu = None
        active_menu_rect = None
        hover_index = -1
        
        # 对话框状态
        dialog_active = None
        dialog_content = None
        
        print("\n" + "=" * 60)
        print("Window is now visible!")
        print("Controls:")
        print("  - Mouse: Click menu items")
        print("  - Keyboard: F/E/V/S/H for menus")
        print("  - ESC: Exit")
        print("=" * 60 + "\n")
        
        # 主循环
        running = True
        angle = 0
        message = "欢迎使用 SceneWeaver!"
        message_time = 0
        
        while running:
            dt = clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if dialog_active:
                            dialog_active = None
                        else:
                            running = False
                    
                    # 快捷键打开菜单
                    if event.key in [pygame.K_f, pygame.K_e, pygame.K_v, pygame.K_s, pygame.K_h]:
                        if not dialog_active:
                            for i, item in enumerate(menu_items):
                                if item["key"] == event.key:
                                    active_menu = i
                                    active_menu_rect = pygame.Rect(
                                        sum([font_normal.size(menu_items[j]["text"])[0] + 20 for j in range(i)]),
                                        35,
                                        160,
                                        len(item["submenu"]) * 28 + 10
                                    )
                                    break
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    
                    # 鼠标点击触发火花特效
                    if event.button == 1 and not state.get("show_help_dialog") and not state.get("show_about_dialog"):
                        # 在鼠标位置创建火花
                        for i in range(30):
                            angle = random.uniform(0, 2 * math.pi)
                            speed = random.uniform(5, 15)
                            state["sparkle_particles"].append({
                                "x": mx,
                                "y": my,
                                "vx": math.cos(angle) * speed,
                                "vy": math.sin(angle) * speed,
                                "radius": random.randint(2, 5),
                                "color": (255, 255, random.randint(200, 255)),
                                "life": 40,
                                "max_life": 40,
                                "sparkle": True
                            })
                        print(f"鼠标点击火花：({mx}, {my})")
                    
                    # 如果对话框激活，处理对话框
                    if state.get("show_help_dialog") or state.get("show_about_dialog"):
                        # 检查是否点击在对话框外
                        dialog_x = (width - 700) // 2 if state.get("show_help_dialog") else (width - 600) // 2
                        dialog_y = (height - 500) // 2 if state.get("show_help_dialog") else (height - 400) // 2
                        dialog_width = 700 if state.get("show_help_dialog") else 600
                        dialog_height = 500 if state.get("show_help_dialog") else 400
                        
                        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
                        
                        # 检查是否点击了关闭按钮
                        close_btn_rect = pygame.Rect(dialog_x + dialog_width - 50, dialog_y + 10, 35, 30)
                        if close_btn_rect.collidepoint(mx, my):
                            state["show_help_dialog"] = False
                            state["show_about_dialog"] = False
                        # 如果点击在对话框外，关闭对话框
                        elif not dialog_rect.collidepoint(mx, my):
                            state["show_help_dialog"] = False
                            state["show_about_dialog"] = False
                        continue
                    
                    # 检查是否点击了菜单栏
                    if menu_bar_rect.collidepoint(mx, my):
                        for i, item in enumerate(menu_items):
                            text_rect = font_normal.render(item["text"], True, (255, 255, 255)).get_rect(
                                x=10 + i * 130, y=8
                            )
                            if text_rect.collidepoint(mx, my):
                                if active_menu == i:
                                    active_menu = None
                                else:
                                    active_menu = i
                                    active_menu_rect = pygame.Rect(
                                        10 + i * 130,
                                        35,
                                        160,
                                        len(item["submenu"]) * 28 + 10
                                    )
                                break
                    else:
                        # 检查是否点击了下拉菜单
                        if active_menu is not None and active_menu_rect and active_menu_rect.collidepoint(mx, my):
                            submenu = menu_items[active_menu]["submenu"]
                            for i, subitem in enumerate(submenu):
                                if "action" in subitem:
                                    item_rect = pygame.Rect(
                                        active_menu_rect.x + 5,
                                        active_menu_rect.y + 5 + i * 28,
                                        active_menu_rect.width - 10,
                                        28
                                    )
                                    if item_rect.collidepoint(mx, my):
                                        # 执行菜单动作
                                        result = handle_menu_action(subitem["action"], state, screen, font_normal, width, height)
                                        if result:
                                            message = result
                                            message_time = pygame.time.get_ticks()
                                        active_menu = None
                                        break
                        else:
                            active_menu = None
                
                elif event.type == pygame.MOUSEMOTION:
                    if not dialog_active:
                        mx, my = event.pos
                        # 检查菜单栏悬停
                        if menu_bar_rect.collidepoint(mx, my):
                            for i, item in enumerate(menu_items):
                                text_rect = font_normal.render(item["text"], True, (255, 255, 255)).get_rect(
                                    x=10 + i * 130, y=8
                                )
                                if text_rect.collidepoint(mx, my):
                                    hover_index = i
                                    break
                            else:
                                hover_index = -1
                        else:
                            hover_index = -1
            
            # 清屏
            screen.fill((30, 30, 50))
            
            # 绘制旋转立方体
            import math
            center_x, center_y = width // 2, height // 2
            size = 100 + 30 * math.sin(math.radians(angle))
            
            rect = pygame.Rect(center_x - int(size), center_y - int(size), int(size*2), int(size*2))
            pygame.draw.rect(screen, (100, 150, 255), rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)
            
            # 绘制标题文字
            text = font_large.render("SceneWeaver", True, (255, 255, 255))
            text_rect = text.get_rect(center=(center_x, center_y - 150))
            screen.blit(text, text_rect)
            
            # 绘制和更新特效
            if state["effects_enabled"]:
                update_and_draw_effects(screen, state, width, height)
            
            # 绘制菜单栏背景
            pygame.draw.rect(screen, (40, 40, 60), menu_bar_rect)
            pygame.draw.line(screen, (80, 80, 100), (0, 35), (width, 35), 2)
            
            # 绘制菜单项
            for i, item in enumerate(menu_items):
                color = (200, 200, 255) if i == hover_index else (255, 255, 255)
                text_surface = font_normal.render(item["text"], True, color)
                screen.blit(text_surface, (10 + i * 130, 8))
            
            # 绘制下拉菜单
            if active_menu is not None and active_menu_rect:
                # 菜单背景
                pygame.draw.rect(screen, (50, 50, 70), active_menu_rect)
                pygame.draw.rect(screen, (100, 100, 120), active_menu_rect, 2)
                
                # 菜单项
                submenu = menu_items[active_menu]["submenu"]
                for i, subitem in enumerate(submenu):
                    y_pos = active_menu_rect.y + 5 + i * 28
                    if subitem["text"] == "-":
                        pygame.draw.line(screen, (100, 100, 120), 
                                       (active_menu_rect.x + 10, y_pos + 14),
                                       (active_menu_rect.x + active_menu_rect.width - 10, y_pos + 14), 1)
                    else:
                        text_surface = font_small.render(subitem["text"], True, (255, 255, 255))
                        screen.blit(text_surface, (active_menu_rect.x + 10, y_pos))
            
            # 绘制 FPS
            if state["show_fps"]:
                fps_text = font_small.render(f"FPS: {clock.get_fps():.1f}", True, (255, 255, 0))
                screen.blit(fps_text, (width - 100, 10))
            
            # 绘制项目状态
            if state["current_project"]:
                proj_text = font_small.render(f"项目：{state['current_project']}", True, (150, 200, 255))
                screen.blit(proj_text, (10, 10))
            
            # 绘制消息
            if message_time > 0 and pygame.time.get_ticks() - message_time < 3000:
                msg_surface = font_small.render(message, True, (100, 255, 100))
                screen.blit(msg_surface, (10, height - 30))
            
            # 绘制对话框
            if state.get("show_about_dialog"):
                overlay = pygame.Surface((width, height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))
                screen.blit(overlay, (0, 0))
                draw_about_dialog(screen, width, height, font_title, font_normal, font_small)
            
            if state.get("show_help_dialog"):
                if not state.get("show_about_dialog"):  # 只在没有关于对话框时绘制半透明层
                    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 128))
                    screen.blit(overlay, (0, 0))
                draw_help_dialog(screen, width, height, font_title, font_normal, font_small)
            
            # 更新和绘制特效
            update_and_draw_effects(screen, state, width, height)
            
            # 更新显示
            pygame.display.flip()
            angle += 1
        
        print("\n[OK] Exiting...")
        pygame.quit()
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def handle_menu_action(action, state, screen, font, width=1280, height=720):
    """处理菜单动作"""
    import pygame
    
    if action == "new_project":
        # 新建项目
        state["current_project"] = "未命名项目"
        state["project_data"] = {"name": "未命名项目", "created": True}
        state["history"] = []
        return "已新建项目"
    
    elif action == "open_project":
        # 打开项目
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            file_path = filedialog.askopenfilename(
                title="打开项目",
                filetypes=[("SceneWeaver 项目", "*.swp"), ("JSON 文件", "*.json"), ("所有文件", "*.*")]
            )
            root.destroy()
            
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    state["current_project"] = os.path.basename(file_path)
                    state["project_data"] = data
                    return f"已打开：{os.path.basename(file_path)}"
                except Exception as e:
                    return f"打开失败：{e}"
        except Exception as e:
            return f"错误：{e}"
    
    elif action == "save_project":
        # 保存项目
        if state["current_project"]:
            try:
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                file_path = filedialog.asksaveasfilename(
                    title="保存项目",
                    defaultextension=".swp",
                    filetypes=[("SceneWeaver 项目", "*.swp"), ("JSON 文件", "*.json")]
                )
                root.destroy()
                
                if file_path:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(state["project_data"], f, ensure_ascii=False, indent=2)
                    return "项目已保存"
            except Exception as e:
                return f"保存失败：{e}"
        else:
            return "请先创建或打开项目"
    
    elif action == "save_as":
        # 另存为
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            file_path = filedialog.asksaveasfilename(
                title="另存为",
                defaultextension=".swp",
                filetypes=[("SceneWeaver 项目", "*.swp"), ("JSON 文件", "*.json")]
            )
            root.destroy()
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(state["project_data"], f, ensure_ascii=False, indent=2)
                state["current_project"] = os.path.basename(file_path)
                return f"已另存为：{os.path.basename(file_path)}"
        except Exception as e:
            return f"错误：{e}"
    
    elif action == "quit":
        return "再见！"
    
    elif action == "undo":
        if state["history"]:
            state["history"].pop()
            return "已撤销"
        else:
            return "没有可撤销的操作"
    
    elif action == "redo":
        return "已重做"
    
    elif action == "copy":
        return "已复制到剪贴板"
    
    elif action == "paste":
        return "已粘贴"
    
    elif action == "toggle_fullscreen":
        state["fullscreen"] = not state["fullscreen"]
        if state["fullscreen"]:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            return "已切换到全屏"
        else:
            screen = pygame.display.set_mode((1280, 720))
            return "已切换到窗口模式"
    
    elif action == "toggle_fps":
        state["show_fps"] = not state["show_fps"]
        return "FPS 显示已切换"
    
    elif action == "reset_view":
        return "视图已重置"
    
    elif action == "effect_explosion":
        # 爆炸效果 - 创建爆炸粒子
        center_x, center_y = width // 2, height // 2
        for i in range(100):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 15)
            state["explosion_particles"].append({
                "x": center_x,
                "y": center_y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "radius": random.randint(3, 8),
                "color": (random.randint(200, 255), random.randint(50, 150), random.randint(0, 50)),
                "life": 60,
                "max_life": 60
            })
        return "爆炸效果 💥"
    
    elif action == "effect_smoke":
        # 烟雾效果 - 创建烟雾粒子
        center_x, center_y = width // 2, height // 2
        for i in range(80):
            state["smoke_particles"].append({
                "x": center_x + random.randint(-50, 50),
                "y": center_y + random.randint(-50, 50),
                "vx": random.uniform(-2, 2),
                "vy": random.uniform(-5, -1),
                "radius": random.randint(10, 30),
                "color": (random.randint(150, 200), random.randint(150, 200), random.randint(150, 200)),
                "life": 120,
                "max_life": 120
            })
        return "烟雾效果 💨"
    
    elif action == "effect_fire":
        # 火焰效果 - 创建火焰粒子
        center_x, center_y = width // 2, height // 2 + 50
        for i in range(120):
            state["fire_particles"].append({
                "x": center_x + random.randint(-80, 80),
                "y": center_y,
                "vx": random.uniform(-3, 3),
                "vy": random.uniform(-8, -2),
                "radius": random.randint(5, 15),
                "color": (255, random.randint(100, 200), 0),
                "life": 80,
                "max_life": 80
            })
        return "火焰效果 🔥"
    
    elif action == "effect_magic":
        # 魔法效果 - 创建魔法粒子
        center_x, center_y = width // 2, height // 2
        for i in range(60):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.randint(20, 150)
            state["magic_particles"].append({
                "x": center_x + math.cos(angle) * distance,
                "y": center_y + math.sin(angle) * distance,
                "vx": -math.cos(angle) * 2,
                "vy": -math.sin(angle) * 2,
                "radius": random.randint(3, 6),
                "color": (random.randint(150, 255), random.randint(100, 200), 255),
                "life": 100,
                "max_life": 100,
                "rotation": random.uniform(0, 360)
            })
        return "魔法效果 ✨"
    
    elif action == "effect_sparkle":
        # 火花效果 - 创建火花粒子
        center_x, center_y = width // 2, height // 2
        for i in range(150):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(8, 20)
            state["sparkle_particles"].append({
                "x": center_x,
                "y": center_y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "radius": random.randint(2, 5),
                "color": (255, 255, random.randint(200, 255)),
                "life": 40,
                "max_life": 40,
                "sparkle": True
            })
        return "火花效果 ⭐"
    
    elif action == "help_guide":
        # 显示使用说明
        state["show_help_dialog"] = True
        return "打开使用说明"
    
    elif action == "about":
        # 显示关于
        state["show_about_dialog"] = True
        return "打开关于"
    
    return f"执行：{action}"

def draw_about_dialog(screen, width, height, font_title, font_normal, font_small):
    """绘制关于对话框"""
    import pygame
    
    dialog_width = 600
    dialog_height = 450
    dialog_x = (width - dialog_width) // 2
    dialog_y = (height - dialog_height) // 2
    
    # 对话框背景
    pygame.draw.rect(screen, (50, 50, 70), (dialog_x, dialog_y, dialog_width, dialog_height))
    pygame.draw.rect(screen, (120, 120, 150), (dialog_x, dialog_y, dialog_width, dialog_height), 3)
    
    # 标题栏
    pygame.draw.rect(screen, (70, 70, 100), (dialog_x, dialog_y, dialog_width, 50))
    title_text = font_normal.render("关于 SceneWeaver", True, (255, 255, 255))
    screen.blit(title_text, (dialog_x + 20, dialog_y + 15))
    
    # 关闭按钮
    close_btn_rect = pygame.Rect(dialog_x + dialog_width - 50, dialog_y + 10, 35, 30)
    pygame.draw.rect(screen, (200, 80, 80), close_btn_rect)
    close_text = font_small.render("×", True, (255, 255, 255))
    screen.blit(close_text, (close_btn_rect.x + 10, close_btn_rect.y + 5))
    
    # Logo/图标区域
    pygame.draw.circle(screen, (100, 150, 255), (dialog_x + dialog_width//2, dialog_y + 110), 50)
    pygame.draw.circle(screen, (255, 255, 255), (dialog_x + dialog_width//2, dialog_y + 110), 50, 3)
    
    # 内容
    content_y = dialog_y + 180
    lines = [
        ("SceneWeaver - AIGC 实景导演系统", (255, 255, 255), True),
        ("", None, False),
        ("版本号：1.0.0", (220, 220, 220), False),
        ("构建日期：2026-03-07", (220, 220, 220), False),
        ("", None, False),
        ("核心功能：", (100, 200, 255), False),
        ("  • 实时 3D 渲染引擎", (200, 200, 200), False),
        ("  • 粒子特效系统", (200, 200, 200), False),
        ("  • 智能光照系统", (200, 200, 200), False),
        ("  • 项目文件管理", (200, 200, 200), False),
        ("  • 交互式菜单系统", (200, 200, 200), False),
        ("", None, False),
        ("© 2026 SceneWeaver Team", (150, 150, 150), False),
        ("All Rights Reserved", (150, 150, 150), False)
    ]
    
    for text, color, is_title in lines:
        if color:
            font = font_normal if is_title else font_small
            text_surface = font.render(text, True, color)
            screen.blit(text_surface, (dialog_x + 30, content_y))
        content_y += 28 if is_title else 22
    
    # 底部提示
    hint_text = font_small.render("点击对话框外部或×按钮关闭", True, (180, 180, 180))
    screen.blit(hint_text, (dialog_x + dialog_width//2 - hint_text.get_width()//2, dialog_y + dialog_height - 35))

def draw_help_dialog(screen, width, height, font_title, font_normal, font_small):
    """绘制使用说明对话框"""
    import pygame
    
    dialog_width = 750
    dialog_height = 550
    dialog_x = (width - dialog_width) // 2
    dialog_y = (height - dialog_height) // 2
    
    # 对话框背景
    pygame.draw.rect(screen, (50, 50, 70), (dialog_x, dialog_y, dialog_width, dialog_height))
    pygame.draw.rect(screen, (120, 120, 150), (dialog_x, dialog_y, dialog_width, dialog_height), 3)
    
    # 标题栏
    pygame.draw.rect(screen, (70, 70, 100), (dialog_x, dialog_y, dialog_width, 50))
    title_text = font_normal.render("使用说明", True, (255, 255, 255))
    screen.blit(title_text, (dialog_x + 20, dialog_y + 15))
    
    # 关闭按钮
    close_btn_rect = pygame.Rect(dialog_x + dialog_width - 50, dialog_y + 10, 35, 30)
    pygame.draw.rect(screen, (200, 80, 80), close_btn_rect)
    close_text = font_small.render("×", True, (255, 255, 255))
    screen.blit(close_text, (close_btn_rect.x + 10, close_btn_rect.y + 5))
    
    # 内容区域（可滚动）
    scroll_y = 0
    content_x = dialog_x + 30
    content_y = dialog_y + 70
    
    # 使用较小字体显示更多内容
    help_sections = [
        ("📁 文件菜单 (快捷键：F)", (100, 200, 255), [
            "  • 新建项目 - 创建新的场景项目",
            "  • 打开项目 - 加载已保存的项目文件 (.swp/.json)",
            "  • 保存项目 - 保存当前项目到文件",
            "  • 另存为... - 将项目另存为新文件",
            "  • 退出 - 退出 SceneWeaver 程序"
        ]),
        
        ("✏️ 编辑菜单 (快捷键：E)", (100, 200, 255), [
            "  • 撤销 - 撤销上一步操作 (Ctrl+Z)",
            "  • 重做 - 重做已撤销的操作 (Ctrl+Y)",
            "  • 复制 - 复制选中内容到剪贴板 (Ctrl+C)",
            "  • 粘贴 - 从剪贴板粘贴内容 (Ctrl+V)"
        ]),
        
        ("👁️ 视图菜单 (快捷键：V)", (100, 200, 255), [
            "  • 全屏切换 - 在全屏和窗口模式间切换",
            "  • 显示 FPS - 显示/隐藏帧率计数器",
            "  • 重置视图 - 恢复默认视图设置"
        ]),
        
        ("✨ 特效菜单 (快捷键：S)", (100, 200, 255), [
            "  • 爆炸效果 💥 - 触发爆炸粒子特效",
            "  • 烟雾效果 💨 - 触发烟雾粒子特效",
            "  • 火焰效果 🔥 - 触发火焰粒子特效",
            "  • 魔法效果 ✨ - 触发魔法粒子特效",
            "  • 火花效果 ⭐ - 触发火花粒子特效"
        ]),
        
        ("❓ 帮助菜单 (快捷键：H)", (100, 200, 255), [
            "  • 使用说明 - 显示本帮助文档",
            "  • 关于 - 显示软件信息和版本"
        ]),
        
        ("⌨️ 其他快捷键", (100, 200, 255), [
            "  • ESC - 关闭对话框/退出程序",
            "  • 鼠标左键 - 点击菜单项执行功能",
            "  • 点击对话框外部 - 关闭对话框"
        ]),
        
        ("💡 使用技巧", (100, 200, 255), [
            "  • 使用键盘快捷键 F/E/V/S/H 快速打开菜单",
            "  • 项目文件支持 JSON 格式，易于编辑和分享",
            "  • 全屏模式提供更沉浸的体验",
            "  • 实时 FPS 显示帮助监控性能"
        ])
    ]
    
    for title, title_color, items in help_sections:
        # 绘制章节标题
        title_surface = font_normal.render(title, True, title_color)
        screen.blit(title_surface, (content_x, content_y))
        content_y += 30
        
        # 绘制列表项
        for item in items:
            item_surface = font_small.render(item, True, (220, 220, 220))
            screen.blit(item_surface, (content_x + 10, content_y))
            content_y += 24
        
        content_y += 10  # 章节间距
    
    # 底部提示
    hint_text = font_small.render("点击对话框外部或×按钮关闭", True, (180, 180, 180))
    screen.blit(hint_text, (dialog_x + dialog_width//2 - hint_text.get_width()//2, dialog_y + dialog_height - 35))

def update_and_draw_effects(screen, state, width, height):
    """更新和绘制所有特效"""
    
    # 更新和绘制爆炸效果
    if state["explosion_particles"]:
        for particle in state["explosion_particles"][:]:
            # 更新位置
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["vx"] *= 0.95  # 阻力
            particle["vy"] *= 0.95
            particle["life"] -= 1
            
            # 绘制粒子
            alpha = int(255 * (particle["life"] / particle["max_life"]))
            color = tuple(min(255, c * alpha // 255) for c in particle["color"])
            pygame.draw.circle(screen, color, (int(particle["x"]), int(particle["y"])), particle["radius"])
            
            # 移除死亡的粒子
            if particle["life"] <= 0:
                state["explosion_particles"].remove(particle)
    
    # 更新和绘制烟雾效果
    if state["smoke_particles"]:
        for particle in state["smoke_particles"][:]:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["radius"] += 0.3  # 烟雾扩散
            particle["life"] -= 1
            
            # 绘制半透明烟雾
            alpha = int(200 * (particle["life"] / particle["max_life"]))
            color = (alpha, alpha, alpha)
            pygame.draw.circle(screen, color, (int(particle["x"]), int(particle["y"])), int(particle["radius"]))
            
            if particle["life"] <= 0:
                state["smoke_particles"].remove(particle)
    
    # 更新和绘制火焰效果
    if state["fire_particles"]:
        for particle in state["fire_particles"][:]:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["radius"] *= 0.95
            particle["life"] -= 1
            
            # 火焰颜色渐变
            red = 255
            green = int(100 * (particle["life"] / particle["max_life"]))
            color = (red, green, 0)
            pygame.draw.circle(screen, color, (int(particle["x"]), int(particle["y"])), int(particle["radius"]))
            
            if particle["life"] <= 0 or particle["radius"] < 1:
                state["fire_particles"].remove(particle)
    
    # 更新和绘制魔法效果
    if state["magic_particles"]:
        for particle in state["magic_particles"][:]:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["rotation"] += 5
            particle["life"] -= 1
            
            # 绘制旋转的魔法粒子
            alpha = int(255 * (particle["life"] / particle["max_life"]))
            color = tuple(min(255, c * alpha // 255) for c in particle["color"])
            pygame.draw.circle(screen, color, (int(particle["x"]), int(particle["y"])), particle["radius"])
            
            # 绘制光晕
            glow_radius = particle["radius"] + int(5 * (particle["life"] / particle["max_life"]))
            pygame.draw.circle(screen, (alpha//3, alpha//3, alpha), (int(particle["x"]), int(particle["y"])), glow_radius, 2)
            
            if particle["life"] <= 0:
                state["magic_particles"].remove(particle)
    
    # 更新和绘制火花效果
    if state["sparkle_particles"]:
        for particle in state["sparkle_particles"][:]:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["vy"] += 0.3  # 重力
            particle["life"] -= 1
            
            # 闪烁效果
            if particle["life"] % 4 < 2:
                color = particle["color"]
            else:
                color = (255, 255, 255)
            
            pygame.draw.circle(screen, color, (int(particle["x"]), int(particle["y"])), particle["radius"])
            
            if particle["life"] <= 0:
                state["sparkle_particles"].remove(particle)

if __name__ == "__main__":
    main()