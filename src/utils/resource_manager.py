"""
Resource Manager - 资源管理系统
统一管理模型、纹理、音频等资源的加载、缓存和优化
"""

import os
import json
import hashlib
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import threading
from urllib.parse import urlparse
import requests
from concurrent.futures import ThreadPoolExecutor


class ResourceType(Enum):
    """资源类型枚举"""
    MODEL = "model"
    TEXTURE = "texture"
    AUDIO = "audio"
    SHADER = "shader"
    CONFIG = "config"


@dataclass
class ResourceMetadata:
    """资源元数据"""
    resource_id: str
    resource_type: ResourceType
    file_path: str
    file_hash: str = ""
    file_size: int = 0
    last_modified: float = 0.0
    version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CacheStrategy(Enum):
    """缓存策略"""
    LRU = "lru"  # 最近最少使用
    FIFO = "fifo"  # 先进先出
    SIZE_BASED = "size_based"  # 基于大小


class ResourceManager:
    """资源管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 资源存储路径
        self.resource_paths = {
            'models': config.get('model_path', './models'),
            'textures': config.get('texture_path', './assets/textures'),
            'audio': config.get('audio_path', './assets/audio'),
            'shaders': config.get('shader_path', './shaders'),
            'cache': config.get('cache_path', './cache')
        }
        
        # 资源注册表
        self.resources: Dict[str, ResourceMetadata] = {}
        self.resource_cache: Dict[str, Any] = {}
        
        # 缓存配置
        self.cache_strategy = CacheStrategy(config.get('cache_strategy', 'lru'))
        self.max_cache_size = config.get('max_cache_size_mb', 512) * 1024 * 1024  # 转换为字节
        self.current_cache_size = 0
        
        # 线程安全
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=4)
        
        # 网络资源下载
        self.download_timeout = config.get('download_timeout', 30)
        self.max_retries = config.get('max_retries', 3)
        
        self.logger.info("ResourceManager初始化完成")
    
    def initialize(self) -> bool:
        """初始化资源管理系统"""
        try:
            # 创建必要的目录
            self._create_resource_directories()
            
            # 加载现有资源索引
            self._load_resource_index()
            
            # 验证资源完整性
            self._verify_resources()
            
            self.logger.info("资源管理系统初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"资源管理系统初始化失败: {e}")
            return False
    
    def _create_resource_directories(self):
        """创建资源目录"""
        for path_key, path_value in self.resource_paths.items():
            path = Path(path_value)
            path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"创建资源目录: {path}")
    
    def _load_resource_index(self):
        """加载资源索引文件"""
        index_file = Path(self.resource_paths['cache']) / 'resource_index.json'
        
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                    
                for resource_id, metadata_dict in index_data.items():
                    metadata = ResourceMetadata(**metadata_dict)
                    self.resources[resource_id] = metadata
                    
                self.logger.info(f"加载了 {len(self.resources)} 个资源索引")
                
            except Exception as e:
                self.logger.warning(f"加载资源索引失败: {e}")
                self.resources = {}
        else:
            self.logger.info("未找到现有资源索引，将创建新的索引")
    
    def _verify_resources(self):
        """验证资源文件完整性"""
        verified_count = 0
        corrupted_count = 0
        
        for resource_id, metadata in self.resources.items():
            try:
                file_path = Path(metadata.file_path)
                if file_path.exists():
                    # 验证文件哈希
                    if metadata.file_hash:
                        current_hash = self._calculate_file_hash(file_path)
                        if current_hash == metadata.file_hash:
                            verified_count += 1
                        else:
                            self.logger.warning(f"资源哈希不匹配: {resource_id}")
                            corrupted_count += 1
                    else:
                        verified_count += 1
                else:
                    self.logger.warning(f"资源文件不存在: {resource_id}")
                    corrupted_count += 1
                    
            except Exception as e:
                self.logger.error(f"验证资源失败 {resource_id}: {e}")
                corrupted_count += 1
        
        self.logger.info(f"资源验证完成: {verified_count} 个正常, {corrupted_count} 个损坏")
    
    def register_resource(self, resource_id: str, resource_type: ResourceType, 
                         file_path: str, **kwargs) -> bool:
        """注册资源"""
        try:
            with self._lock:
                # 检查资源是否已存在
                if resource_id in self.resources:
                    self.logger.warning(f"资源已存在: {resource_id}")
                    return False
                
                # 创建资源元数据
                file_path_obj = Path(file_path)
                if not file_path_obj.exists():
                    self.logger.error(f"资源文件不存在: {file_path}")
                    return False
                
                metadata = ResourceMetadata(
                    resource_id=resource_id,
                    resource_type=resource_type,
                    file_path=str(file_path_obj.absolute()),
                    file_size=file_path_obj.stat().st_size,
                    last_modified=file_path_obj.stat().st_mtime,
                    **kwargs
                )
                
                # 计算文件哈希
                metadata.file_hash = self._calculate_file_hash(file_path_obj)
                
                # 添加到资源注册表
                self.resources[resource_id] = metadata
                
                # 保存索引
                self._save_resource_index()
                
                self.logger.info(f"注册资源成功: {resource_id} ({resource_type.value})")
                return True
                
        except Exception as e:
            self.logger.error(f"注册资源失败 {resource_id}: {e}")
            return False
    
    def load_resource(self, resource_id: str, force_reload: bool = False) -> Optional[Any]:
        """加载资源到内存"""
        try:
            # 检查缓存
            if not force_reload and resource_id in self.resource_cache:
                self.logger.debug(f"从缓存加载资源: {resource_id}")
                return self.resource_cache[resource_id]
            
            # 获取资源元数据
            if resource_id not in self.resources:
                self.logger.error(f"资源未注册: {resource_id}")
                return None
            
            metadata = self.resources[resource_id]
            
            # 加载资源
            resource_data = self._load_resource_data(metadata)
            if resource_data is None:
                return None
            
            # 添加到缓存
            with self._lock:
                self._add_to_cache(resource_id, resource_data, metadata.file_size)
            
            self.logger.info(f"加载资源成功: {resource_id}")
            return resource_data
            
        except Exception as e:
            self.logger.error(f"加载资源失败 {resource_id}: {e}")
            return None
    
    def _load_resource_data(self, metadata: ResourceMetadata) -> Optional[Any]:
        """根据资源类型加载数据"""
        file_path = Path(metadata.file_path)
        
        try:
            if metadata.resource_type == ResourceType.MODEL:
                return self._load_model(file_path)
            elif metadata.resource_type == ResourceType.TEXTURE:
                return self._load_texture(file_path)
            elif metadata.resource_type == ResourceType.AUDIO:
                return self._load_audio(file_path)
            elif metadata.resource_type == ResourceType.SHADER:
                return self._load_shader(file_path)
            elif metadata.resource_type == ResourceType.CONFIG:
                return self._load_config(file_path)
            else:
                # 通用二进制加载
                with open(file_path, 'rb') as f:
                    return f.read()
                    
        except Exception as e:
            self.logger.error(f"加载资源数据失败 {metadata.resource_id}: {e}")
            return None
    
    def _load_model(self, file_path: Path) -> Optional[Any]:
        """加载模型文件"""
        try:
            # 根据文件扩展名选择加载方式
            if file_path.suffix.lower() in ['.obj', '.ply']:
                # 网格模型
                return self._load_mesh_model(file_path)
            elif file_path.suffix.lower() in ['.fbx', '.glb', '.gltf']:
                # 3D模型格式
                return self._load_3d_model(file_path)
            else:
                # 通用模型加载
                with open(file_path, 'rb') as f:
                    return f.read()
        except Exception as e:
            self.logger.error(f"加载模型失败: {e}")
            return None
    
    def _load_texture(self, file_path: Path) -> Optional[Any]:
        """加载纹理文件"""
        try:
            import pygame
            # 使用Pygame加载图像
            return pygame.image.load(str(file_path))
        except ImportError:
            # 如果没有Pygame，返回文件路径
            return str(file_path)
        except Exception as e:
            self.logger.warning(f"Pygame加载纹理失败，返回文件路径: {e}")
            # Pygame加载失败时，返回文件路径作为后备方案
            return str(file_path)
    
    def _load_audio(self, file_path: Path) -> Optional[Any]:
        """加载音频文件"""
        try:
            # 返回文件路径，实际播放由音频系统处理
            return str(file_path)
        except Exception as e:
            self.logger.error(f"加载音频失败: {e}")
            return None
    
    def _load_shader(self, file_path: Path) -> Optional[str]:
        """加载着色器文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"加载着色器失败: {e}")
            return None
    
    def _load_config(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """加载配置文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() == '.json':
                    return json.load(f)
                elif file_path.suffix.lower() in ['.yml', '.yaml']:
                    import yaml
                    return yaml.safe_load(f)
                else:
                    return f.read()
        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
            return None
    
    def download_resource(self, url: str, resource_id: str, 
                         resource_type: ResourceType, **kwargs) -> bool:
        """下载网络资源"""
        try:
            # 解析URL获取文件名
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path) or f"{resource_id}_{int(time.time())}"
            
            # 确定保存路径
            resource_dir = Path(self.resource_paths[resource_type.value + 's'])
            file_path = resource_dir / filename
            
            # 下载文件
            self.logger.info(f"开始下载资源: {url} -> {file_path}")
            
            for attempt in range(self.max_retries):
                try:
                    response = requests.get(url, timeout=self.download_timeout, stream=True)
                    response.raise_for_status()
                    
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    self.logger.info(f"下载完成: {filename}")
                    break
                    
                except requests.RequestException as e:
                    if attempt < self.max_retries - 1:
                        self.logger.warning(f"下载失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                        continue
                    else:
                        raise e
            
            # 注册下载的资源
            return self.register_resource(resource_id, resource_type, str(file_path), **kwargs)
            
        except Exception as e:
            self.logger.error(f"下载资源失败 {resource_id}: {e}")
            return False
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.warning(f"计算文件哈希失败: {e}")
            return ""
    
    def _add_to_cache(self, resource_id: str, data: Any, size: int):
        """添加资源到缓存"""
        # 检查缓存大小限制
        if self.current_cache_size + size > self.max_cache_size:
            self._evict_cache_entries()
        
        self.resource_cache[resource_id] = data
        self.current_cache_size += size
        
        self.logger.debug(f"资源加入缓存: {resource_id}, 大小: {size} bytes")
    
    def _evict_cache_entries(self):
        """驱逐缓存条目"""
        if not self.resource_cache:
            return
        
        # 根据缓存策略驱逐
        if self.cache_strategy == CacheStrategy.LRU:
            # 移除最旧的条目（简单实现）
            oldest_key = next(iter(self.resource_cache))
            self._remove_from_cache(oldest_key)
        elif self.cache_strategy == CacheStrategy.SIZE_BASED:
            # 移除最大的条目
            largest_key = max(self.resource_cache.keys(), 
                            key=lambda k: self.resources[k].file_size if k in self.resources else 0)
            self._remove_from_cache(largest_key)
    
    def _remove_from_cache(self, resource_id: str):
        """从缓存中移除资源"""
        if resource_id in self.resource_cache:
            data = self.resource_cache.pop(resource_id)
            if resource_id in self.resources:
                self.current_cache_size -= self.resources[resource_id].file_size
            self.logger.debug(f"从缓存移除资源: {resource_id}")
    
    def get_resource_info(self, resource_id: str) -> Optional[ResourceMetadata]:
        """获取资源信息"""
        return self.resources.get(resource_id)
    
    def list_resources(self, resource_type: Optional[ResourceType] = None) -> List[str]:
        """列出资源"""
        if resource_type:
            return [rid for rid, meta in self.resources.items() 
                   if meta.resource_type == resource_type]
        else:
            return list(self.resources.keys())
    
    def _save_resource_index(self):
        """保存资源索引"""
        try:
            index_file = Path(self.resource_paths['cache']) / 'resource_index.json'
            
            # 转换为可序列化的字典
            index_data = {}
            for resource_id, metadata in self.resources.items():
                index_data[resource_id] = {
                    'resource_id': metadata.resource_id,
                    'resource_type': metadata.resource_type.value,
                    'file_path': metadata.file_path,
                    'file_hash': metadata.file_hash,
                    'file_size': metadata.file_size,
                    'last_modified': metadata.last_modified,
                    'version': metadata.version,
                    'dependencies': metadata.dependencies,
                    'metadata': metadata.metadata
                }
            
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"保存资源索引失败: {e}")
    
    def cleanup(self):
        """清理资源管理器"""
        try:
            # 保存索引
            self._save_resource_index()
            
            # 清理缓存
            self.resource_cache.clear()
            self.current_cache_size = 0
            
            # 关闭线程池
            self._executor.shutdown(wait=True)
            
            self.logger.info("ResourceManager资源清理完成")
            
        except Exception as e:
            self.logger.error(f"资源管理器清理失败: {e}")


# 资源管理器工厂类
class ResourceManagerFactory:
    """资源管理器工厂"""
    
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls, config: Dict[str, Any] = None) -> ResourceManager:
        """获取资源管理器单例实例"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = ResourceManager(config or {})
                    cls._instance.initialize()
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """重置单例实例"""
        with cls._lock:
            if cls._instance:
                cls._instance.cleanup()
            cls._instance = None