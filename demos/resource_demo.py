#!/usr/bin/env python3
"""
Resource Manager Demo - 资源管理器演示程序
展示SceneWeaver的资源管理系统功能
"""

import sys
from pathlib import Path
import time
import logging
import tempfile
import shutil

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import pygame
    from pygame.locals import *
except ImportError as e:
    print(f"Pygame导入失败: {e}")
    sys.exit(1)

from utils.resource_manager import ResourceManager, ResourceManagerFactory, ResourceType


def setup_demo_config():
    """设置演示配置"""
    # 创建临时目录用于演示
    temp_dir = Path(tempfile.mkdtemp(prefix="scene_weaver_demo_"))
    
    return {
        'resource_manager': {
            'model_path': str(temp_dir / 'models'),
            'texture_path': str(temp_dir / 'textures'),
            'audio_path': str(temp_dir / 'audio'),
            'cache_path': str(temp_dir / 'cache'),
            'max_cache_size_mb': 50,
            'cache_strategy': 'lru'
        },
        'graphics': {
            'width': 1024,
            'height': 768,
            'fullscreen': False
        }
    }, temp_dir


def create_demo_resources(temp_dir: Path):
    """创建演示用的资源文件"""
    # 创建模型文件
    models_dir = temp_dir / 'models'
    models_dir.mkdir(exist_ok=True)
    
    model_files = {
        'cube.obj': """# Cube Model
v -1.0 -1.0  1.0
v  1.0 -1.0  1.0
v  1.0  1.0  1.0
v -1.0  1.0  1.0
v -1.0 -1.0 -1.0
v  1.0 -1.0 -1.0
v  1.0  1.0 -1.0
v -1.0  1.0 -1.0
""",
        'sphere.obj': """# Sphere Model
v 0.0 0.0 1.0
v 0.707 0.0 0.707
v 1.0 0.0 0.0
"""
    }
    
    for filename, content in model_files.items():
        (models_dir / filename).write_text(content)
    
    # 创建纹理文件（简单文本文件模拟）
    textures_dir = temp_dir / 'textures'
    textures_dir.mkdir(exist_ok=True)
    
    texture_files = {
        'wood.jpg': 'JPEG_TEXTURE_DATA_PLACEHOLDER',
        'metal.png': 'PNG_TEXTURE_DATA_PLACEHOLDER',
        'grass.bmp': 'BMP_TEXTURE_DATA_PLACEHOLDER'
    }
    
    for filename, content in texture_files.items():
        (textures_dir / filename).write_text(content)
    
    # 创建着色器文件
    shaders_dir = temp_dir / 'shaders'
    shaders_dir.mkdir(exist_ok=True)
    
    shader_files = {
        'vertex.glsl': """#version 330 core
layout (location = 0) in vec3 aPos;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
void main()
{
    gl_Position = projection * view * model * vec4(aPos, 1.0);
}
""",
        'fragment.glsl': """#version 330 core
out vec4 FragColor;
uniform vec3 objectColor;
void main()
{
    FragColor = vec4(objectColor, 1.0);
}
"""
    }
    
    for filename, content in shader_files.items():
        (shaders_dir / filename).write_text(content)
    
    print(f"✅ 创建了演示资源文件在: {temp_dir}")


class ResourceManagerDemo:
    """资源管理器演示主类"""
    
    def __init__(self):
        self.config, self.temp_dir = setup_demo_config()
        self.resource_manager = None
        self.screen = None
        self.running = False
        self.demo_step = 0
        
    def initialize(self):
        """初始化演示系统"""
        try:
            # 初始化Pygame
            pygame.init()
            self.screen = pygame.display.set_mode(
                (self.config['graphics']['width'], self.config['graphics']['height'])
            )
            pygame.display.set_caption("SceneWeaver 资源管理器演示")
            
            # 初始化资源管理器
            self.resource_manager = ResourceManagerFactory.get_instance(
                self.config['resource_manager']
            )
            
            # 创建演示资源
            create_demo_resources(self.temp_dir)
            
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
                elif event.key == K_SPACE:
                    self.demo_step += 1
                    self.run_demo_step()
    
    def run_demo_step(self):
        """运行演示步骤"""
        steps = [
            self.demo_resource_registration,
            self.demo_resource_loading,
            self.demo_cache_management,
            self.demo_resource_listing
        ]
        
        if self.demo_step < len(steps):
            steps[self.demo_step]()
        else:
            print("🎉 所有演示步骤已完成！")
            self.demo_step = 0  # 重新开始
    
    def demo_resource_registration(self):
        """演示资源注册"""
        print("\n📝 演示步骤 1: 资源注册")
        print("-" * 40)
        
        # 注册模型资源
        models_registered = 0
        for model_file in (self.temp_dir / 'models').glob('*.obj'):
            resource_id = f"model_{model_file.stem}"
            success = self.resource_manager.register_resource(
                resource_id=resource_id,
                resource_type=ResourceType.MODEL,
                file_path=str(model_file),
                version="1.0.0",
                metadata={
                    "description": f"3D {model_file.stem} model",
                    "format": "OBJ"
                }
            )
            if success:
                models_registered += 1
                print(f"   ✅ 注册模型: {resource_id}")
        
        # 注册纹理资源
        textures_registered = 0
        for texture_file in (self.temp_dir / 'textures').glob('*.*'):
            resource_id = f"texture_{texture_file.stem}"
            success = self.resource_manager.register_resource(
                resource_id=resource_id,
                resource_type=ResourceType.TEXTURE,
                file_path=str(texture_file),
                version="1.0.0",
                metadata={
                    "description": f"{texture_file.stem} texture",
                    "format": texture_file.suffix.upper()[1:]
                }
            )
            if success:
                textures_registered += 1
                print(f"   ✅ 注册纹理: {resource_id}")
        
        # 注册着色器资源
        shaders_registered = 0
        for shader_file in (self.temp_dir / 'shaders').glob('*.glsl'):
            resource_id = f"shader_{shader_file.stem}"
            success = self.resource_manager.register_resource(
                resource_id=resource_id,
                resource_type=ResourceType.SHADER,
                file_path=str(shader_file),
                version="1.0.0",
                metadata={
                    "description": f"{shader_file.stem} shader",
                    "type": "vertex" if "vertex" in shader_file.name else "fragment"
                }
            )
            if success:
                shaders_registered += 1
                print(f"   ✅ 注册着色器: {resource_id}")
        
        print(f"\n📊 注册统计:")
        print(f"   模型资源: {models_registered} 个")
        print(f"   纹理资源: {textures_registered} 个")
        print(f"   着色器资源: {shaders_registered} 个")
        print(f"   总计: {models_registered + textures_registered + shaders_registered} 个资源")
    
    def demo_resource_loading(self):
        """演示资源加载"""
        print("\n📥 演示步骤 2: 资源加载")
        print("-" * 40)
        
        # 加载模型资源
        print("   加载模型资源:")
        model_resources = self.resource_manager.list_resources(ResourceType.MODEL)
        for resource_id in model_resources[:2]:  # 只加载前两个
            data = self.resource_manager.load_resource(resource_id)
            if data:
                print(f"   ✅ 加载成功: {resource_id}")
                # 显示部分内容
                content_preview = str(data)[:100] + "..." if len(str(data)) > 100 else str(data)
                print(f"      内容预览: {content_preview}")
            else:
                print(f"   ❌ 加载失败: {resource_id}")
        
        # 加载着色器资源
        print("\n   加载着色器资源:")
        shader_resources = self.resource_manager.list_resources(ResourceType.SHADER)
        for resource_id in shader_resources:
            data = self.resource_manager.load_resource(resource_id)
            if data:
                print(f"   ✅ 加载成功: {resource_id}")
                # 显示前几行
                lines = str(data).split('\n')[:3]
                for line in lines:
                    print(f"      {line}")
            else:
                print(f"   ❌ 加载失败: {resource_id}")
    
    def demo_cache_management(self):
        """演示缓存管理"""
        print("\n💾 演示步骤 3: 缓存管理")
        print("-" * 40)
        
        # 显示当前缓存状态
        print(f"   当前缓存条目数: {len(self.resource_manager.resource_cache)}")
        print(f"   当前缓存大小: {self.resource_manager.current_cache_size} bytes")
        print(f"   最大缓存大小: {self.resource_manager.max_cache_size} bytes")
        
        # 测试缓存命中
        print("\n   测试缓存命中:")
        model_resources = self.resource_manager.list_resources(ResourceType.MODEL)
        if model_resources:
            resource_id = model_resources[0]
            # 第一次加载（从磁盘）
            start_time = time.time()
            data1 = self.resource_manager.load_resource(resource_id, force_reload=True)
            first_load_time = time.time() - start_time
            
            # 第二次加载（从缓存）
            start_time = time.time()
            data2 = self.resource_manager.load_resource(resource_id)
            cache_load_time = time.time() - start_time
            
            print(f"   磁盘加载时间: {first_load_time*1000:.2f}ms")
            print(f"   缓存加载时间: {cache_load_time*1000:.2f}ms")
            print(f"   性能提升: {first_load_time/cache_load_time:.1f}x")
    
    def demo_resource_listing(self):
        """演示资源列表"""
        print("\n📋 演示步骤 4: 资源列表")
        print("-" * 40)
        
        # 按类型列出资源
        resource_types = [
            (ResourceType.MODEL, "模型"),
            (ResourceType.TEXTURE, "纹理"),
            (ResourceType.SHADER, "着色器"),
            (ResourceType.AUDIO, "音频"),
            (ResourceType.CONFIG, "配置")
        ]
        
        total_resources = 0
        for res_type, display_name in resource_types:
            resources = self.resource_manager.list_resources(res_type)
            count = len(resources)
            total_resources += count
            print(f"   {display_name}资源: {count} 个")
            if resources:
                for resource_id in resources[:3]:  # 只显示前3个
                    info = self.resource_manager.get_resource_info(resource_id)
                    if info:
                        print(f"      - {resource_id} (v{info.version})")
                if count > 3:
                    print(f"      ... 还有 {count - 3} 个资源")
        
        print(f"\n📊 总计: {total_resources} 个资源")
    
    def render(self):
        """渲染演示界面"""
        if not self.screen:
            return
            
        # 清除屏幕
        self.screen.fill((30, 30, 40))
        
        # 显示标题
        font = pygame.font.Font(None, 36)
        title = font.render("SceneWeaver 资源管理器演示", True, (255, 255, 255))
        self.screen.blit(title, (20, 20))
        
        # 显示操作说明
        instructions = [
            "空格键: 执行下一步演示",
            "ESC键: 退出演示",
            "",
            f"演示步骤: {self.demo_step + 1}/4",
            "1. 资源注册",
            "2. 资源加载", 
            "3. 缓存管理",
            "4. 资源列表"
        ]
        
        font_small = pygame.font.Font(None, 24)
        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, (200, 200, 200))
            self.screen.blit(text, (20, 80 + i * 30))
        
        # 显示统计信息
        stats_y = 350
        stats = [
            f"注册资源总数: {len(self.resource_manager.resources)}",
            f"缓存资源数: {len(self.resource_manager.resource_cache)}",
            f"缓存使用: {self.resource_manager.current_cache_size} bytes"
        ]
        
        for stat in stats:
            text = font_small.render(stat, True, (150, 200, 255))
            self.screen.blit(text, (20, stats_y))
            stats_y += 30
        
        # 更新显示
        pygame.display.flip()
    
    def run(self, duration=120):
        """运行演示"""
        if not self.initialize():
            print("演示初始化失败")
            return
        
        print("🌟 启动SceneWeaver资源管理器演示...")
        print("=" * 60)
        print("💡 操作说明:")
        print("   - 按空格键执行下一步演示")
        print("   - 按ESC键退出演示")
        print("   - 演示将持续到所有步骤完成")
        print("=" * 60)
        
        clock = pygame.time.Clock()
        start_time = time.time()
        
        try:
            # 自动执行第一步
            self.run_demo_step()
            
            while self.running and (time.time() - start_time) < duration:
                self.handle_events()
                self.render()
                clock.tick(60)
                
                # 显示进度
                elapsed = time.time() - start_time
                if int(elapsed) % 20 == 0 and elapsed > 0:
                    print(f"\r⏱️  演示进行中... ({elapsed:.0f}s/{duration}s)", end="", flush=True)
            
            print(f"\n✅ {duration}秒演示完成！")
            
        except KeyboardInterrupt:
            print("\n👋 演示被用户中断")
        except Exception as e:
            print(f"\n❌ 演示运行出错: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理资源"""
        # 清理资源管理器
        if self.resource_manager:
            ResourceManagerFactory.reset_instance()
        
        # 清理Pygame
        if self.screen:
            pygame.quit()
        
        # 清理临时目录
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            print(f"🗑️  清理临时目录: {self.temp_dir}")
        
        print("🔚 资源管理器演示已退出")


def main():
    """主函数"""
    demo = ResourceManagerDemo()
    demo.run(duration=120)  # 运行2分钟演示


if __name__ == "__main__":
    main()