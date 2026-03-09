"""
Particle System 单元测试
测试粒子系统的各种功能和效果
"""

import unittest
import sys
from pathlib import Path
import numpy as np

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from graphics.particle_system import ParticleSystem, ParticleEmitter, Particle
from utils.config_manager import ConfigManager


class TestParticle(unittest.TestCase):
    """粒子类测试"""
    
    def setUp(self):
        """测试前准备"""
        self.particle = Particle(
            position=np.array([0.0, 0.0, 0.0]),
            velocity=np.array([1.0, 1.0, 0.0]),
            lifetime=5.0,
            color=(255, 255, 255)
        )
    
    def test_particle_initialization(self):
        """测试粒子初始化"""
        self.assertIsNotNone(self.particle)
        np.testing.assert_array_equal(self.particle.position, [0.0, 0.0, 0.0])
        np.testing.assert_array_equal(self.particle.velocity, [1.0, 1.0, 0.0])
        self.assertEqual(self.particle.lifetime, 5.0)
        self.assertEqual(self.particle.color, (255, 255, 255))
        self.assertTrue(self.particle.active)
    
    def test_particle_update(self):
        """测试粒子更新"""
        dt = 0.1
        initial_position = self.particle.position.copy()
        
        self.particle.update(dt)
        
        # 验证位置更新
        expected_position = initial_position + self.particle.velocity * dt
        np.testing.assert_array_almost_equal(self.particle.position, expected_position)
        
        # 验证生命周期减少
        self.assertEqual(self.particle.lifetime, 4.9)
        
        # 验证粒子仍然活跃
        self.assertTrue(self.particle.active)
    
    def test_particle_lifetime_expiration(self):
        """测试粒子生命周期到期"""
        # 更新超过生命周期
        for _ in range(51):  # 5.0 / 0.1 = 50次更新
            self.particle.update(0.1)
        
        # 粒子应该不再活跃
        self.assertFalse(self.particle.active)
        self.assertEqual(self.particle.lifetime, 0.0)


class TestParticleEmitter(unittest.TestCase):
    """粒子发射器测试"""
    
    def setUp(self):
        """测试前准备"""
        config_manager = ConfigManager()
        self.config = config_manager.get_config()
        self.emitter = ParticleEmitter(
            position=np.array([0.0, 0.0, 0.0]),
            particle_type="explosion",
            config=self.config
        )
    
    def test_emitter_initialization(self):
        """测试发射器初始化"""
        self.assertIsNotNone(self.emitter)
        np.testing.assert_array_equal(self.emitter.position, [0.0, 0.0, 0.0])
        self.assertEqual(self.emitter.particle_type, "explosion")
        self.assertEqual(len(self.emitter.particles), 0)
        self.assertTrue(self.emitter.active)
    
    def test_emitter_emit_particles(self):
        """测试发射粒子"""
        count = 10
        self.emitter.emit(count)
        
        self.assertEqual(len(self.emitter.particles), count)
        for particle in self.emitter.particles:
            self.assertTrue(particle.active)
    
    def test_emitter_update(self):
        """测试发射器更新"""
        # 先发射一些粒子
        self.emitter.emit(5)
        initial_particle_count = len(self.emitter.particles)
        
        # 更新发射器
        dt = 0.1
        self.emitter.update(dt)
        
        # 验证粒子被更新
        self.assertEqual(len(self.emitter.particles), initial_particle_count)
        # 验证所有粒子都被更新了一次
        for particle in self.emitter.particles:
            self.assertEqual(particle.lifetime, 4.9)  # 假设初始生命周期为5.0
    
    def test_emitter_cleanup_inactive_particles(self):
        """测试清理不活跃粒子"""
        # 发射粒子并让它们过期
        self.emitter.emit(5)
        
        # 让粒子生命周期过期
        for _ in range(51):
            self.emitter.update(0.1)
        
        # 验证所有粒子都被清理
        self.assertEqual(len(self.emitter.particles), 0)


class TestParticleSystem(unittest.TestCase):
    """粒子系统测试"""
    
    def setUp(self):
        """测试前准备"""
        config_manager = ConfigManager()
        self.config = config_manager.get_config()
        self.particle_system = ParticleSystem(self.config)
    
    def test_system_initialization(self):
        """测试粒子系统初始化"""
        self.assertIsNotNone(self.particle_system)
        self.assertEqual(len(self.particle_system.emitters), 0)
        self.assertTrue(self.particle_system.enabled)
        self.logger = self.particle_system.logger
    
    def test_add_emitter(self):
        """测试添加发射器"""
        position = np.array([1.0, 2.0, 3.0])
        emitter_type = "explosion"
        
        emitter_id = self.particle_system.add_emitter(position, emitter_type)
        
        self.assertIsNotNone(emitter_id)
        self.assertEqual(len(self.particle_system.emitters), 1)
        
        emitter = self.particle_system.emitters[emitter_id]
        np.testing.assert_array_equal(emitter.position, position)
        self.assertEqual(emitter.particle_type, emitter_type)
    
    def test_remove_emitter(self):
        """测试移除发射器"""
        # 先添加一个发射器
        emitter_id = self.particle_system.add_emitter(np.array([0, 0, 0]), "explosion")
        self.assertEqual(len(self.particle_system.emitters), 1)
        
        # 移除发射器
        result = self.particle_system.remove_emitter(emitter_id)
        
        self.assertTrue(result)
        self.assertEqual(len(self.particle_system.emitters), 0)
    
    def test_remove_nonexistent_emitter(self):
        """测试移除不存在的发射器"""
        result = self.particle_system.remove_emitter("nonexistent")
        self.assertFalse(result)
    
    def test_trigger_effect(self):
        """测试触发预设效果"""
        # 测试爆炸效果
        effect_id = self.particle_system.trigger_effect("explosion")
        self.assertIsNotNone(effect_id)
        self.assertGreater(len(self.particle_system.emitters), 0)
        
        # 测试烟雾效果
        effect_id = self.particle_system.trigger_effect("smoke")
        self.assertIsNotNone(effect_id)
    
    def test_update_system(self):
        """测试系统更新"""
        # 添加一个发射器并发射粒子
        emitter_id = self.particle_system.add_emitter(np.array([0, 0, 0]), "explosion")
        emitter = self.particle_system.emitters[emitter_id]
        emitter.emit(10)
        
        initial_particle_count = len(emitter.particles)
        
        # 更新系统
        dt = 0.1
        self.particle_system.update(dt)
        
        # 验证系统被更新
        self.assertEqual(len(emitter.particles), initial_particle_count)
    
    def test_get_active_particle_count(self):
        """测试获取活跃粒子数量"""
        # 初始状态应该没有活跃粒子
        count = self.particle_system.get_active_particle_count()
        self.assertEqual(count, 0)
        
        # 添加发射器并发射粒子
        emitter_id = self.particle_system.add_emitter(np.array([0, 0, 0]), "explosion")
        emitter = self.particle_system.emitters[emitter_id]
        emitter.emit(5)
        
        # 应该有5个活跃粒子
        count = self.particle_system.get_active_particle_count()
        self.assertEqual(count, 5)
    
    def test_cleanup(self):
        """测试系统清理"""
        # 添加一些发射器
        self.particle_system.add_emitter(np.array([0, 0, 0]), "explosion")
        self.particle_system.add_emitter(np.array([1, 1, 1]), "smoke")
        self.assertEqual(len(self.particle_system.emitters), 2)
        
        # 清理系统
        self.particle_system.cleanup()
        
        # 验证所有发射器都被移除
        self.assertEqual(len(self.particle_system.emitters), 0)


class TestParticleTypes(unittest.TestCase):
    """粒子类型测试"""
    
    def setUp(self):
        """测试前准备"""
        config_manager = ConfigManager()
        self.config = config_manager.get_config()
    
    def test_explosion_emitter_properties(self):
        """测试爆炸发射器属性"""
        emitter = ParticleEmitter(np.array([0, 0, 0]), "explosion", self.config)
        
        # 验证爆炸粒子的特殊属性
        self.assertEqual(emitter.particle_type, "explosion")
        self.assertGreaterEqual(emitter.particle_speed_range[1], emitter.particle_speed_range[0])
    
    def test_smoke_emitter_properties(self):
        """测试烟雾发射器属性"""
        emitter = ParticleEmitter(np.array([0, 0, 0]), "smoke", self.config)
        
        self.assertEqual(emitter.particle_type, "smoke")
        # 烟雾粒子应该有不同的生命周期范围
        self.assertGreater(emitter.particle_lifetime_range[1], emitter.particle_lifetime_range[0])
    
    def test_fire_emitter_properties(self):
        """测试火焰发射器属性"""
        emitter = ParticleEmitter(np.array([0, 0, 0]), "fire", self.config)
        
        self.assertEqual(emitter.particle_type, "fire")
        # 验证火焰颜色范围
        self.assertIsNotNone(emitter.particle_color_range)


if __name__ == '__main__':
    unittest.main()