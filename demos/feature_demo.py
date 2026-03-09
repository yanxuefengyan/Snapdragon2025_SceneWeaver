#!/usr/bin/env python3
"""
Feature Demo - 功能演示程序
展示SceneWeaver新增的核心功能
"""

import sys
from pathlib import Path
import time
import logging

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.logger import setup_logger
from graphics.particle_system import ParticleSystem, PresetEffects, ParticleType


def demo_particle_system():
    """演示粒子系统功能"""
    print("✨ 粒子系统演示")
    print("-" * 30)
    
    # 创建粒子系统
    ps = ParticleSystem()
    
    # 演示不同类型的粒子效果
    effects = [
        (ParticleType.EXPLOSION, "爆炸效果"),
        (ParticleType.SMOKE, "烟雾效果"), 
        (ParticleType.FIRE, "火焰效果"),
        (ParticleType.MAGIC, "魔法效果"),
        (ParticleType.SPARKLE, "闪光效果")
    ]
    
    for particle_type, description in effects:
        print(f"  • {description}")
        emitter = ps.create_emitter(400, 300, particle_type)
        emitter.emit(20)  # 发射20个粒子
        
        # 模拟几帧更新
        for i in range(30):
            ps.update(1.0)
        
        # 显示当前粒子数量
        active_particles = len(emitter.particles)
        print(f"    活跃粒子数: {active_particles}")
    
    print(f"  总发射器数量: {len(ps.emitters)}")
    print()


def demo_presets():
    """演示预设效果"""
    print("🎯 预设效果演示")
    print("-" * 30)
    
    ps = ParticleSystem()
    
    print("  • 爆炸爆发")
    PresetEffects.explosion_effect(ps, 200, 200, intensity=3)
    
    print("  • 烟雾轨迹")
    smoke_emitter = PresetEffects.smoke_trail(ps, 400, 300)
    
    print("  • 火焰效果")
    fire_emitter = PresetEffects.fire_effect(ps, 600, 400)
    
    print("  • 魔法圆环")
    magic_emitter = PresetEffects.magic_circle(ps, 800, 300)
    
    print("  • 闪光爆发")
    PresetEffects.sparkle_burst(ps, 1000, 200, count=50)
    
    # 更新几帧
    for i in range(60):
        ps.update(1.0)
    
    total_particles = ps.get_total_particle_count()
    active_emitters = ps.get_active_emitter_count()
    
    print(f"  总粒子数: {total_particles}")
    print(f"  活跃发射器: {active_emitters}")
    print()


def main():
    """主演示函数"""
    print("🎮 SceneWeaver 新功能演示")
    print("=" * 50)
    print()
    
    # 设置日志
    setup_logger({'console_output': True}, logging.INFO)
    
    try:
        # 演示粒子系统
        demo_particle_system()
        
        # 演示预设效果
        demo_presets()
        
        print("✅ 所有功能演示完成！")
        print("\n📋 功能总结:")
        print("  • 粒子系统: 支持5种粒子类型")
        print("  • 预设效果: 爆炸、烟雾、火焰、魔法、闪光")
        print("  • 实时渲染: 60FPS流畅更新")
        print("  • 资源管理: 自动清理和优化")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        logging.error(f"演示错误: {e}")


if __name__ == "__main__":
    main()