"""
File Input System - 文件输入系统
处理文件选择、拖拽上传、文件处理等功能
"""

import logging
import os
import json
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class FileType(Enum):
    """文件类型枚举"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    MODEL = "model"
    CONFIG = "config"
    TEXT = "text"
    ANY = "any"


class FileOperation(Enum):
    """文件操作枚举"""
    SELECT = "select"
    DROP = "drop"
    LOAD = "load"
    SAVE = "save"


@dataclass
class FileInfo:
    """文件信息数据类"""
    path: str
    name: str
    extension: str
    size: int  # bytes
    type: FileType
    mime_type: str = ""
    metadata: Dict[str, Any] = None


class FileFilter:
    """文件过滤器"""
    
    def __init__(self):
        self.filters = {
            FileType.IMAGE: ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'],
            FileType.VIDEO: ['.mp4', '.avi', '.mov', '.mkv', '.wmv'],
            FileType.AUDIO: ['.mp3', '.wav', '.ogg', '.flac', '.aac'],
            FileType.MODEL: ['.pt', '.pth', '.onnx', '.pb', '.h5'],
            FileType.CONFIG: ['.yaml', '.yml', '.json', '.ini', '.cfg'],
            FileType.TEXT: ['.txt', '.md', '.csv', '.xml']
        }
    
    def is_valid_file(self, file_path: str, file_type: FileType) -> bool:
        """检查文件是否符合指定类型"""
        if file_type == FileType.ANY:
            return True
            
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if file_type in self.filters:
            return extension in self.filters[file_type]
        return False
    
    def get_extensions_for_type(self, file_type: FileType) -> List[str]:
        """获取指定类型的文件扩展名"""
        return self.filters.get(file_type, [])


class FileDialog:
    """文件对话框"""
    
    def __init__(self, file_filter: FileFilter):
        self.file_filter = file_filter
        self.logger = logging.getLogger(__name__)
    
    def select_file(self, file_type: FileType = FileType.ANY, 
                   title: str = "选择文件") -> Optional[str]:
        """
        选择单个文件
        
        Args:
            file_type: 文件类型过滤器
            title: 对话框标题
            
        Returns:
            文件路径或None
        """
        try:
            # 尝试使用tkinter文件对话框
            import tkinter as tk
            from tkinter import filedialog
            
            # 隐藏主窗口
            root = tk.Tk()
            root.withdraw()
            
            # 构建文件类型过滤器
            filetypes = self._build_filetypes(file_type)
            
            # 打开文件选择对话框
            file_path = filedialog.askopenfilename(
                title=title,
                filetypes=filetypes
            )
            
            root.destroy()
            
            if file_path and self.file_filter.is_valid_file(file_path, file_type):
                self.logger.info(f"选择了文件: {file_path}")
                return file_path
            elif file_path:
                self.logger.warning(f"选择的文件不符合类型要求: {file_path}")
                return None
                
        except ImportError:
            self.logger.warning("tkinter不可用，使用控制台输入")
            return self._select_file_console(file_type)
        except Exception as e:
            self.logger.error(f"文件选择对话框出错: {e}")
            return None
    
    def select_multiple_files(self, file_type: FileType = FileType.ANY,
                            title: str = "选择多个文件") -> List[str]:
        """
        选择多个文件
        
        Args:
            file_type: 文件类型过滤器
            title: 对话框标题
            
        Returns:
            文件路径列表
        """
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            
            filetypes = self._build_filetypes(file_type)
            
            file_paths = filedialog.askopenfilenames(
                title=title,
                filetypes=filetypes
            )
            
            root.destroy()
            
            valid_files = [
                path for path in file_paths 
                if self.file_filter.is_valid_file(path, file_type)
            ]
            
            self.logger.info(f"选择了 {len(valid_files)} 个文件")
            return valid_files
            
        except ImportError:
            self.logger.warning("tkinter不可用，使用控制台输入")
            return self._select_multiple_files_console(file_type)
        except Exception as e:
            self.logger.error(f"多文件选择对话框出错: {e}")
            return []
    
    def select_directory(self, title: str = "选择目录") -> Optional[str]:
        """
        选择目录
        
        Args:
            title: 对话框标题
            
        Returns:
            目录路径或None
        """
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            
            dir_path = filedialog.askdirectory(title=title)
            root.destroy()
            
            if dir_path:
                self.logger.info(f"选择了目录: {dir_path}")
                return dir_path
                
        except ImportError:
            self.logger.warning("tkinter不可用，使用控制台输入")
            return self._select_directory_console()
        except Exception as e:
            self.logger.error(f"目录选择对话框出错: {e}")
            return None
    
    def save_file(self, file_type: FileType = FileType.ANY,
                 title: str = "保存文件", default_name: str = "") -> Optional[str]:
        """
        保存文件
        
        Args:
            file_type: 文件类型
            title: 对话框标题
            default_name: 默认文件名
            
        Returns:
            文件路径或None
        """
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            
            filetypes = self._build_filetypes(file_type)
            
            file_path = filedialog.asksaveasfilename(
                title=title,
                defaultextension=self._get_default_extension(file_type),
                filetypes=filetypes,
                initialfile=default_name
            )
            
            root.destroy()
            
            if file_path:
                self.logger.info(f"保存文件到: {file_path}")
                return file_path
                
        except ImportError:
            self.logger.warning("tkinter不可用，使用控制台输入")
            return self._save_file_console(file_type, default_name)
        except Exception as e:
            self.logger.error(f"保存文件对话框出错: {e}")
            return None
    
    def _build_filetypes(self, file_type: FileType) -> List[tuple]:
        """构建文件类型过滤器"""
        if file_type == FileType.ANY:
            return [("所有文件", "*.*")]
        
        extensions = self.file_filter.get_extensions_for_type(file_type)
        if extensions:
            ext_str = ";".join([f"*{ext}" for ext in extensions])
            type_name = file_type.value.capitalize()
            return [(f"{type_name}文件", ext_str), ("所有文件", "*.*")]
        else:
            return [("所有文件", "*.*")]
    
    def _get_default_extension(self, file_type: FileType) -> str:
        """获取默认文件扩展名"""
        extensions = self.file_filter.get_extensions_for_type(file_type)
        return extensions[0] if extensions else ""
    
    def _select_file_console(self, file_type: FileType) -> Optional[str]:
        """控制台文件选择"""
        print(f"\n=== 文件选择 ({file_type.value}) ===")
        print("请输入文件完整路径:")
        
        file_path = input().strip()
        if file_path and self.file_filter.is_valid_file(file_path, file_type):
            return file_path
        elif file_path:
            print("文件类型不匹配")
            return None
        return None
    
    def _select_multiple_files_console(self, file_type: FileType) -> List[str]:
        """控制台多文件选择"""
        print(f"\n=== 多文件选择 ({file_type.value}) ===")
        print("请输入文件路径，每行一个，输入空行结束:")
        
        files = []
        while True:
            file_path = input().strip()
            if not file_path:
                break
            if self.file_filter.is_valid_file(file_path, file_type):
                files.append(file_path)
            else:
                print(f"文件类型不匹配: {file_path}")
        
        return files
    
    def _select_directory_console(self) -> Optional[str]:
        """控制台目录选择"""
        print("\n=== 目录选择 ===")
        print("请输入目录路径:")
        
        dir_path = input().strip()
        if dir_path and os.path.isdir(dir_path):
            return dir_path
        return None
    
    def _save_file_console(self, file_type: FileType, default_name: str) -> Optional[str]:
        """控制台保存文件"""
        print(f"\n=== 保存文件 ({file_type.value}) ===")
        print(f"默认文件名: {default_name}")
        print("请输入保存路径:")
        
        file_path = input().strip()
        if file_path:
            return file_path
        return None


class FileProcessor:
    """文件处理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.processors = {}
        self._register_default_processors()
    
    def _register_default_processors(self):
        """注册默认文件处理器"""
        self.register_processor(FileType.IMAGE, self._process_image)
        self.register_processor(FileType.VIDEO, self._process_video)
        self.register_processor(FileType.AUDIO, self._process_audio)
        self.register_processor(FileType.CONFIG, self._process_config)
        self.register_processor(FileType.TEXT, self._process_text)
    
    def register_processor(self, file_type: FileType, processor: Callable):
        """注册文件处理器"""
        self.processors[file_type] = processor
    
    def process_file(self, file_info: FileInfo) -> Dict[str, Any]:
        """处理文件"""
        try:
            processor = self.processors.get(file_info.type)
            if processor:
                return processor(file_info)
            else:
                return self._process_generic(file_info)
        except Exception as e:
            self.logger.error(f"文件处理出错 {file_info.path}: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'file_info': file_info
            }
    
    def _process_image(self, file_info: FileInfo) -> Dict[str, Any]:
        """处理图像文件"""
        try:
            # 这里可以集成PIL/OpenCV等图像处理库
            result = {
                'status': 'success',
                'message': '图像文件处理完成',
                'file_info': file_info,
                'metadata': {
                    'processed': True,
                    'type': 'image'
                }
            }
            self.logger.info(f"图像处理完成: {file_info.name}")
            return result
        except Exception as e:
            return {
                'status': 'error',
                'message': f"图像处理失败: {e}",
                'file_info': file_info
            }
    
    def _process_video(self, file_info: FileInfo) -> Dict[str, Any]:
        """处理视频文件"""
        try:
            # 这里可以集成OpenCV等视频处理库
            result = {
                'status': 'success',
                'message': '视频文件处理完成',
                'file_info': file_info,
                'metadata': {
                    'processed': True,
                    'type': 'video'
                }
            }
            self.logger.info(f"视频处理完成: {file_info.name}")
            return result
        except Exception as e:
            return {
                'status': 'error',
                'message': f"视频处理失败: {e}",
                'file_info': file_info
            }
    
    def _process_audio(self, file_info: FileInfo) -> Dict[str, Any]:
        """处理音频文件"""
        try:
            result = {
                'status': 'success',
                'message': '音频文件处理完成',
                'file_info': file_info,
                'metadata': {
                    'processed': True,
                    'type': 'audio'
                }
            }
            self.logger.info(f"音频处理完成: {file_info.name}")
            return result
        except Exception as e:
            return {
                'status': 'error',
                'message': f"音频处理失败: {e}",
                'file_info': file_info
            }
    
    def _process_config(self, file_info: FileInfo) -> Dict[str, Any]:
        """处理配置文件"""
        try:
            # 读取配置文件内容
            with open(file_info.path, 'r', encoding='utf-8') as f:
                if file_info.extension in ['.json']:
                    config_data = json.load(f)
                else:
                    config_data = f.read()
            
            result = {
                'status': 'success',
                'message': '配置文件处理完成',
                'file_info': file_info,
                'metadata': {
                    'processed': True,
                    'type': 'config',
                    'config_data': config_data
                }
            }
            self.logger.info(f"配置处理完成: {file_info.name}")
            return result
        except Exception as e:
            return {
                'status': 'error',
                'message': f"配置处理失败: {e}",
                'file_info': file_info
            }
    
    def _process_text(self, file_info: FileInfo) -> Dict[str, Any]:
        """处理文本文件"""
        try:
            with open(file_info.path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = {
                'status': 'success',
                'message': '文本文件处理完成',
                'file_info': file_info,
                'metadata': {
                    'processed': True,
                    'type': 'text',
                    'content_length': len(content),
                    'preview': content[:100] + "..." if len(content) > 100 else content
                }
            }
            self.logger.info(f"文本处理完成: {file_info.name}")
            return result
        except Exception as e:
            return {
                'status': 'error',
                'message': f"文本处理失败: {e}",
                'file_info': file_info
            }
    
    def _process_generic(self, file_info: FileInfo) -> Dict[str, Any]:
        """通用文件处理"""
        result = {
            'status': 'success',
            'message': '文件已接收',
            'file_info': file_info,
            'metadata': {
                'processed': False,
                'type': 'generic'
            }
        }
        self.logger.info(f"通用文件处理: {file_info.name}")
        return result


class DragDropHandler:
    """拖拽处理"""
    
    def __init__(self):
        self.drop_targets = []
        self.logger = logging.getLogger(__name__)
    
    def add_drop_target(self, rect, callback: Callable):
        """添加拖拽目标区域"""
        self.drop_targets.append({
            'rect': rect,
            'callback': callback
        })
    
    def handle_drop(self, file_paths: List[str], drop_position: tuple):
        """处理文件拖拽"""
        for target in self.drop_targets:
            if self._point_in_rect(drop_position, target['rect']):
                try:
                    target['callback'](file_paths)
                    self.logger.info(f"文件拖拽到目标区域: {len(file_paths)} 个文件")
                    return True
                except Exception as e:
                    self.logger.error(f"拖拽处理出错: {e}")
        return False
    
    def _point_in_rect(self, point: tuple, rect) -> bool:
        """检查点是否在矩形内"""
        x, y = point
        if hasattr(rect, 'collidepoint'):
            return rect.collidepoint(x, y)
        else:
            # 假设rect是(x, y, width, height)格式
            rx, ry, rw, rh = rect
            return rx <= x <= rx + rw and ry <= y <= ry + rh


class FileInputSystem:
    """文件输入系统主类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.file_filter = FileFilter()
        self.file_dialog = FileDialog(self.file_filter)
        self.file_processor = FileProcessor()
        self.drag_drop_handler = DragDropHandler()
        
        # 回调函数
        self.callbacks = {}
        
        # 历史记录
        self.recent_files = []
        self.max_recent_files = config.get('max_recent_files', 10)
        
        self.logger.info("FileInputSystem初始化完成")
    
    def select_file(self, file_type: FileType = FileType.ANY, 
                   title: str = "选择文件") -> Optional[FileInfo]:
        """选择文件并返回文件信息"""
        file_path = self.file_dialog.select_file(file_type, title)
        if file_path:
            return self._create_file_info(file_path, file_type)
        return None
    
    def select_multiple_files(self, file_type: FileType = FileType.ANY,
                            title: str = "选择多个文件") -> List[FileInfo]:
        """选择多个文件"""
        file_paths = self.file_dialog.select_multiple_files(file_type, title)
        return [self._create_file_info(path, file_type) for path in file_paths]
    
    def select_directory(self, title: str = "选择目录") -> Optional[str]:
        """选择目录"""
        return self.file_dialog.select_directory(title)
    
    def save_file(self, file_type: FileType = FileType.ANY,
                 title: str = "保存文件", default_name: str = "") -> Optional[str]:
        """保存文件"""
        return self.file_dialog.save_file(file_type, title, default_name)
    
    def process_file(self, file_info: FileInfo) -> Dict[str, Any]:
        """处理文件"""
        result = self.file_processor.process_file(file_info)
        
        # 触发回调
        self._trigger_callback('file_processed', {
            'file_info': file_info,
            'result': result
        })
        
        # 添加到最近文件
        self._add_to_recent_files(file_info)
        
        return result
    
    def add_drop_target(self, rect, callback: Callable):
        """添加拖拽目标"""
        self.drag_drop_handler.add_drop_target(rect, callback)
    
    def handle_drag_drop(self, file_paths: List[str], drop_position: tuple) -> bool:
        """处理拖拽事件"""
        return self.drag_drop_handler.handle_drop(file_paths, drop_position)
    
    def _create_file_info(self, file_path: str, file_type: FileType) -> FileInfo:
        """创建文件信息对象"""
        path = Path(file_path)
        stat = path.stat()
        
        return FileInfo(
            path=str(path.absolute()),
            name=path.name,
            extension=path.suffix.lower(),
            size=stat.st_size,
            type=file_type,
            mime_type=self._get_mime_type(path.suffix.lower())
        )
    
    def _get_mime_type(self, extension: str) -> str:
        """获取MIME类型"""
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.yaml': 'application/yaml',
            '.yml': 'application/yaml',
            '.json': 'application/json'
        }
        return mime_types.get(extension, 'application/octet-stream')
    
    def _add_to_recent_files(self, file_info: FileInfo):
        """添加到最近文件"""
        # 移除重复项
        self.recent_files = [f for f in self.recent_files if f.path != file_info.path]
        
        # 添加到开头
        self.recent_files.insert(0, file_info)
        
        # 限制数量
        if len(self.recent_files) > self.max_recent_files:
            self.recent_files = self.recent_files[:self.max_recent_files]
    
    def get_recent_files(self) -> List[FileInfo]:
        """获取最近文件列表"""
        return self.recent_files.copy()
    
    def clear_recent_files(self):
        """清空最近文件列表"""
        self.recent_files.clear()
    
    def add_callback(self, event_type: str, callback: Callable):
        """添加事件回调"""
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        self.callbacks[event_type].append(callback)
    
    def _trigger_callback(self, event_type: str, data: Any):
        """触发回调"""
        if event_type in self.callbacks:
            for callback in self.callbacks[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"回调执行出错: {e}")
    
    def cleanup(self):
        """清理资源"""
        self.callbacks.clear()
        self.recent_files.clear()
        self.logger.info("FileInputSystem资源清理完成")