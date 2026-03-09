#!/usr/bin/env python3
"""
SceneWeaver 图形功能演示程序
专注于展示核心图形功能，绕过AI相关问题
"""

import sys
import os
import time
import logging
from pathlib import Path

# 添加src目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from utils.logger import setup_logger
from graphics.particle_system import ParticleSystem, ParticleType, PresetEffects
from graphics.lighting import LightingSystem, LightingPresets
import pygame


def main():
    """主函数"""
    print("🚀 SceneWeaver 图形功能演示")
    print("=" * 50)
    
    # 设置日志
    setup_logger({'console_output': True}, logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # 初始化Pygame
        pygame.init()
        screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("SceneWeaver Graphics Demo")
        clock = pygame.time.Clock()
        
        print("✅ Pygame初始化成功")
        
        # 初始化粒子系统
        particle_system = ParticleSystem()
        print("✅ 粒子系统初始化成功")
        
        # 初始化光照系统
        lighting_system = LightingSystem()
        LightingPresets.sunny_day(lighting_system)
        print("✅ 光照系统初始化成功")
        
        # 当前粒子类型
        current_particle_type = ParticleType.EXPLOSION
        
        # 主循环
        running = True
        frame_count = 0
        start_time = time.time()
        
        print("\n🎮 演示控制说明:")
        print("- ESC: 退出程序")
        print("- 空格键: 触发当前类型粒子效果")
        print("- L键: 切换光照预设")
        print("- 数字键1-5: 切换粒子类型")
        print("  1=爆炸 2=烟雾 3=火焰 4=魔法 5=闪光")
        
        while running:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        # 触发粒子效果
                        x, y = pygame.mouse.get_pos()
                        if current_particle_type == ParticleType.EXPLOSION:
                            PresetEffects.explosion_effect(particle_system, x, y, intensity=3)
                        elif current_particle_type == ParticleType.SMOKE:
                            PresetEffects.smoke_trail(particle_system, x, y)
                        elif current_particle_type == ParticleType.FIRE:
                            PresetEffects.fire_effect(particle_system, x, y)
                        elif current_particle_type == ParticleType.MAGIC:
                            PresetEffects.magic_circle(particle_system, x, y)
                        elif current_particle_type == ParticleType.SPARKLE:
                            PresetEffects.sparkle_burst(particle_system, x, y, count=30)
                        print(f"💥 在位置 ({x}, {y}) 触发 {current_particle_type.name} 效果")
                    elif event.key == pygame.K_l:
                        # 切换光照预设
                        presets = ['sunny_day', 'indoor', 'dramatic']
                        preset_index = frame_count // 300 % len(presets)
                        preset_func = getattr(LightingPresets, presets[preset_index])
                        preset_func(lighting_system)
                        print(f"💡 切换到光照预设: {presets[preset_index]}")
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                        # 切换粒子类型
                        particle_types = [
                            ParticleType.EXPLOSION,
                            ParticleType.SMOKE,
                            ParticleType.FIRE,
                            ParticleType.MAGIC,
                            ParticleType.SPARKLE
                        ]
                        type_index = event.key - pygame.K_1
                        current_particle_type = particle_types[type_index]
                        print(f"✨ 切换到粒子类型: {current_particle_type.name}")
            
            # 更新粒子系统
            delta_time = clock.tick(60) / 1000.0
            particle_system.update(delta_time)
            
            # 渲染
            screen.fill((30, 30, 50))  # 深蓝色背景
            
            # 渲染粒子
            for emitter in particle_system.emitters:
                particle_type = emitter.particle_type  # 从发射器获取类型
                for particle in emitter.particles:
                    if particle.life > 0:
                        # 根据粒子类型设置颜色
                        if particle_type == ParticleType.EXPLOSION:
                            # 热色系
                            r = min(255, 200 + int(55 * (particle.life / particle.max_life)))
                            g = max(50, int(150 * (particle.life / particle.max_life)))
                            b = max(0, int(100 * (particle.life / particle.max_life)))
                        elif particle_type == ParticleType.FIRE:
                            # 火焰色
                            r = 255
                            g = max(100, int(200 * (particle.life / particle.max_life)))
                            b = max(0, int(50 * (particle.life / particle.max_life)))
                        elif particle_type == ParticleType.MAGIC:
                            # 魔法紫色
                            r = max(100, int(150 * (particle.life / particle.max_life)))
                            g = max(50, int(100 * (particle.life / particle.max_life)))
                            b = min(255, 200 + int(55 * (particle.life / particle.max_life)))
                        else:
                            # 默认白色系
                            intensity = int(200 * (particle.life / particle.max_life))
                            r = g = b = intensity
                        
                        # 应用透明度
                        alpha = int(255 * (particle.life / particle.max_life))
                        
                        # 绘制粒子
                        size = max(1, int(particle.size))
                        color = (r, g, b)
                        
                        pygame.draw.circle(screen, color, 
                                         (int(particle.x), int(particle.y)), size)
                        
                        # 绘制外圈增加层次感
                        if size > 2 and alpha > 50:
                            pygame.draw.circle(screen, 
                                             (min(255, r+30), min(255, g+30), min(255, b+30)),
                                             (int(particle.x), int(particle.y)), 
                                             size + 1, 1)
            
            # 显示信息
            font = pygame.font.Font(None, 36)
            info_text = [
                f"FPS: {clock.get_fps():.1f}",
                f"粒子发射器: {len(particle_system.emitters)}",
                f"活动粒子: {particle_system.get_total_particle_count()}",
                f"当前类型: {current_particle_type.name}",
                f"帧数: {frame_count}",
                f"运行时间: {time.time() - start_time:.1f}s"
            ]
            
            for i, text in enumerate(info_text):
                text_surface = font.render(text, True, (255, 255, 255))
                screen.blit(text_surface, (10, 10 + i * 30))
            
            # 更新显示
            pygame.display.flip()
            frame_count += 1
            
            # 自动触发一些效果
            if frame_count % 180 == 0:  # 每3秒
                x = 200 + (frame_count // 180) * 100
                y = 300
                if x < 1000:
                    PresetEffects.explosion_effect(particle_system, x, y, intensity=2)
                    print(f"🤖 自动触发爆炸效果 at ({x}, {y})")
        
        # 清理
        particle_system.clear_all()
        pygame.quit()
        print("\n👋 演示结束，感谢使用SceneWeaver!")
        
    except Exception as e:
        logger.error(f"演示程序出错: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()


if __name__ == "__main__":
    main()