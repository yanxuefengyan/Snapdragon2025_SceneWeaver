import pygame
import logging
import time

class Renderer:
    """渲染器类"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.screen = None
        self.clock = None
        self.width = config.get('width', 1280)
        self.height = config.get('height', 720)
        self.fullscreen = config.get('fullscreen', False)
        
    def initialize(self):
        """初始化渲染器"""
        try:
            # 初始化 Pygame
            pygame.init()
            pygame.font.init()
            
            # 设置显示模式
            flags = pygame.DOUBLEBUF | pygame.HWSURFACE
            if self.fullscreen:
                flags |= pygame.FULLSCREEN
                
            self.screen = pygame.display.set_mode((self.width, self.height), flags)
            pygame.display.set_caption("SceneWeaver")
            
            # 创建时钟对象用于控制帧率
            self.clock = pygame.time.Clock()
            
            # 初始化一些效果参数
            self.effects = {
                'explosion': {'active': False, 'timer': 0},
                'smoke': {'active': False, 'timer': 0},
                'fire': {'active': False, 'timer': 0},
                'magic': {'active': False, 'timer': 0},
                'sparkle': {'active': False, 'timer': 0},
                'lighting_preset': {'active': False, 'timer': 0}
            }
            
            self.logger.info(f"渲染器初始化成功: {self.width}x{self.height}")
            return True
            
        except Exception as e:
            self.logger.error(f"渲染器初始化失败：{e}")
            return False
    
    def clear(self):
        """清除屏幕"""
        # 使用深色背景
        self.screen.fill((20, 20, 30))
    
    def update_camera(self, movement):
        """更新摄像机位置"""
        # 这里可以添加摄像机移动逻辑
        pass
    
    def render_scene(self):
        """渲染场景"""
        # 绘制一些基本的网格线作为参考
        width, height = self.screen.get_size()
        center_x, center_y = width // 2, height // 2
        
        # 绘制中心十字线
        pygame.draw.line(self.screen, (50, 50, 80), (center_x, 0), (center_x, height), 1)
        pygame.draw.line(self.screen, (50, 50, 80), (0, center_y), (width, center_y), 1)
        
        # 绘制网格
        grid_spacing = 50
        for x in range(0, width, grid_spacing):
            pygame.draw.line(self.screen, (30, 30, 50), (x, 0), (x, height), 1)
        for y in range(0, height, grid_spacing):
            pygame.draw.line(self.screen, (30, 30, 50), (0, y), (width, y), 1)
        
        # 显示提示信息
        font = pygame.font.Font(None, 24)
        text = font.render("SceneWeaver - 按数字键1-5触发特效，空格键切换灯光预设", True, (150, 150, 150))
        self.screen.blit(text, (10, 10))
        
        # 如果有激活的效果，可以在这里绘制
        active_effects = [k for k, v in self.effects.items() if v['active']]
        if active_effects:
            effect_text = font.render(f"特效: {', '.join(active_effects)}", True, (255, 255, 100))
            self.screen.blit(effect_text, (10, 40))
    
    def present(self):
        """更新显示"""
        # 控制帧率
        self.clock.tick(60)
        pygame.display.flip()
    
    def trigger_effect(self, effect_type, x=None, y=None):
        """触发改良效果"""
        if effect_type in self.effects:
            self.effects[effect_type]['active'] = not self.effects[effect_type]['active']
            self.effects[effect_type]['timer'] = 60  # 60帧持续时间
            print(f"触发效果: {effect_type} at {x}, {y}" if x and y else f"触发效果: {effect_type}")
    
    def cleanup(self):
        """清理资源"""
        if self.screen:
            pygame.display.quit()
        pygame.quit()
import logging
import pygame
import os

class CoreEngine:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.project_data = None
        
    def _load_project(self, file_path):
        """加载项目文件"""
        self.logger.info(f"加载项目: {file_path}")
        # TODO: 实现项目加载逻辑
        self.project_data = {"name": os.path.basename(file_path), "path": file_path}
        print(f"项目加载成功: {file_path}")
        
    def _save_project_to_path(self, file_path):
        """保存项目到指定路径"""
        self.logger.info(f"保存项目到: {file_path}")
        # TODO: 实现项目保存逻辑
        if not self.project_data:
            self.project_data = {"name": os.path.basename(file_path), "path": file_path}
        print(f"项目保存成功: {file_path}")
        
    def _on_file_open(self):
        """打开项目"""
        self.logger.info("文件 > 打开")
        
        # 方法 1: 使用 tkinter
        try:
            import os
            import tkinter as tk
            from tkinter import filedialog
            
            # 创建根窗口但不显示
            root = tk.Tk()
            root.withdraw()  # 隐藏窗口
            root.attributes('-topmost', True)  # 置顶
            root.update()  # 更新窗口事件
            
            # 打开文件对话框
            file_path = filedialog.askopenfilename(
                parent=root,
                title="打开项目",
                filetypes=[
                    ("SceneWeaver 项目", "*.swp"),
                    ("JSON 文件", "*.json"),
                    ("所有文件", "*.*")
                ],
                initialdir=os.path.expanduser("~")  # 初始目录为用户主目录
            )
            
            root.destroy()  # 确保窗口被销毁
            
            if file_path and os.path.exists(file_path):
                self._load_project(file_path)
                return
            else:
                self.logger.info("文件选择已取消")
                return
                
        except Exception as e:
            self.logger.warning(f"tkinter 对话框失败：{e}")
            try:
                root.destroy()
            except:
                pass
        
        # 方法 2: 使用 Pygame GUI 作为后备
        try:
            self.logger.info("使用 Pygame 文件选择器")
            # 这里可以实现一个简单的 Pygame 文件浏览器
            # 暂时使用控制台方式，但不阻塞主循环
            print("\n请选择文件路径 (或输入 q 取消):")
            # 注意：在实际应用中应该使用非阻塞输入方式
            # 这里为了演示，使用简单的输入处理
            import threading
            def get_user_input():
                file_path = input("> ")
                if file_path and file_path.lower() != 'q':
                    if os.path.exists(file_path):
                        self._load_project(file_path)
                    else:
                        print("文件不存在")
                else:
                    print("文件选择已取消")
            
            # 在新线程中获取输入，避免阻塞主循环
            threading.Thread(target=get_user_input, daemon=True).start()
            
        except Exception as e:
            self.logger.error(f"文件打开失败：{e}")
            print(f"错误：无法打开文件 - {e}")

    def _on_file_save_as(self):
        """另存为项目"""
        self.logger.info("文件 > 另存为")
        
        # 方法 1: 使用 tkinter
        try:
            import os
            import tkinter as tk
            from tkinter import filedialog
            import time
            
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            root.update()
            
            # 默认文件名
            default_name = "Untitled.swp"
            if hasattr(self, 'project_data') and 'name' in self.project_data:
                default_name = f"{self.project_data['name']}.swp"
            
            file_path = filedialog.asksaveasfilename(
                parent=root,
                title="另存为",
                defaultextension=".swp",
                initialfile=default_name,
                initialdir=os.path.expanduser("~"),
                filetypes=[
                    ("SceneWeaver 项目", "*.swp"),
                    ("JSON 文件", "*.json"),
                    ("所有文件", "*.*")
                ]
            )
            
            root.destroy()
            
            if file_path:

                # 确保目录存在
                directory = os.path.dirname(file_path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory)
                
                self._save_project_to_path(file_path)
                return
            else:
                self.logger.info("另存为已取消")
                return
                
        except Exception as e:
            self.logger.warning(f"tkinter 对话框失败：{e}")
            try:
                root.destroy()
            except:
                pass
        
        # 方法 2: 使用控制台输入
        try:
            print("\n请输入保存路径 (或输入 q 取消):")
            if hasattr(self, 'project_data') and 'name' in self.project_data:
                print(f"默认文件名：{self.project_data['name']}.swp")
            
            # 使用线程避免阻塞主循环
            import threading
            def get_save_path():
                file_path = input("> ")
                if file_path and file_path.lower() != 'q':
                    # 确保目录存在
                    directory = os.path.dirname(file_path)
                    if directory and not os.path.exists(directory):
                        try:
                            os.makedirs(directory)
                            self.logger.info(f"创建目录：{directory}")
                        except Exception as e:
                            print(f"无法创建目录：{e}")
                    
                    self._save_project_to_path(file_path)
                else:
                    print("保存已取消")
            
            threading.Thread(target=get_save_path, daemon=True).start()
            
        except Exception as e:
            self.logger.error(f"另存为失败：{e}")
            print(f"错误：另存为失败 - {e}")
    
    def run(self):
        """启动引擎主循环"""
        self.logger.info("启动引擎主循环")
        running = True
        
        while running:
            # 处理事件
            # TODO: 添加事件处理逻辑
            pass
            
            # 更新引擎状态
            # TODO: 添加状态更新逻辑
            pass
            
            # 渲染画面
            # TODO: 添加渲染逻辑
            pass
            
            # 控制帧率
            # TODO: 添加帧率控制逻辑
            pass
            
        self.logger.info("引擎主循环结束")