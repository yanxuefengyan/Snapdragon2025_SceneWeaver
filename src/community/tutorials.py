"""
Tutorials and Documentation System - 教程文档系统
SceneWeaver在线教程和帮助文档管理系统
"""

import os
import json
import urllib.request
import urllib.parse
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Tutorial:
    """教程数据类"""
    id: str
    title: str
    description: str
    author: str
    category: str
    difficulty: str  # beginner, intermediate, advanced
    estimated_time: int  # minutes
    created_time: str
    updated_time: str
    content: str = ""
    video_url: str = ""
    thumbnail_url: str = ""
    tags: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    completion_rate: float = 0.0
    rating: float = 0.0
    view_count: int = 0


@dataclass
class DocumentationPage:
    """文档页面数据类"""
    id: str
    title: str
    content: str
    category: str
    version: str
    last_updated: str
    toc: List[Dict[str, Any]] = field(default_factory=list)  # table of contents
    related_pages: List[str] = field(default_factory=list)


@dataclass
class UserProgress:
    """用户学习进度"""
    user_id: str
    tutorial_id: str
    progress: float = 0.0  # 0.0 - 1.0
    completed: bool = False
    last_accessed: str = ""
    time_spent: int = 0  # seconds


class TutorialSystem:
    """教程管理系统"""
    
    def __init__(self, api_url: str = "https://learn.scene-weaver.com/api"):
        self.api_url = api_url
        self.cache_dir = Path("cache/tutorials")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # 用户进度跟踪
        self.user_progress: Dict[str, UserProgress] = {}
        self.progress_file = self.cache_dir / "user_progress.json"
        self._load_user_progress()
    
    def _load_user_progress(self):
        """加载用户进度数据"""
        try:
            if self.progress_file.exists():
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        progress = UserProgress(**item)
                        self.user_progress[progress.tutorial_id] = progress
        except Exception as e:
            self.logger.warning(f"加载用户进度失败: {e}")
    
    def _save_user_progress(self):
        """保存用户进度数据"""
        try:
            data = [vars(progress) for progress in self.user_progress.values()]
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存用户进度失败: {e}")
    
    def get_tutorials(self, category: str = None, difficulty: str = None,
                     limit: int = 50) -> List[Tutorial]:
        """获取教程列表"""
        try:
            params = {'limit': limit}
            if category:
                params['category'] = category
            if difficulty:
                params['difficulty'] = difficulty
            
            url = f"{self.api_url}/tutorials?{urllib.parse.urlencode(params)}"
            response = urllib.request.urlopen(url)
            data = json.loads(response.read().decode())
            
            tutorials = []
            for item in data.get('tutorials', []):
                tutorial = self._parse_tutorial(item)
                tutorials.append(tutorial)
            
            self.logger.info(f"获取到 {len(tutorials)} 个教程")
            return tutorials
            
        except Exception as e:
            self.logger.error(f"获取教程失败: {e}")
            return []
    
    def _parse_tutorial(self, data: Dict[str, Any]) -> Tutorial:
        """解析教程数据"""
        # 确保必要字段存在
        now_iso = datetime.now().isoformat()
        
        return Tutorial(
            id=data.get('id', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            author=data.get('author', ''),
            category=data.get('category', ''),
            difficulty=data.get('difficulty', 'beginner'),
            estimated_time=data.get('estimated_time', 30),
            created_time=data.get('created_time', now_iso),
            updated_time=data.get('updated_time', now_iso),
            content=data.get('content', ''),
            video_url=data.get('video_url', ''),
            thumbnail_url=data.get('thumbnail_url', ''),
            tags=data.get('tags', []),
            prerequisites=data.get('prerequisites', []),
            completion_rate=float(data.get('completion_rate', 0)),
            rating=float(data.get('rating', 0)),
            view_count=int(data.get('view_count', 0))
        )
    
    def get_tutorial(self, tutorial_id: str) -> Optional[Tutorial]:
        """获取单个教程详情"""
        try:
            # 先检查缓存
            cache_file = self.cache_dir / f"tutorial_{tutorial_id}.json"
            if cache_file.exists():
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        return self._parse_tutorial(data)
                except Exception as e:
                    self.logger.warning(f"缓存文件读取失败: {e}")
            
            # 从服务器获取
            url = f"{self.api_url}/tutorials/{tutorial_id}"
            response = urllib.request.urlopen(url)
            data = json.loads(response.read().decode())
            
            if data.get('success'):
                tutorial = self._parse_tutorial(data['tutorial'])
                
                # 缓存到本地
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(data['tutorial'], f, indent=2, ensure_ascii=False)
                
                return tutorial
            else:
                self.logger.error(f"获取教程失败: {data.get('error')}")
                return None
                
        except Exception as e:
            self.logger.error(f"获取教程异常 {tutorial_id}: {e}")
            return None
    
    def search_tutorials(self, query: str, category: str = None) -> List[Tutorial]:
        """搜索教程"""
        try:
            params = {'q': query}
            if category:
                params['category'] = category
            
            url = f"{self.api_url}/tutorials/search?{urllib.parse.urlencode(params)}"
            response = urllib.request.urlopen(url)
            data = json.loads(response.read().decode())
            
            tutorials = []
            for item in data.get('results', []):
                tutorials.append(self._parse_tutorial(item))
            
            return tutorials
            
        except Exception as e:
            self.logger.error(f"教程搜索失败: {e}")
            return []
    
    def get_categories(self) -> List[str]:
        """获取教程分类"""
        try:
            url = f"{self.api_url}/tutorials/categories"
            response = urllib.request.urlopen(url)
            data = json.loads(response.read().decode())
            return data.get('categories', [])
        except Exception as e:
            self.logger.error(f"获取分类失败: {e}")
            return []
    
    def get_difficulty_levels(self) -> List[str]:
        """获取难度等级"""
        return ['beginner', 'intermediate', 'advanced']
    
    def update_progress(self, tutorial_id: str, progress: float, 
                       time_spent: int = 0) -> bool:
        """更新学习进度"""
        try:
            # 更新内存中的进度
            if tutorial_id in self.user_progress:
                user_progress = self.user_progress[tutorial_id]
                user_progress.progress = progress
                user_progress.completed = progress >= 1.0
                user_progress.time_spent += time_spent
                user_progress.last_accessed = datetime.now().isoformat()
            else:
                user_progress = UserProgress(
                    user_id="current_user",  # 实际应用中应该是真实的用户ID
                    tutorial_id=tutorial_id,
                    progress=progress,
                    completed=progress >= 1.0,
                    last_accessed=datetime.now().isoformat(),
                    time_spent=time_spent
                )
                self.user_progress[tutorial_id] = user_progress
            
            # 保存到文件
            self._save_user_progress()
            
            # 发送到服务器（如果已登录）
            # 这里可以添加同步到云端的逻辑
            
            self.logger.info(f"进度更新成功: {tutorial_id} - {progress:.2%}")
            return True
            
        except Exception as e:
            self.logger.error(f"进度更新失败: {e}")
            return False
    
    def get_user_progress(self, tutorial_id: str) -> Optional[UserProgress]:
        """获取用户学习进度"""
        return self.user_progress.get(tutorial_id)
    
    def get_completed_tutorials(self) -> List[str]:
        """获取已完成的教程列表"""
        return [tid for tid, progress in self.user_progress.items() 
                if progress.completed]
    
    def get_recommended_tutorials(self, limit: int = 5) -> List[Tutorial]:
        """获取推荐教程"""
        try:
            # 基于用户历史和流行度推荐
            completed_ids = set(self.get_completed_tutorials())
            
            # 获取热门教程
            popular_tutorials = self.get_tutorials(limit=limit * 2)
            
            # 过滤掉已完成的教程
            recommended = [t for t in popular_tutorials 
                          if t.id not in completed_ids][:limit]
            
            return recommended
            
        except Exception as e:
            self.logger.error(f"获取推荐失败: {e}")
            return []
    
    def rate_tutorial(self, tutorial_id: str, rating: float, 
                     comment: str = "") -> bool:
        """评价教程"""
        try:
            data = {
                'tutorial_id': tutorial_id,
                'rating': rating,
                'comment': comment
            }
            
            url = f"{self.api_url}/tutorials/{tutorial_id}/rate"
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            
            if result.get('success'):
                self.logger.info("教程评价成功")
                return True
            else:
                self.logger.error(f"教程评价失败: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"教程评价异常: {e}")
            return False
    
    def get_tutorial_statistics(self, tutorial_id: str) -> Dict[str, Any]:
        """获取教程统计数据"""
        try:
            url = f"{self.api_url}/tutorials/{tutorial_id}/stats"
            response = urllib.request.urlopen(url)
            data = json.loads(response.read().decode())
            return data.get('statistics', {})
        except Exception as e:
            self.logger.error(f"获取统计失败: {e}")
            return {}


class DocumentationSystem:
    """文档管理系统"""
    
    def __init__(self, api_url: str = "https://docs.scene-weaver.com/api"):
        self.api_url = api_url
        self.cache_dir = Path("cache/docs")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def get_documentation_tree(self) -> Dict[str, Any]:
        """获取文档树结构"""
        try:
            cache_file = self.cache_dir / "doc_tree.json"
            
            # 检查缓存
            if cache_file.exists():
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    self.logger.warning(f"文档树缓存读取失败: {e}")
            
            # 从服务器获取
            url = f"{self.api_url}/docs/tree"
            response = urllib.request.urlopen(url)
            data = json.loads(response.read().decode())
            
            # 缓存到本地
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return data
            
        except Exception as e:
            self.logger.error(f"获取文档树失败: {e}")
            return {}
    
    def get_page(self, page_id: str) -> Optional[DocumentationPage]:
        """获取文档页面"""
        try:
            # 检查缓存
            cache_file = self.cache_dir / f"page_{page_id}.json"
            if cache_file.exists():
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        return self._parse_doc_page(data)
                except Exception as e:
                    self.logger.warning(f"页面缓存读取失败: {e}")
            
            # 从服务器获取
            url = f"{self.api_url}/docs/pages/{page_id}"
            response = urllib.request.urlopen(url)
            data = json.loads(response.read().decode())
            
            if data.get('success'):
                page = self._parse_doc_page(data['page'])
                
                # 缓存到本地
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(data['page'], f, indent=2, ensure_ascii=False)
                
                return page
            else:
                self.logger.error(f"获取页面失败: {data.get('error')}")
                return None
                
        except Exception as e:
            self.logger.error(f"获取页面异常 {page_id}: {e}")
            return None
    
    def _parse_doc_page(self, data: Dict[str, Any]) -> DocumentationPage:
        """解析文档页面数据"""
        return DocumentationPage(
            id=data['id'],
            title=data['title'],
            content=data['content'],
            category=data['category'],
            version=data['version'],
            last_updated=data['last_updated'],
            toc=data.get('toc', []),
            related_pages=data.get('related_pages', [])
        )
    
    def search_documentation(self, query: str) -> List[Dict[str, Any]]:
        """搜索文档"""
        try:
            params = {'q': query}
            url = f"{self.api_url}/docs/search?{urllib.parse.urlencode(params)}"
            response = urllib.request.urlopen(url)
            data = json.loads(response.read().decode())
            return data.get('results', [])
        except Exception as e:
            self.logger.error(f"文档搜索失败: {e}")
            return []
    
    def get_recent_updates(self, limit: int = 10) -> List[DocumentationPage]:
        """获取最近更新的文档"""
        try:
            url = f"{self.api_url}/docs/recent?limit={limit}"
            response = urllib.request.urlopen(url)
            data = json.loads(response.read().decode())
            
            pages = []
            for item in data.get('pages', []):
                pages.append(self._parse_doc_page(item))
            
            return pages
            
        except Exception as e:
            self.logger.error(f"获取更新失败: {e}")
            return []


# 本地教程系统（用于开发测试）
class LocalTutorialSystem(TutorialSystem):
    """本地教程系统"""
    
    def __init__(self, local_path: str = "local_tutorials"):
        super().__init__("http://localhost:8080/api")
        self.local_path = Path(local_path)
        self.local_path.mkdir(exist_ok=True)
        
        # 初始化示例教程
        self._init_sample_tutorials()
    
    def _init_sample_tutorials(self):
        """初始化示例教程"""
        now_iso = datetime.now().isoformat()
        
        sample_tutorials = [
            {
                'id': 'intro_basics',
                'title': 'SceneWeaver基础入门',
                'description': '学习SceneWeaver的基本操作和核心概念',
                'author': '官方教程',
                'category': 'basics',
                'difficulty': 'beginner',
                'estimated_time': 30,
                'created_time': now_iso,
                'updated_time': now_iso,
                'content': '# SceneWeaver基础入门\n\n欢迎来到SceneWeaver世界！...',
                'tags': ['入门', '基础', '新手']
            },
            {
                'id': 'advanced_rendering',
                'title': '高级渲染技巧',
                'description': '掌握专业的渲染技术和效果制作',
                'author': '高级用户',
                'category': 'rendering',
                'difficulty': 'advanced',
                'estimated_time': 60,
                'created_time': now_iso,
                'updated_time': now_iso,
                'content': '# 高级渲染技巧\n\n本教程将带你深入了解...',
                'tags': ['渲染', '高级', '专业']
            }
        ]
        
        # 保存示例教程
        tutorials_file = self.local_path / "tutorials.json"
        with open(tutorials_file, 'w', encoding='utf-8') as f:
            json.dump(sample_tutorials, f, indent=2, ensure_ascii=False)
    
    def get_tutorials(self, category: str = None, difficulty: str = None,
                     limit: int = 50) -> List[Tutorial]:
        """获取本地教程"""
        try:
            tutorials_file = self.local_path / "tutorials.json"
            if not tutorials_file.exists():
                return []
            
            with open(tutorials_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            tutorials = []
            for item in data:
                tutorial = self._parse_tutorial(item)
                if category and tutorial.category != category:
                    continue
                if difficulty and tutorial.difficulty != difficulty:
                    continue
                tutorials.append(tutorial)
            
            return tutorials[:limit]
            
        except Exception as e:
            self.logger.error(f"获取本地教程失败: {e}")
            return []


# 教程系统工厂
class TutorialSystemFactory:
    """教程系统工厂"""
    
    @staticmethod
    def create_tutorial_system(system_type: str = "online", **kwargs) -> TutorialSystem:
        """创建教程系统实例"""
        if system_type == "online":
            return TutorialSystem(**kwargs)
        elif system_type == "local":
            return LocalTutorialSystem(**kwargs)
        else:
            raise ValueError(f"不支持的系统类型: {system_type}")
    
    @staticmethod
    def create_documentation_system(system_type: str = "online", **kwargs) -> DocumentationSystem:
        """创建文档系统实例"""
        if system_type == "online":
            return DocumentationSystem(**kwargs)
        elif system_type == "local":
            # 可以实现本地文档系统
            return DocumentationSystem(**kwargs)
        else:
            raise ValueError(f"不支持的系统类型: {system_type}")