"""
Lighting System - 光照系统
实现基础光照、阴影和后处理效果
"""

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


class LightType(Enum):
    """光源类型"""
    DIRECTIONAL = "directional"  # 方向光
    POINT = "point"              # 点光源
    SPOT = "spot"                # 聚光灯


@dataclass
class Light:
    """光源数据类"""
    light_type: LightType
    position: np.ndarray  # 位置 [x, y, z]
    direction: np.ndarray = None  # 方向向量
    color: Tuple[int, int, int] = (255, 255, 255)  # RGB颜色
    intensity: float = 1.0  # 强度
    attenuation: float = 1.0  # 衰减系数
    angle: float = 45.0  # 聚光灯角度（度）
    cast_shadows: bool = True  # 是否投射阴影


@dataclass
class Material:
    """材质数据类"""
    ambient: Tuple[float, float, float] = (0.1, 0.1, 0.1)  # 环境光反射
    diffuse: Tuple[float, float, float] = (0.8, 0.8, 0.8)  # 漫反射
    specular: Tuple[float, float, float] = (0.5, 0.5, 0.5)  # 镜面反射
    shininess: float = 32.0  # 高光系数


class LightingSystem:
    """光照系统管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 光源管理
        self.lights: List[Light] = []
        self.global_ambient = (0.2, 0.2, 0.2)  # 全局环境光
        
        # 材质管理
        self.materials: Dict[str, Material] = {}
        self.default_material = Material()
        
        # 阴影设置
        self.shadow_quality = self.config.get('shadow_quality', 'medium')
        self.shadow_resolution = self._get_shadow_resolution()
        
        # 后处理效果
        self.post_effects = {
            'bloom': False,
            'tone_mapping': True,
            'gamma_correction': True,
            'anti_aliasing': True
        }
        
        self.logger.info("LightingSystem初始化完成")
    
    def _get_shadow_resolution(self) -> Tuple[int, int]:
        """根据质量设置获取阴影分辨率"""
        quality_map = {
            'low': (512, 512),
            'medium': (1024, 1024),
            'high': (2048, 2048),
            'ultra': (4096, 4096)
        }
        return quality_map.get(self.shadow_quality, (1024, 1024))
    
    def add_light(self, light: Light) -> int:
        """添加光源，返回光源ID"""
        self.lights.append(light)
        light_id = len(self.lights) - 1
        self.logger.info(f"添加光源: {light.light_type.value}, ID: {light_id}")
        return light_id
    
    def remove_light(self, light_id: int):
        """移除指定ID的光源"""
        if 0 <= light_id < len(self.lights):
            removed_light = self.lights.pop(light_id)
            self.logger.info(f"移除光源: {removed_light.light_type.value}")
    
    def create_directional_light(self, direction: np.ndarray, 
                               color: Tuple[int, int, int] = (255, 255, 255),
                               intensity: float = 1.0) -> Light:
        """创建方向光"""
        # 确保方向向量不为零
        norm = np.linalg.norm(direction)
        if norm == 0:
            direction = np.array([0, -1, 0])  # 默认向下
        else:
            direction = direction / norm  # 标准化
            
        light = Light(
            light_type=LightType.DIRECTIONAL,
            position=np.array([0, 0, 0]),  # 方向光位置无关紧要
            direction=direction,
            color=color,
            intensity=intensity
        )
        self.add_light(light)
        return light
    
    def create_point_light(self, position: np.ndarray,
                          color: Tuple[int, int, int] = (255, 255, 255),
                          intensity: float = 1.0,
                          attenuation: float = 1.0) -> Light:
        """创建点光源"""
        light = Light(
            light_type=LightType.POINT,
            position=position,
            color=color,
            intensity=intensity,
            attenuation=attenuation
        )
        self.add_light(light)
        return light
    
    def create_spot_light(self, position: np.ndarray,
                         direction: np.ndarray,
                         color: Tuple[int, int, int] = (255, 255, 255),
                         intensity: float = 1.0,
                         angle: float = 45.0) -> Light:
        """创建聚光灯"""
        # 确保方向向量不为零
        norm = np.linalg.norm(direction)
        if norm == 0:
            direction = np.array([0, -1, 0])  # 默认向下
        else:
            direction = direction / norm  # 标准化
            
        light = Light(
            light_type=LightType.SPOT,
            position=position,
            direction=direction,
            color=color,
            intensity=intensity,
            angle=angle
        )
        self.add_light(light)
        return light
    
    def calculate_lighting(self, point: np.ndarray, normal: np.ndarray,
                          material: Material = None) -> Tuple[int, int, int]:
        """
        计算指定点的光照颜色
        
        Args:
            point: 世界坐标点
            normal: 表面法线向量
            material: 材质属性
            
        Returns:
            RGB颜色值 (0-255)
        """
        if material is None:
            material = self.default_material
            
        # 初始化颜色分量
        ambient = np.array(self.global_ambient)
        diffuse = np.array([0.0, 0.0, 0.0])
        specular = np.array([0.0, 0.0, 0.0])
        
        # 安全的视线向量计算（避免除零）
        point_norm = np.linalg.norm(point)
        if point_norm > 1e-6:  # 避免除零
            view_dir = -point / point_norm
        else:
            view_dir = np.array([0.0, 0.0, -1.0])  # 默认视线方向
        
        # 标准化法线向量
        normal_norm = np.linalg.norm(normal)
        if normal_norm > 1e-6:
            normal = normal / normal_norm
        else:
            normal = np.array([0.0, 1.0, 0.0])  # 默认法线方向
        
        # 计算每个光源的贡献
        for light in self.lights:
            light_contribution = self._calculate_light_contribution(
                light, point, normal, view_dir, material
            )
            diffuse += light_contribution['diffuse']
            specular += light_contribution['specular']
        
        # 合成最终颜色
        final_color = (
            ambient * np.array(material.ambient) +
            diffuse * np.array(material.diffuse) +
            specular * np.array(material.specular)
        )
        
        # 转换为0-255范围并确保数值有效
        final_color = np.clip(final_color * 255, 0, 255)
        # 处理可能的NaN值
        final_color = np.nan_to_num(final_color, nan=0.0, posinf=255.0, neginf=0.0)
        return tuple(int(c) for c in final_color)
    
    def _calculate_light_contribution(self, light: Light, point: np.ndarray,
                                    normal: np.ndarray, view_dir: np.ndarray,
                                    material: Material) -> Dict[str, np.ndarray]:
        """计算单个光源的光照贡献"""
        contribution = {
            'diffuse': np.array([0.0, 0.0, 0.0]),
            'specular': np.array([0.0, 0.0, 0.0])
        }
        
        if light.light_type == LightType.DIRECTIONAL:
            # 方向光计算
            light_dir = -light.direction
            # 确保方向向量标准化
            light_dir_norm = np.linalg.norm(light_dir)
            if light_dir_norm > 1e-6:
                light_dir = light_dir / light_dir_norm
            else:
                light_dir = np.array([0.0, -1.0, 0.0])
                
            contribution = self._calculate_directional_lighting(
                light, light_dir, normal, view_dir, material
            )
            
        elif light.light_type == LightType.POINT:
            # 点光源计算
            light_dir = light.position - point
            distance = np.linalg.norm(light_dir)
            if distance > 1e-6:  # 避免除零
                light_dir = light_dir / distance
                contribution = self._calculate_point_lighting(
                    light, light_dir, normal, view_dir, material, distance
                )
                
        elif light.light_type == LightType.SPOT:
            # 聚光灯计算
            light_dir = light.position - point
            distance = np.linalg.norm(light_dir)
            if distance > 1e-6:  # 避免除零
                light_dir = light_dir / distance
                contribution = self._calculate_spot_lighting(
                    light, light_dir, normal, view_dir, material, distance
                )
        
        return contribution
    
    def _calculate_directional_lighting(self, light: Light, light_dir: np.ndarray,
                                      normal: np.ndarray, view_dir: np.ndarray,
                                      material: Material) -> Dict[str, np.ndarray]:
        """计算方向光照明"""
        # 漫反射
        diff_factor = max(np.dot(normal, light_dir), 0)
        diffuse = np.array(light.color) / 255.0 * diff_factor * light.intensity
        
        # 镜面反射
        reflect_dir = 2 * np.dot(normal, light_dir) * normal - light_dir
        spec_factor = max(np.dot(view_dir, reflect_dir), 0) ** material.shininess
        specular = np.array(light.color) / 255.0 * spec_factor * light.intensity
        
        return {
            'diffuse': diffuse,
            'specular': specular
        }
    
    def _calculate_point_lighting(self, light: Light, light_dir: np.ndarray,
                                normal: np.ndarray, view_dir: np.ndarray,
                                material: Material, distance: float) -> Dict[str, np.ndarray]:
        """计算点光源照明"""
        # 衰减计算
        attenuation = 1.0 / (1.0 + light.attenuation * distance)
        
        # 漫反射
        diff_factor = max(np.dot(normal, light_dir), 0)
        diffuse = np.array(light.color) / 255.0 * diff_factor * light.intensity * attenuation
        
        # 镜面反射
        reflect_dir = 2 * np.dot(normal, light_dir) * normal - light_dir
        spec_factor = max(np.dot(view_dir, reflect_dir), 0) ** material.shininess
        specular = np.array(light.color) / 255.0 * spec_factor * light.intensity * attenuation
        
        return {
            'diffuse': diffuse,
            'specular': specular
        }
    
    def _calculate_spot_lighting(self, light: Light, light_dir: np.ndarray,
                               normal: np.ndarray, view_dir: np.ndarray,
                               material: Material, distance: float) -> Dict[str, np.ndarray]:
        """计算聚光灯照明"""
        # 衰减计算
        attenuation = 1.0 / (1.0 + light.attenuation * distance)
        
        # 聚光灯角度限制
        angle_cos = np.dot(-light_dir, light.direction)
        spot_cutoff = math.cos(math.radians(light.angle))
        
        if angle_cos < spot_cutoff:
            return {'diffuse': np.array([0.0, 0.0, 0.0]), 'specular': np.array([0.0, 0.0, 0.0])}
        
        # 聚光灯强度衰减
        spot_intensity = (angle_cos - spot_cutoff) / (1.0 - spot_cutoff)
        attenuation *= spot_intensity
        
        # 漫反射
        diff_factor = max(np.dot(normal, light_dir), 0)
        diffuse = np.array(light.color) / 255.0 * diff_factor * light.intensity * attenuation
        
        # 镜面反射
        reflect_dir = 2 * np.dot(normal, light_dir) * normal - light_dir
        spec_factor = max(np.dot(view_dir, reflect_dir), 0) ** material.shininess
        specular = np.array(light.color) / 255.0 * spec_factor * light.intensity * attenuation
        
        return {
            'diffuse': diffuse,
            'specular': specular
        }
    
    def render_shadows(self, screen, objects: List[Any]):
        """渲染阴影效果"""
        if not self.lights:
            return
            
        # 简化的阴影渲染（实际项目中需要深度缓冲）
        for light in self.lights:
            if light.cast_shadows:
                self._render_light_shadows(screen, light, objects)
    
    def _render_light_shadows(self, screen, light: Light, objects: List[Any]):
        """渲染单个光源的阴影"""
        # 这里实现简化的阴影算法
        # 实际项目中应该使用阴影贴图或光线追踪
        pass
    
    def apply_post_processing(self, screen):
        """应用后处理效果"""
        if not any(self.post_effects.values()):
            return
            
        # 这里实现后处理效果
        # 如Bloom、色调映射、伽马校正等
        pass
    
    def set_global_ambient(self, ambient: Tuple[float, float, float]):
        """设置全局环境光"""
        self.global_ambient = ambient
        self.logger.info(f"全局环境光设置为: {ambient}")
    
    def enable_post_effect(self, effect_name: str, enabled: bool = True):
        """启用/禁用后处理效果"""
        if effect_name in self.post_effects:
            self.post_effects[effect_name] = enabled
            self.logger.info(f"后处理效果 {effect_name}: {'启用' if enabled else '禁用'}")
    
    def get_light_count(self) -> int:
        """获取光源数量"""
        return len(self.lights)
    
    def cleanup(self):
        """清理光照系统资源"""
        self.lights.clear()
        self.materials.clear()
        self.logger.info("LightingSystem资源清理完成")


# 预设光照配置
class LightingPresets:
    """光照预设配置"""
    
    @staticmethod
    def sunny_day(lighting_system: LightingSystem):
        """晴天光照预设"""
        lighting_system.lights.clear()
        lighting_system.set_global_ambient((0.3, 0.3, 0.4))
        
        # 主太阳光（方向光）
        sun_direction = np.array([-0.5, -1.0, -0.3])
        lighting_system.create_directional_light(
            direction=sun_direction,
            color=(255, 240, 200),
            intensity=1.2
        )
        
        # 天空环境光
        sky_light = np.array([0.3, 0.3, 1.0])
        lighting_system.create_directional_light(
            direction=sky_light,
            color=(150, 180, 255),
            intensity=0.4
        )
    
    @staticmethod
    def indoor(lighting_system: LightingSystem):
        """室内光照预设"""
        lighting_system.lights.clear()
        lighting_system.set_global_ambient((0.1, 0.1, 0.1))
        
        # 主照明灯
        lighting_system.create_point_light(
            position=np.array([0, 3, 0]),
            color=(255, 240, 220),
            intensity=1.5,
            attenuation=0.5
        )
        
        # 辅助照明
        lighting_system.create_point_light(
            position=np.array([-2, 2, -2]),
            color=(200, 220, 255),
            intensity=0.8,
            attenuation=0.8
        )
    
    @staticmethod
    def dramatic(lighting_system: LightingSystem):
        """戏剧性光照预设"""
        lighting_system.lights.clear()
        lighting_system.set_global_ambient((0.05, 0.05, 0.1))
        
        # 强烈的主光源
        lighting_system.create_spot_light(
            position=np.array([2, 4, 3]),
            direction=np.array([-1, -2, -1]),
            color=(255, 200, 150),
            intensity=2.0,
            angle=30.0
        )
        
        # 背景补光
        lighting_system.create_point_light(
            position=np.array([-3, 2, -1]),
            color=(100, 150, 255),
            intensity=0.5,
            attenuation=1.0
        )