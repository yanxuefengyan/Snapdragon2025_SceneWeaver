"""
Particle System - 粒子系统
实现各种粒子效果，包括爆炸、烟雾、魔法效果等
"""

import random
import math
import logging
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum

try:
    import pygame
    import numpy as np
except ImportError as e:
    print(f"依赖导入失败: {e}")
    raise


class ParticleType(Enum):
    """粒子类型枚举"""
    EXPLOSION = "explosion"
    SMOKE = "smoke"
    FIRE = "fire"
    MAGIC = "magic"
    SPARKLE = "sparkle"


@dataclass
class Particle:
    """粒子数据类"""
    x: float
    y: float
    vx: float  # x方向速度
    vy: float  # y方向速度
    life: float  # 生命周期
    max_life: float  # 最大生命周期
    size: float  # 粒子大小
    color: Tuple[int, int, int]  # RGB颜色
    alpha: int = 255  # 透明度
    gravity: float = 0.0  # 重力影响
    drag: float = 0.99  # 空气阻力


class ParticleEmitter:
    """粒子发射器"""
    
    def __init__(self, x: float, y: float, particle_type: ParticleType = ParticleType.EXPLOSION):
        self.x = x
        self.y = y
        self.particle_type = particle_type
        self.particles: List[Particle] = []
        self.active = True
        self.emit_rate = 10  # 每帧发射粒子数
        self.logger = logging.getLogger(__name__)
    
    def emit(self, count: int = None):
        """发射粒子"""
        if not self.active:
            return
            
        emit_count = count or self.emit_rate
        
        for _ in range(emit_count):
            particle = self._create_particle()
            self.particles.append(particle)
    
    def _create_particle(self) -> Particle:
        """创建单个粒子"""
        if self.particle_type == ParticleType.EXPLOSION:
            return self._create_explosion_particle()
        elif self.particle_type == ParticleType.SMOKE:
            return self._create_smoke_particle()
        elif self.particle_type == ParticleType.FIRE:
            return self._create_fire_particle()
        elif self.particle_type == ParticleType.MAGIC:
            return self._create_magic_particle()
        elif self.particle_type == ParticleType.SPARKLE:
            return self._create_sparkle_particle()
        else:
            return self._create_default_particle()
    
    def _create_explosion_particle(self) -> Particle:
        """创建爆炸粒子"""
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 8)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        life = random.uniform(30, 60)
        size = random.uniform(2, 6)
        color = (
            random.randint(200, 255),  # 红色
            random.randint(100, 200),  # 绿色
            random.randint(50, 150)    # 蓝色
        )
        
        return Particle(
            x=self.x,
            y=self.y,
            vx=vx,
            vy=vy,
            life=life,
            max_life=life,
            size=size,
            color=color,
            gravity=0.1,
            drag=0.98
        )
    
    def _create_smoke_particle(self) -> Particle:
        """创建烟雾粒子"""
        vx = random.uniform(-1, 1)
        vy = random.uniform(-2, -0.5)
        
        life = random.uniform(60, 120)
        size = random.uniform(3, 8)
        color = (
            random.randint(150, 200),  # 灰色调
            random.randint(150, 200),
            random.randint(150, 200)
        )
        
        return Particle(
            x=self.x,
            y=self.y,
            vx=vx,
            vy=vy,
            life=life,
            max_life=life,
            size=size,
            color=color,
            gravity=-0.05,  # 向上飘
            drag=0.995
        )
    
    def _create_fire_particle(self) -> Particle:
        """创建火焰粒子"""
        angle = random.uniform(-0.3, 0.3)  # 主要向上
        speed = random.uniform(1, 4)
        vx = math.sin(angle) * speed
        vy = -math.cos(angle) * speed  # 向上
        
        life = random.uniform(20, 40)
        size = random.uniform(2, 5)
        color = (
            random.randint(255, 255),  # 黄橙色
            random.randint(100, 200),
            random.randint(0, 50)
        )
        
        return Particle(
            x=self.x,
            y=self.y,
            vx=vx,
            vy=vy,
            life=life,
            max_life=life,
            size=size,
            color=color,
            gravity=0.05,
            drag=0.99
        )
    
    def _create_magic_particle(self) -> Particle:
        """创建魔法粒子"""
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 3)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        life = random.uniform(40, 80)
        size = random.uniform(1, 3)
        hue = random.randint(0, 360)
        # 转换HSV到RGB
        color = self._hsv_to_rgb(hue, 1.0, 1.0)
        
        return Particle(
            x=self.x,
            y=self.y,
            vx=vx,
            vy=vy,
            life=life,
            max_life=life,
            size=size,
            color=color,
            gravity=0.0,
            drag=0.999
        )
    
    def _create_sparkle_particle(self) -> Particle:
        """创建闪光粒子"""
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.5, 2)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        life = random.uniform(15, 30)
        size = random.uniform(1, 2)
        brightness = random.randint(200, 255)
        color = (brightness, brightness, brightness)
        
        return Particle(
            x=self.x,
            y=self.y,
            vx=vx,
            vy=vy,
            life=life,
            max_life=life,
            size=size,
            color=color,
            alpha=random.randint(200, 255),
            gravity=0.0,
            drag=1.0
        )
    
    def _create_default_particle(self) -> Particle:
        """创建默认粒子"""
        vx = random.uniform(-2, 2)
        vy = random.uniform(-2, 2)
        
        return Particle(
            x=self.x,
            y=self.y,
            vx=vx,
            vy=vy,
            life=60,
            max_life=60,
            size=3,
            color=(255, 255, 255)
        )
    
    def _hsv_to_rgb(self, h, s, v) -> Tuple[int, int, int]:
        """HSV转RGB"""
        h = h % 360
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        
        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
            
        return (
            int((r + m) * 255),
            int((g + m) * 255),
            int((b + m) * 255)
        )
    
    def update(self, delta_time: float = 1.0):
        """更新粒子状态"""
        if not self.active:
            return
        
        # 更新每个粒子
        for particle in self.particles[:]:  # 使用副本避免修改列表时的问题
            # 更新位置
            particle.x += particle.vx * delta_time
            particle.y += particle.vy * delta_time
            
            # 应用重力和阻力
            particle.vy += particle.gravity * delta_time
            particle.vx *= particle.drag
            particle.vy *= particle.drag
            
            # 更新生命周期
            particle.life -= delta_time
            
            # 更新透明度（随生命周期衰减）
            particle.alpha = int(255 * (particle.life / particle.max_life))
            
            # 移除死亡粒子
            if particle.life <= 0:
                self.particles.remove(particle)
    
    def render(self, screen):
        """渲染粒子"""
        if not screen:
            return
            
        for particle in self.particles:
            if particle.alpha > 0:
                # 创建带透明度的颜色
                color_with_alpha = (*particle.color, particle.alpha)
                
                # 绘制粒子（圆形）
                pygame.draw.circle(
                    screen,
                    particle.color,
                    (int(particle.x), int(particle.y)),
                    int(particle.size)
                )
                
                # 绘制外圈增加视觉效果
                if particle.size > 2:
                    pygame.draw.circle(
                        screen,
                        (min(255, particle.color[0] + 50),
                         min(255, particle.color[1] + 50),
                         min(255, particle.color[2] + 50)),
                        (int(particle.x), int(particle.y)),
                        int(particle.size + 1),
                        1
                    )


class ParticleSystem:
    """粒子系统管理器"""
    
    def __init__(self):
        self.emitters: List[ParticleEmitter] = []
        self.logger = logging.getLogger(__name__)
        self.logger.info("ParticleSystem初始化完成")
    
    def create_emitter(self, x: float, y: float, particle_type: ParticleType = ParticleType.EXPLOSION) -> ParticleEmitter:
        """创建新的粒子发射器"""
        emitter = ParticleEmitter(x, y, particle_type)
        self.emitters.append(emitter)
        return emitter
    
    def remove_emitter(self, emitter: ParticleEmitter):
        """移除粒子发射器"""
        if emitter in self.emitters:
            self.emitters.remove(emitter)
    
    def update(self, delta_time: float = 1.0):
        """更新所有粒子发射器"""
        for emitter in self.emitters[:]:  # 使用副本
            emitter.update(delta_time)
            
            # 移除不活跃且无粒子的发射器
            if not emitter.active and len(emitter.particles) == 0:
                self.emitters.remove(emitter)
    
    def render(self, screen):
        """渲染所有粒子"""
        for emitter in self.emitters:
            emitter.render(screen)
    
    def clear_all(self):
        """清空所有粒子"""
        self.emitters.clear()
    
    def get_active_emitter_count(self) -> int:
        """获取活跃发射器数量"""
        return len([e for e in self.emitters if e.active])
    
    def get_total_particle_count(self) -> int:
        """获取总粒子数量"""
        return sum(len(emitter.particles) for emitter in self.emitters)


# 预设的粒子效果组合
class PresetEffects:
    """预设粒子效果"""
    
    @staticmethod
    def explosion_effect(particle_system: ParticleSystem, x: float, y: float, intensity: int = 5):
        """爆炸效果"""
        for _ in range(intensity):
            emitter = particle_system.create_emitter(x, y, ParticleType.EXPLOSION)
            emitter.emit_rate = 20
            emitter.emit(30)  # 立即发射大量粒子
            emitter.active = False  # 一次性效果
    
    @staticmethod
    def smoke_trail(particle_system: ParticleSystem, x: float, y: float) -> ParticleEmitter:
        """烟雾轨迹"""
        emitter = particle_system.create_emitter(x, y, ParticleType.SMOKE)
        emitter.emit_rate = 3
        return emitter
    
    @staticmethod
    def fire_effect(particle_system: ParticleSystem, x: float, y: float) -> ParticleEmitter:
        """火焰效果"""
        emitter = particle_system.create_emitter(x, y, ParticleType.FIRE)
        emitter.emit_rate = 8
        return emitter
    
    @staticmethod
    def magic_circle(particle_system: ParticleSystem, x: float, y: float) -> ParticleEmitter:
        """魔法阵效果"""
        emitter = particle_system.create_emitter(x, y, ParticleType.MAGIC)
        emitter.emit_rate = 15
        return emitter
    
    @staticmethod
    def sparkle_burst(particle_system: ParticleSystem, x: float, y: float, count: int = 50):
        """闪光爆发"""
        emitter = particle_system.create_emitter(x, y, ParticleType.SPARKLE)
        emitter.emit(count)
        emitter.active = False  # 一次性效果