"""
Plugin Market - 插件市场系统
SceneWeaver插件市场的在线管理模块
"""

import os
import json
import urllib.request
import urllib.parse
from typing import Dict, List, Any, Optional
from pathlib import Path
import hashlib
import zipfile
import logging
from dataclasses import dataclass, field
from datetime import datetime

from .plugin_manager import PluginInfo, PluginType

logger = logging.getLogger(__name__)


@dataclass
class MarketPluginInfo:
    """市场插件信息"""
    id: str
    name: str
    version: str
    author: str
    description: str
    plugin_type: PluginType
    download_url: str
    thumbnail_url: str = ""
    rating: float = 0.0
    download_count: int = 0
    last_updated: str = ""
    size: int = 0
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    compatibility: List[str] = field(default_factory=lambda: ["windows", "android", "ios", "web"])


class PluginMarket:
    """插件市场管理器"""
    
    def __init__(self, market_url: str = "https://plugins.scene-weaver.com/api"):
        self.market_url = market_url
        self.cache_dir = Path("cache/plugins")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # 缓存市场数据
        self._market_cache: Dict[str, MarketPluginInfo] = {}
        self._last_update = None
    
    def search_plugins(self, query: str = "", plugin_type: Optional[PluginType] = None,
                      tags: List[str] = None, sort_by: str = "rating") -> List[MarketPluginInfo]:
        """搜索插件"""
        try:
            # 构建查询参数
            params = {}
            if query:
                params['q'] = query
            if plugin_type:
                params['type'] = plugin_type.value
            if tags:
                params['tags'] = ','.join(tags)
            params['sort'] = sort_by
            
            # 发送请求
            url = f"{self.market_url}/search?{urllib.parse.urlencode(params)}"
            response = urllib.request.urlopen(url)
            data = json.loads(response.read().decode())
            
            # 解析结果
            plugins = []
            for item in data.get('plugins', []):
                plugin_info = self._parse_market_plugin_info(item)
                plugins.append(plugin_info)
                self._market_cache[plugin_info.id] = plugin_info
            
            self._last_update = datetime.now()
            self.logger.info(f"搜索到 {len(plugins)} 个插件")
            return plugins
            
        except Exception as e:
            self.logger.error(f"插件搜索失败: {e}")
            return []
    
    def get_plugin_details(self, plugin_id: str) -> Optional[MarketPluginInfo]:
        """获取插件详细信息"""
        # 先检查缓存
        if plugin_id in self._market_cache:
            return self._market_cache[plugin_id]
        
        try:
            # 从服务器获取
            url = f"{self.market_url}/plugins/{plugin_id}"
            response = urllib.request.urlopen(url)
            data = json.loads(response.read().decode())
            
            plugin_info = self._parse_market_plugin_info(data)
            self._market_cache[plugin_id] = plugin_info
            
            return plugin_info
            
        except Exception as e:
            self.logger.error(f"获取插件详情失败 {plugin_id}: {e}")
            return None
    
    def _parse_market_plugin_info(self, data: Dict[str, Any]) -> MarketPluginInfo:
        """解析市场插件信息"""
        return MarketPluginInfo(
            id=data['id'],
            name=data['name'],
            version=data['version'],
            author=data['author'],
            description=data['description'],
            plugin_type=PluginType(data['type']),
            download_url=data['download_url'],
            thumbnail_url=data.get('thumbnail_url', ''),
            rating=float(data.get('rating', 0)),
            download_count=int(data.get('download_count', 0)),
            last_updated=data.get('last_updated', ''),
            size=int(data.get('size', 0)),
            dependencies=data.get('dependencies', []),
            tags=data.get('tags', []),
            compatibility=data.get('compatibility', [])
        )
    
    def download_plugin(self, plugin_id: str, destination: str = None) -> bool:
        """下载插件"""
        try:
            plugin_info = self.get_plugin_details(plugin_id)
            if not plugin_info:
                self.logger.error(f"插件不存在: {plugin_id}")
                return False
            
            # 确定下载路径
            if destination is None:
                destination = str(self.cache_dir / f"{plugin_info.name}_{plugin_info.version}.zip")
            
            destination_path = Path(destination)
            
            # 检查缓存
            if self._is_cache_valid(plugin_info, destination_path):
                self.logger.info(f"使用缓存的插件文件: {destination}")
                return True
            
            # 下载文件
            self.logger.info(f"开始下载插件: {plugin_info.name} v{plugin_info.version}")
            
            # 创建临时文件
            temp_file = destination_path.with_suffix('.tmp')
            
            # 下载到临时文件
            urllib.request.urlretrieve(plugin_info.download_url, temp_file)
            
            # 验证文件完整性
            if not self._verify_download(temp_file, plugin_info):
                temp_file.unlink()
                self.logger.error("插件文件校验失败")
                return False
            
            # 重命名为正式文件
            if destination_path.exists():
                destination_path.unlink()
            temp_file.rename(destination_path)
            
            self.logger.info(f"插件下载完成: {destination}")
            return True
            
        except Exception as e:
            self.logger.error(f"插件下载失败 {plugin_id}: {e}")
            return False
    
    def _is_cache_valid(self, plugin_info: MarketPluginInfo, cache_file: Path) -> bool:
        """检查缓存文件是否有效"""
        if not cache_file.exists():
            return False
        
        # 检查文件大小
        if cache_file.stat().st_size != plugin_info.size:
            return False
        
        # 可以添加更多的校验逻辑
        return True
    
    def _verify_download(self, file_path: Path, plugin_info: MarketPluginInfo) -> bool:
        """验证下载文件的完整性"""
        try:
            # 检查文件大小
            if file_path.stat().st_size != plugin_info.size:
                return False
            
            # 可以添加MD5/SHA256校验
            # 这里简化处理
            return True
            
        except Exception as e:
            self.logger.error(f"文件校验失败: {e}")
            return False
    
    def install_plugin(self, plugin_id: str, extract_path: str = None) -> bool:
        """安装插件"""
        try:
            plugin_info = self.get_plugin_details(plugin_id)
            if not plugin_info:
                return False
            
            # 确定下载文件路径
            download_file = self.cache_dir / f"{plugin_info.name}_{plugin_info.version}.zip"
            
            # 下载插件（如果需要）
            if not download_file.exists():
                if not self.download_plugin(plugin_id, str(download_file)):
                    return False
            
            # 确定解压路径
            if extract_path is None:
                extract_path = f"plugins/{plugin_info.name}"
            
            extract_dir = Path(extract_path)
            extract_dir.mkdir(parents=True, exist_ok=True)
            
            # 解压插件
            self.logger.info(f"解压插件到: {extract_path}")
            with zipfile.ZipFile(download_file, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # 验证解压结果
            if not self._validate_plugin_structure(extract_dir):
                self.logger.error("插件结构验证失败")
                return False
            
            self.logger.info(f"插件安装成功: {plugin_info.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"插件安装失败 {plugin_id}: {e}")
            return False
    
    def _validate_plugin_structure(self, plugin_dir: Path) -> bool:
        """验证插件目录结构"""
        # 检查必需文件
        required_files = ['plugin.py', 'manifest.json']
        for file_name in required_files:
            if not (plugin_dir / file_name).exists():
                self.logger.error(f"缺少必需文件: {file_name}")
                return False
        
        # 检查manifest文件
        try:
            with open(plugin_dir / 'manifest.json', 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            required_fields = ['name', 'version', 'type']
            for field in required_fields:
                if field not in manifest:
                    self.logger.error(f"manifest缺少字段: {field}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"manifest文件读取失败: {e}")
            return False
        
        return True
    
    def get_featured_plugins(self, limit: int = 10) -> List[MarketPluginInfo]:
        """获取推荐插件"""
        return self.search_plugins(sort_by="featured")[:limit]
    
    def get_popular_plugins(self, limit: int = 10) -> List[MarketPluginInfo]:
        """获取热门插件"""
        return self.search_plugins(sort_by="downloads")[:limit]
    
    def get_new_plugins(self, limit: int = 10) -> List[MarketPluginInfo]:
        """获取最新插件"""
        return self.search_plugins(sort_by="updated")[:limit]
    
    def get_plugin_categories(self) -> List[str]:
        """获取插件分类"""
        categories = set()
        for plugin_info in self._market_cache.values():
            categories.add(plugin_info.plugin_type.value)
        return sorted(list(categories))
    
    def get_plugins_by_category(self, category: str) -> List[MarketPluginInfo]:
        """按分类获取插件"""
        plugins = []
        for plugin_info in self._market_cache.values():
            if plugin_info.plugin_type.value == category:
                plugins.append(plugin_info)
        return sorted(plugins, key=lambda x: x.rating, reverse=True)
    
    def submit_plugin_rating(self, plugin_id: str, rating: float, review: str = "") -> bool:
        """提交插件评分"""
        try:
            data = {
                'plugin_id': plugin_id,
                'rating': rating,
                'review': review
            }
            
            # 发送到服务器
            url = f"{self.market_url}/ratings"
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            
            if result.get('success'):
                self.logger.info(f"评分提交成功: {plugin_id}")
                return True
            else:
                self.logger.error(f"评分提交失败: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"评分提交异常: {e}")
            return False
    
    def get_user_ratings(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户评分记录"""
        try:
            url = f"{self.market_url}/users/{user_id}/ratings"
            response = urllib.request.urlopen(url)
            data = json.loads(response.read().decode())
            return data.get('ratings', [])
            
        except Exception as e:
            self.logger.error(f"获取用户评分失败: {e}")
            return []
    
    def cleanup_cache(self, max_age_days: int = 30):
        """清理缓存文件"""
        try:
            cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 3600)
            
            for cache_file in self.cache_dir.glob("*.zip"):
                if cache_file.stat().st_mtime < cutoff_time:
                    cache_file.unlink()
                    self.logger.info(f"清理缓存文件: {cache_file}")
            
            self.logger.info("缓存清理完成")
            
        except Exception as e:
            self.logger.error(f"缓存清理失败: {e}")


# 插件市场客户端工厂
class PluginMarketFactory:
    """插件市场客户端工厂"""
    
    @staticmethod
    def create_market_client(market_type: str = "official", **kwargs) -> PluginMarket:
        """创建插件市场客户端"""
        if market_type == "official":
            return PluginMarket(**kwargs)
        elif market_type == "local":
            return LocalPluginMarket(**kwargs)
        else:
            raise ValueError(f"不支持的市场类型: {market_type}")


class LocalPluginMarket(PluginMarket):
    """本地插件市场（用于开发测试）"""
    
    def __init__(self, local_path: str = "local_plugins"):
        super().__init__("http://localhost:8080/api")
        self.local_path = Path(local_path)
        self.local_path.mkdir(exist_ok=True)
    
    def search_plugins(self, query: str = "", plugin_type: PluginType = None,
                      tags: List[str] = None, sort_by: str = "rating") -> List[MarketPluginInfo]:
        """从本地目录搜索插件"""
        plugins = []
        
        for plugin_dir in self.local_path.iterdir():
            if plugin_dir.is_dir():
                try:
                    manifest_file = plugin_dir / "manifest.json"
                    if manifest_file.exists():
                        with open(manifest_file, 'r', encoding='utf-8') as f:
                            manifest = json.load(f)
                        
                        plugin_info = MarketPluginInfo(
                            id=plugin_dir.name,
                            name=manifest.get('name', plugin_dir.name),
                            version=manifest.get('version', '1.0.0'),
                            author=manifest.get('author', 'Unknown'),
                            description=manifest.get('description', ''),
                            plugin_type=PluginType(manifest.get('type', 'custom')),
                            download_url=f"file://{plugin_dir}",
                            size=sum(f.stat().st_size for f in plugin_dir.rglob('*') if f.is_file())
                        )
                        plugins.append(plugin_info)
                        
                except Exception as e:
                    logger.warning(f"解析本地插件失败 {plugin_dir}: {e}")
        
        return plugins