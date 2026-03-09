"""
Graphics Renderer - 图形渲染系统
适配Windows ARM64环境的渲染实现
"""

import logging
import numpy as np
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field

try:
    import pygame
    from pygame.locals import *
except ImportError as e:
    print(f"Pygame导入失败: {e}")
    raise

# 导入粒子系统和光照系统
from .particle_system import ParticleSystem, PresetEffects, ParticleType
from .lighting import LightingSystem, LightingPresets


@dataclass
class Camera:
    """摄像机数据类"""
    position: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 5.0], dtype=np.float32))
    target: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0], dtype=np.float32))
    up: np.ndarray = field(default_factory=lambda: np.array([0.0, 1.0, 0.0], dtype=np.float32))
    fov: float = 45.0
    near: float = 0.1
    far: float = 100.0


class Renderer:
    """图形渲染器 - Pygame实现"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化渲染器
        
        Args:
            config: 图形配置
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 窗口和显示
        self.screen = None
        self.width = config.get('width', 1280)
        self.height = config.get('height', 720)
        self.fullscreen = config.get('fullscreen', False)
        
        # 摄像机
        self.camera = Camera()
        self.yaw = -90.0
        self.pitch = 0.0
        
        # 渲染状态
        self.cube_rotation = 0.0
        self.clock = None
        
        # 粒子系统
        self.particle_system = ParticleSystem()
        self.effects_enabled = config.get('effects_enabled', True)
        
        # 光照系统
        self.lighting_system = LightingSystem(config.get('lighting', {}))
        self.lighting_enabled = config.get('lighting_enabled', True)
        
        # 特效触发器
        self.effect_triggers = {
            'explosion': False,
            'smoke': False,
            'fire': False,
            'magic': False,
            'sparkle': False
        }
        
        # 后处理设置
        self.post_processing = {
            'bloom': config.get('bloom', False),
            'tone_mapping': config.get('tone_mapping', True),
            'gamma_correction': config.get('gamma_correction', True),
            'anti_aliasing': config.get('anti_aliasing', True)
        }
        
        self.logger.info("Renderer (Pygame) 初始化完成")
    
    def initialize(self) -> bool:
        """
        初始化Pygame显示系统
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 初始化Pygame
            pygame.init()
            
            # 设置显示模式
            flags = pygame.DOUBLEBUF
            if self.fullscreen:
                flags |= pygame.FULLSCREEN
            
            self.screen = pygame.display.set_mode(
                (self.width, self.height), 
                flags
            )
            pygame.display.set_caption("SceneWeaver - AIGC实景导演")
            
            # 初始化时钟
            self.clock = pygame.time.Clock()
            
            # 初始化光照系统
            if self.lighting_enabled:
                self._setup_lighting()
            
            self.logger.info(f"Pygame显示系统初始化成功: {self.width}x{self.height}")
            return True
            
        except Exception as e:
            self.logger.error(f"图形系统初始化失败: {e}")
            return False
    
    def _setup_lighting(self):
        """设置光照系统"""
        # 设置默认光照预设
        lighting_preset = self.config.get('lighting_preset', 'sunny_day')
        
        if lighting_preset == 'sunny_day':
            LightingPresets.sunny_day(self.lighting_system)
        elif lighting_preset == 'indoor':
            LightingPresets.indoor(self.lighting_system)
        elif lighting_preset == 'dramatic':
            LightingPresets.dramatic(self.lighting_system)
        else:
            # 自定义光照设置
            self.lighting_system.create_directional_light(
                direction=np.array([-0.5, -1.0, -0.3]),
                color=(255, 240, 200),
                intensity=1.0
            )
        
        self.logger.info(f"光照系统初始化完成，预设: {lighting_preset}")
    
    def trigger_effect(self, effect_type: str, x: float = None, y: float = None):
        """触发动效"""
        if not self.effects_enabled:
            return
            
        x = x or self.width // 2
        y = y or self.height // 2
        
        if effect_type == 'explosion':
            PresetEffects.explosion_effect(self.particle_system, x, y, intensity=3)
        elif effect_type == 'smoke':
            emitter = PresetEffects.smoke_trail(self.particle_system, x, y)
            # 持续一段时间
            import threading
            def stop_smoke():
                import time
                time.sleep(3)
                emitter.active = False
            threading.Thread(target=stop_smoke, daemon=True).start()
        elif effect_type == 'fire':
            PresetEffects.fire_effect(self.particle_system, x, y)
        elif effect_type == 'magic':
            PresetEffects.magic_circle(self.particle_system, x, y)
        elif effect_type == 'sparkle':
            PresetEffects.sparkle_burst(self.particle_system, x, y, count=30)
        elif effect_type == 'lighting_preset':
            # 切换光照预设
            self._cycle_lighting_presets()
    
    def _cycle_lighting_presets(self):
        """循环切换光照预设"""
        presets = ['sunny_day', 'indoor', 'dramatic']
        current_preset = self.config.get('lighting_preset', 'sunny_day')
        current_index = presets.index(current_preset) if current_preset in presets else 0
        next_index = (current_index + 1) % len(presets)
        next_preset = presets[next_index]
        
        self.config['lighting_preset'] = next_preset
        self._setup_lighting()
        self.logger.info(f"切换光照预设到: {next_preset}")
    
    def update_camera(self, events: List[Any]):
        """更新摄像机位置"""
        camera_speed = self.config.get('movement_speed', 2.5) * (1/60.0)
        
        # 处理键盘输入
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_w]:  # 前进
            direction = self.camera.target - self.camera.position
            direction = direction / np.linalg.norm(direction)
            self.camera.position += direction * camera_speed
            self.camera.target += direction * camera_speed
            
        if keys[pygame.K_s]:  # 后退
            direction = self.camera.target - self.camera.position
            direction = direction / np.linalg.norm(direction)
            self.camera.position -= direction * camera_speed
            self.camera.target -= direction * camera_speed
            
        if keys[pygame.K_a]:  # 左移
            right = np.cross(self.camera.up, self.camera.target - self.camera.position)
            right = right / np.linalg.norm(right)
            self.camera.position -= right * camera_speed
            self.camera.target -= right * camera_speed
            
        if keys[pygame.K_d]:  # 右移
            right = np.cross(self.camera.up, self.camera.target - self.camera.position)
            right = right / np.linalg.norm(right)
            self.camera.position += right * camera_speed
            self.camera.target += right * camera_speed
    
    def clear(self):
        """清除屏幕"""
        if self.screen is None:
            self.logger.warning("屏幕未初始化")
            return
        self.screen.fill((25, 25, 25))  # 深灰色背景
    
    def render_scene(self):
        """渲染场景"""
        if self.screen is None:
            return
            
        # 渲染带光照的立方体
        self._render_lit_cube()
        
        # 渲染坐标轴指示器
        self._render_axis_indicator()
        
        # 渲染粒子效果
        if self.effects_enabled:
            self.particle_system.render(self.screen)
        
        # 应用后处理效果
        if any(self.post_processing.values()):
            self._apply_post_processing()
    
    def _render_lit_cube(self):
        """渲染带光照的立方体"""
        if self.screen is None:
            return
            
        center_x, center_y = self.width // 2, self.height // 2
        size = 100 + 50 * np.sin(np.radians(self.cube_rotation))
        
        # 立方体的世界坐标（简化）
        cube_pos = np.array([0, 0, 0])
        cube_normal = np.array([0, 0, 1])  # 简化的法线
        
        # 计算光照颜色
        if self.lighting_enabled and self.lighting_system.get_light_count() > 0:
            lit_color = self.lighting_system.calculate_lighting(cube_pos, cube_normal)
        else:
            # 默认颜色
            lit_color = (200, 150, 100)
        
        # 立方体的6个面（简化2D投影）
        faces = [
            # 前面
            [(center_x-size, center_y-size), (center_x+size, center_y-size),
             (center_x+size, center_y+size), (center_x-size, center_y+size)],
            
            # 上面  
            [(center_x-size, center_y-size), (center_x+size, center_y-size),
             (center_x+size+20, center_y-size-20), (center_x-size+20, center_y-size-20)],
        ]
        
        # 使用光照计算的颜色
        colors = [lit_color, self._adjust_brightness(lit_color, 1.2)]
        
        for face, color in zip(faces, colors):
            pygame.draw.polygon(self.screen, color, face)
            pygame.draw.polygon(self.screen, (255, 255, 255), face, 2)
        
        # 更新旋转角度
        self.cube_rotation += 2.0
    
    def _adjust_brightness(self, color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """调整颜色亮度"""
        adjusted = tuple(min(255, max(0, int(c * factor))) for c in color)
        return adjusted
    
    def _render_axis_indicator(self):
        """渲染坐标轴指示器"""
        if self.screen is None:
            return
            
        margin = 20
        length = 60
        
        # X轴 - 红色
        pygame.draw.line(self.screen, (255, 0, 0), 
                        (margin, margin), (margin + length, margin), 3)
        # Y轴 - 绿色
        pygame.draw.line(self.screen, (0, 255, 0), 
                        (margin, margin), (margin, margin + length), 3)
        # Z轴 - 蓝色
        pygame.draw.line(self.screen, (0, 0, 255), 
                        (margin, margin), (margin + length//2, margin + length//2), 3)
        
        # 轴标签
        font = pygame.font.Font(None, 24)
        x_text = font.render("X", True, (255, 0, 0))
        y_text = font.render("Y", True, (0, 255, 0))
        z_text = font.render("Z", True, (0, 0, 255))
        
        self.screen.blit(x_text, (margin + length + 5, margin - 10))
        self.screen.blit(y_text, (margin - 15, margin + length + 5))
        self.screen.blit(z_text, (margin + length//2 + 5, margin + length//2 + 5))
    
    def _apply_post_processing(self):
        """应用后处理效果"""
        # 简化的后处理实现
        if self.post_processing.get('bloom', False):
            self._apply_bloom_effect()
        
        if self.post_processing.get('gamma_correction', False):
            self._apply_gamma_correction()
    
    def _apply_bloom_effect(self):
        """应用泛光效果"""
        # 简化的泛光实现
        # 实际项目中需要使用帧缓冲和模糊算法
        pass
    
    def _apply_gamma_correction(self):
        """应用伽马校正"""
        # 简化的伽马校正
        # 实际项目中需要像素级处理
        pass
    
    def present(self):
        """更新显示"""
        if self.screen is None:
            return
        pygame.display.flip()
        if self.clock:
            self.clock.tick(60)  # 限制60FPS
    
    def update_scene(self, ai_results: Any, delta_time: float):
        """
        更新场景对象
        
        Args:
            ai_results: AI处理结果
            delta_time: 帧间隔时间
        """
        # 更新粒子系统
        if self.effects_enabled:
            self.particle_system.update(delta_time)
            
            # 根据AI结果触发动效
            if ai_results and hasattr(ai_results, 'detected_objects'):
                self._trigger_ai_effects(ai_results.detected_objects)
        
        # 更新光照系统
        if self.lighting_enabled:
            # 可以在这里添加动态光照更新逻辑
            pass
    
    def _trigger_ai_effects(self, detected_objects):
        """根据AI检测结果触发动效"""
        for obj in detected_objects:
            if obj.confidence > 0.8:  # 置信度阈值
                # 根据对象类型触发动效
                if obj.label in ['person', 'car']:
                    self.trigger_effect('sparkle', obj.x, obj.y)
                elif obj.label in ['fire', 'light']:
                    self.trigger_effect('fire', obj.x, obj.y)
    
    def cleanup(self):
        """清理Pygame资源"""
        # 清理粒子系统
        self.particle_system.clear_all()
        
        # 清理光照系统
        if self.lighting_system:
            self.lighting_system.cleanup()
        
        pygame.quit()
        self.logger.info("Renderer资源清理完成")