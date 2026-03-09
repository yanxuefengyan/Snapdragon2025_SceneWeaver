#!/usr/bin/env python3
"""
Lighting Demo - 光照系统演示程序
展示SceneWeaver的光照系统功能
"""

import sys
from pathlib import Path
import time
import logging

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import pygame
    from pygame.locals import *
except ImportError as e:
    print(f"Pygame导入失败: {e}")
    sys.exit(1)

from graphics.lighting import LightingSystem, LightingPresets
from graphics.renderer import Renderer


def setup_demo_config():
    """设置演示配置"""
    return {
        'graphics': {
            'width': 1280,
            'height': 720,
            'fullscreen': False,
            'vsync': True,
            'lighting_enabled': True,
            'lighting_preset': 'sunny_day',
            'effects_enabled': True
        },
        'ai': {
            'device': 'cpu',
            'model_path': './models'
        },
        'input': {
            'mouse_sensitivity': 0.1,
            'movement_speed': 2.5
        },
        'performance': {
            'target_fps': 60,
            'enable_profiling': False
        }
    }


def create_demo_instructions():
    """创建演示说明"""
    instructions = """
    🎮 SceneWeaver 光照系统演示说明
    
    键盘控制:
    - WASD: 移动摄像机
    - L: 切换光照预设 (晴天/室内/戏剧性)
    - ESC: 退出程序
    - F1-F5: 触发不同特效
    
    光照预设说明:
    1. 晴天模式 - 自然的户外光照
    2. 室内模式 - 温暖的室内照明
    3. 戏剧性模式 - 强烈的对比光照
    
    当前演示将展示:
    - 实时光照计算
    - 不同材质的光照反应
    - 光源类型的效果差异
    - 预设光照场景切换
    """
    
    print(instructions)


class LightingDemo:
    """光照演示主类"""
    
    def __init__(self):
        self.config = setup_demo_config()
        self.renderer = None
        self.lighting_system = None
        self.running = False
        self.current_preset = 0
        self.presets = ['sunny_day', 'indoor', 'dramatic']
        
    def initialize(self):
        """初始化演示系统"""
        try:
            # 初始化渲染器
            self.renderer = Renderer(self.config['graphics'])
            if not self.renderer.initialize():
                return False
            
            # 获取光照系统引用
            self.lighting_system = self.renderer.lighting_system
            
            self.running = True
            return True
            
        except Exception as e:
            print(f"初始化失败: {e}")
            return False
    
    def handle_events(self):
        """处理输入事件"""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                elif event.key == K_l:
                    self.cycle_lighting_preset()
                elif event.key == K_F1:
                    self.renderer.trigger_effect('explosion')
                elif event.key == K_F2:
                    self.renderer.trigger_effect('fire')
                elif event.key == K_F3:
                    self.renderer.trigger_effect('magic')
                elif event.key == K_F4:
                    self.renderer.trigger_effect('sparkle')
                elif event.key == K_F5:
                    self.renderer.trigger_effect('smoke')
    
    def cycle_lighting_preset(self):
        """循环切换光照预设"""
        self.current_preset = (self.current_preset + 1) % len(self.presets)
        preset_name = self.presets[self.current_preset]
        
        # 应用新的光照预设
        if preset_name == 'sunny_day':
            LightingPresets.sunny_day(self.lighting_system)
        elif preset_name == 'indoor':
            LightingPresets.indoor(self.lighting_system)
        elif preset_name == 'dramatic':
            LightingPresets.dramatic(self.lighting_system)
        
        print(f"切换到光照预设: {preset_name}")
        print(f"当前光源数量: {self.lighting_system.get_light_count()}")
    
    def update(self, delta_time):
        """更新演示逻辑"""
        # 更新摄像机
        events = pygame.event.get()
        self.renderer.update_camera(events)
        
        # 更新场景
        self.renderer.update_scene(None, delta_time)
    
    def render(self):
        """渲染演示画面"""
        # 清除屏幕
        self.renderer.clear()
        
        # 渲染场景
        self.renderer.render_scene()
        
        # 渲染UI信息
        self.render_ui()
        
        # 更新显示
        self.renderer.present()
    
    def render_ui(self):
        """渲染用户界面信息"""
        if not self.renderer.screen:
            return
            
        # 显示当前状态
        font = pygame.font.Font(None, 24)
        
        # 当前预设信息
        preset_text = font.render(
            f"光照预设: {self.presets[self.current_preset]}", 
            True, (255, 255, 255)
        )
        self.renderer.screen.blit(preset_text, (10, 10))
        
        # 光源数量
        light_count_text = font.render(
            f"光源数量: {self.lighting_system.get_light_count()}", 
            True, (255, 255, 255)
        )
        self.renderer.screen.blit(light_count_text, (10, 40))
        
        # 控制说明
        controls = [
            "L: 切换光照预设",
            "F1-F5: 特效",
            "WASD: 移动",
            "ESC: 退出"
        ]
        
        for i, control in enumerate(controls):
            control_text = font.render(control, True, (200, 200, 200))
            self.renderer.screen.blit(control_text, (10, 70 + i * 25))
    
    def run(self, duration=60):
        """运行演示"""
        if not self.initialize():
            print("演示初始化失败")
            return
        
        print(f"开始{duration}秒光照演示...")
        start_time = time.time()
        
        clock = pygame.time.Clock()
        
        try:
            while self.running and (time.time() - start_time) < duration:
                delta_time = 1.0 / 60.0  # 固定60FPS时间步长
                
                self.handle_events()
                self.update(delta_time)
                self.render()
                
                clock.tick(60)
                
                # 显示进度
                elapsed = time.time() - start_time
                progress = (elapsed / duration) * 100
                if int(elapsed) % 10 == 0:  # 每10秒显示一次
                    print(f"\r进度: {progress:.1f}% | 运行时间: {elapsed:.1f}s", end="", flush=True)
            
            print(f"\n✅ {duration}秒演示完成！")
            
        except KeyboardInterrupt:
            print("\n👋 演示被用户中断")
        except Exception as e:
            print(f"\n❌ 演示运行出错: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理资源"""
        if self.renderer:
            self.renderer.cleanup()
        print("🔚 光照演示已退出")


def main():
    """主函数"""
    print("🌟 启动SceneWeaver光照系统演示...")
    print(f"Python版本: {sys.version}")
    print(f"平台: {sys.platform}")
    print()
    
    # 显示操作说明
    create_demo_instructions()
    
    # 创建并运行演示
    demo = LightingDemo()
    demo.run(duration=60)  # 运行60秒演示


if __name__ == "__main__":
    main()