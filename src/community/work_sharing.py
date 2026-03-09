"""
Work Sharing Platform - 作品分享平台
SceneWeaver用户作品分享和协作系统
"""

import os
import json
import hashlib
import urllib.request
import urllib.parse
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class WorkMetadata:
    """作品元数据"""
    id: str
    title: str
    description: str
    author: str
    author_id: str
    created_time: str
    updated_time: str
    tags: List[str] = field(default_factory=list)
    thumbnail_url: str = ""
    download_count: int = 0
    like_count: int = 0
    view_count: int = 0
    file_size: int = 0
    version: str = "1.0.0"
    visibility: str = "public"  # public, private, unlisted
    license: str = "CC-BY-4.0"


@dataclass
class Comment:
    """评论数据"""
    id: str
    work_id: str
    author: str
    author_id: str
    content: str
    created_time: str
    parent_id: Optional[str] = None


@dataclass
class CollaborationRequest:
    """协作请求"""
    id: str
    work_id: str
    requester_id: str
    requester_name: str
    message: str
    status: str = "pending"  # pending, accepted, rejected
    created_time: str = ""


class WorkSharingPlatform:
    """作品分享平台"""
    
    def __init__(self, api_url: str = "https://share.scene-weaver.com/api"):
        self.api_url = api_url
        self.cache_dir = Path("cache/works")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # 用户认证信息
        self.user_token = None
        self.user_info = None
    
    def authenticate(self, username: str, password: str) -> bool:
        """用户认证"""
        try:
            data = {
                'username': username,
                'password': password
            }
            
            url = f"{self.api_url}/auth/login"
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            
            if result.get('success'):
                self.user_token = result['token']
                self.user_info = result['user']
                self.logger.info(f"用户认证成功: {username}")
                return True
            else:
                self.logger.error(f"认证失败: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"认证异常: {e}")
            return False
    
    def register_user(self, username: str, email: str, password: str) -> bool:
        """用户注册"""
        try:
            data = {
                'username': username,
                'email': email,
                'password': password
            }
            
            url = f"{self.api_url}/auth/register"
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            
            if result.get('success'):
                self.logger.info(f"用户注册成功: {username}")
                return True
            else:
                self.logger.error(f"注册失败: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"注册异常: {e}")
            return False
    
    def upload_work(self, work_path: str, metadata: WorkMetadata) -> Optional[str]:
        """上传作品"""
        try:
            work_file = Path(work_path)
            if not work_file.exists():
                self.logger.error(f"作品文件不存在: {work_path}")
                return None
            
            # 更新元数据
            metadata.file_size = work_file.stat().st_size
            metadata.updated_time = datetime.now().isoformat()
            
            # 准备上传数据
            boundary = '----SceneWeaverBoundary'
            body = self._create_multipart_body(boundary, metadata, work_file)
            
            # 发送请求
            url = f"{self.api_url}/works/upload"
            req = urllib.request.Request(
                url,
                data=body,
                headers={
                    'Content-Type': f'multipart/form-data; boundary={boundary}',
                    'Authorization': f'Bearer {self.user_token}'
                }
            )
            
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            
            if result.get('success'):
                work_id = result['work_id']
                self.logger.info(f"作品上传成功: {work_id}")
                return work_id
            else:
                self.logger.error(f"作品上传失败: {result.get('error')}")
                return None
                
        except Exception as e:
            self.logger.error(f"作品上传异常: {e}")
            return None
    
    def _create_multipart_body(self, boundary: str, metadata: WorkMetadata, 
                              work_file: Path) -> bytes:
        """创建multipart表单数据"""
        body_parts = []
        
        # 添加元数据
        metadata_json = json.dumps({
            'title': metadata.title,
            'description': metadata.description,
            'tags': metadata.tags,
            'visibility': metadata.visibility,
            'license': metadata.license,
            'version': metadata.version
        })
        
        body_parts.append(f'--{boundary}\r\n'.encode())
        body_parts.append('Content-Disposition: form-data; name="metadata"\r\n'.encode())
        body_parts.append('Content-Type: application/json\r\n\r\n'.encode())
        body_parts.append(metadata_json.encode())
        body_parts.append('\r\n'.encode())
        
        # 添加文件
        body_parts.append(f'--{boundary}\r\n'.encode())
        body_parts.append(f'Content-Disposition: form-data; name="file"; filename="{work_file.name}"\r\n'.encode())
        body_parts.append('Content-Type: application/octet-stream\r\n\r\n'.encode())
        
        with open(work_file, 'rb') as f:
            body_parts.append(f.read())
        
        body_parts.append('\r\n'.encode())
        body_parts.append(f'--{boundary}--\r\n'.encode())
        
        return b''.join(body_parts)
    
    def download_work(self, work_id: str, destination: str = None) -> bool:
        """下载作品"""
        try:
            # 确定保存路径
            if destination is None:
                destination = str(self.cache_dir / f"work_{work_id}")
            
            destination_path = Path(destination)
            
            # 检查缓存
            if self._is_work_cached(work_id, destination_path):
                self.logger.info(f"使用缓存的作品文件: {destination}")
                return True
            
            # 下载作品
            url = f"{self.api_url}/works/{work_id}/download"
            req = urllib.request.Request(
                url,
                headers={'Authorization': f'Bearer {self.user_token}'}
            )
            
            # 创建临时文件
            temp_file = destination_path.with_suffix('.tmp')
            
            # 下载到临时文件
            urllib.request.urlretrieve(url, temp_file)
            
            # 重命名为正式文件
            if destination_path.exists():
                destination_path.unlink()
            temp_file.rename(destination_path)
            
            # 更新浏览次数
            self._increment_view_count(work_id)
            
            self.logger.info(f"作品下载成功: {work_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"作品下载失败 {work_id}: {e}")
            return False
    
    def _is_work_cached(self, work_id: str, cache_file: Path) -> bool:
        """检查作品是否已缓存"""
        if not cache_file.exists():
            return False
        
        # 可以添加更复杂的缓存验证逻辑
        return True
    
    def _increment_view_count(self, work_id: str):
        """增加浏览次数"""
        try:
            url = f"{self.api_url}/works/{work_id}/view"
            req = urllib.request.Request(
                url,
                method='POST',
                headers={'Authorization': f'Bearer {self.user_token}'}
            )
            urllib.request.urlopen(req)
        except Exception as e:
            self.logger.debug(f"更新浏览次数失败: {e}")
    
    def search_works(self, query: str = "", tags: List[str] = None,
                    sort_by: str = "created_time", limit: int = 20) -> List[WorkMetadata]:
        """搜索作品"""
        try:
            params = {'limit': limit, 'sort': sort_by}
            if query:
                params['q'] = query
            if tags:
                params['tags'] = ','.join(tags)
            
            url = f"{self.api_url}/works/search?{urllib.parse.urlencode(params)}"
            response = urllib.request.urlopen(url)
            data = json.loads(response.read().decode())
            
            works = []
            for item in data.get('works', []):
                work_metadata = self._parse_work_metadata(item)
                works.append(work_metadata)
            
            self.logger.info(f"搜索到 {len(works)} 个作品")
            return works
            
        except Exception as e:
            self.logger.error(f"作品搜索失败: {e}")
            return []
    
    def _parse_work_metadata(self, data: Dict[str, Any]) -> WorkMetadata:
        """解析作品元数据"""
        return WorkMetadata(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            author=data['author'],
            author_id=data['author_id'],
            created_time=data['created_time'],
            updated_time=data['updated_time'],
            tags=data.get('tags', []),
            thumbnail_url=data.get('thumbnail_url', ''),
            download_count=data.get('download_count', 0),
            like_count=data.get('like_count', 0),
            view_count=data.get('view_count', 0),
            file_size=data.get('file_size', 0),
            version=data.get('version', '1.0.0'),
            visibility=data.get('visibility', 'public'),
            license=data.get('license', 'CC-BY-4.0')
        )
    
    def get_work_details(self, work_id: str) -> Optional[WorkMetadata]:
        """获取作品详细信息"""
        try:
            url = f"{self.api_url}/works/{work_id}"
            response = urllib.request.urlopen(url)
            data = json.loads(response.read().decode())
            
            if data.get('success'):
                return self._parse_work_metadata(data['work'])
            else:
                self.logger.error(f"获取作品详情失败: {data.get('error')}")
                return None
                
        except Exception as e:
            self.logger.error(f"获取作品详情异常 {work_id}: {e}")
            return None
    
    def get_user_works(self, user_id: str = None) -> List[WorkMetadata]:
        """获取用户作品"""
        try:
            if user_id is None and self.user_info:
                user_id = self.user_info['id']
            
            url = f"{self.api_url}/users/{user_id}/works"
            response = urllib.request.urlopen(url)
            data = json.loads(response.read().decode())
            
            works = []
            for item in data.get('works', []):
                works.append(self._parse_work_metadata(item))
            
            return works
            
        except Exception as e:
            self.logger.error(f"获取用户作品失败: {e}")
            return []
    
    def add_comment(self, work_id: str, content: str, parent_id: str = None) -> bool:
        """添加评论"""
        try:
            data = {
                'work_id': work_id,
                'content': content
            }
            if parent_id:
                data['parent_id'] = parent_id
            
            url = f"{self.api_url}/comments"
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.user_token}'
                }
            )
            
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            
            if result.get('success'):
                self.logger.info("评论添加成功")
                return True
            else:
                self.logger.error(f"评论添加失败: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"评论添加异常: {e}")
            return False
    
    def get_comments(self, work_id: str) -> List[Comment]:
        """获取作品评论"""
        try:
            url = f"{self.api_url}/works/{work_id}/comments"
            response = urllib.request.urlopen(url)
            data = json.loads(response.read().decode())
            
            comments = []
            for item in data.get('comments', []):
                comment = Comment(
                    id=item['id'],
                    work_id=item['work_id'],
                    author=item['author'],
                    author_id=item['author_id'],
                    content=item['content'],
                    created_time=item['created_time'],
                    parent_id=item.get('parent_id')
                )
                comments.append(comment)
            
            return comments
            
        except Exception as e:
            self.logger.error(f"获取评论失败: {e}")
            return []
    
    def like_work(self, work_id: str) -> bool:
        """点赞作品"""
        try:
            url = f"{self.api_url}/works/{work_id}/like"
            req = urllib.request.Request(
                url,
                method='POST',
                headers={'Authorization': f'Bearer {self.user_token}'}
            )
            
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            
            if result.get('success'):
                self.logger.info("点赞成功")
                return True
            else:
                self.logger.error(f"点赞失败: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"点赞异常: {e}")
            return False
    
    def send_collaboration_request(self, work_id: str, message: str) -> bool:
        """发送协作请求"""
        try:
            data = {
                'work_id': work_id,
                'message': message
            }
            
            url = f"{self.api_url}/collaboration/request"
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.user_token}'
                }
            )
            
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            
            if result.get('success'):
                self.logger.info("协作请求发送成功")
                return True
            else:
                self.logger.error(f"协作请求发送失败: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"协作请求发送异常: {e}")
            return False
    
    def get_collaboration_requests(self) -> List[CollaborationRequest]:
        """获取协作请求"""
        try:
            url = f"{self.api_url}/collaboration/requests"
            req = urllib.request.Request(
                url,
                headers={'Authorization': f'Bearer {self.user_token}'}
            )
            
            response = urllib.request.urlopen(req)
            data = json.loads(response.read().decode())
            
            requests = []
            for item in data.get('requests', []):
                request = CollaborationRequest(
                    id=item['id'],
                    work_id=item['work_id'],
                    requester_id=item['requester_id'],
                    requester_name=item['requester_name'],
                    message=item['message'],
                    status=item['status'],
                    created_time=item['created_time']
                )
                requests.append(request)
            
            return requests
            
        except Exception as e:
            self.logger.error(f"获取协作请求失败: {e}")
            return []
    
    def respond_collaboration_request(self, request_id: str, accept: bool) -> bool:
        """回应协作请求"""
        try:
            data = {
                'request_id': request_id,
                'accept': accept
            }
            
            url = f"{self.api_url}/collaboration/respond"
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.user_token}'
                }
            )
            
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            
            if result.get('success'):
                status = "接受" if accept else "拒绝"
                self.logger.info(f"协作请求已{status}")
                return True
            else:
                self.logger.error(f"回应协作请求失败: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"回应协作请求异常: {e}")
            return False
    
    def get_popular_works(self, limit: int = 10) -> List[WorkMetadata]:
        """获取热门作品"""
        return self.search_works(sort_by="like_count", limit=limit)
    
    def get_latest_works(self, limit: int = 10) -> List[WorkMetadata]:
        """获取最新作品"""
        return self.search_works(sort_by="created_time", limit=limit)
    
    def get_featured_works(self, limit: int = 10) -> List[WorkMetadata]:
        """获取推荐作品"""
        return self.search_works(sort_by="featured", limit=limit)
    
    def cleanup_cache(self, max_age_days: int = 7):
        """清理缓存文件"""
        try:
            cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 3600)
            
            for cache_file in self.cache_dir.glob("*"):
                if cache_file.stat().st_mtime < cutoff_time:
                    cache_file.unlink()
                    self.logger.info(f"清理缓存文件: {cache_file}")
            
            self.logger.info("作品缓存清理完成")
            
        except Exception as e:
            self.logger.error(f"缓存清理失败: {e}")


# 本地作品分享（用于开发测试）
class LocalWorkSharing(WorkSharingPlatform):
    """本地作品分享平台"""
    
    def __init__(self, local_path: str = "local_works"):
        super().__init__("http://localhost:8080/api")
        self.local_path = Path(local_path)
        self.local_path.mkdir(exist_ok=True)
        self.works_db = self.local_path / "works.json"
        
        # 初始化本地数据库
        if not self.works_db.exists():
            self._init_local_db()
    
    def _init_local_db(self):
        """初始化本地数据库"""
        db_data = {
            'works': [],
            'users': [],
            'comments': []
        }
        with open(self.works_db, 'w', encoding='utf-8') as f:
            json.dump(db_data, f, indent=2, ensure_ascii=False)
    
    def authenticate(self, username: str, password: str) -> bool:
        """本地认证"""
        # 简化的本地认证
        self.user_token = "local_token"
        self.user_info = {'id': 'local_user', 'username': username}
        return True
    
    def upload_work(self, work_path: str, metadata: WorkMetadata) -> Optional[str]:
        """本地上传"""
        try:
            work_file = Path(work_path)
            if not work_file.exists():
                return None
            
            # 生成作品ID
            work_id = f"local_{hashlib.md5(work_file.name.encode()).hexdigest()[:8]}"
            
            # 复制文件到本地存储
            dest_path = self.local_path / f"{work_id}_{work_file.name}"
            import shutil
            shutil.copy2(work_file, dest_path)
            
            # 更新数据库
            self._add_work_to_db(work_id, metadata, str(dest_path))
            
            return work_id
            
        except Exception as e:
            self.logger.error(f"本地上传失败: {e}")
            return None
    
    def _add_work_to_db(self, work_id: str, metadata: WorkMetadata, file_path: str):
        """添加作品到本地数据库"""
        try:
            with open(self.works_db, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
            
            work_record = {
                'id': work_id,
                'title': metadata.title,
                'description': metadata.description,
                'author': metadata.author,
                'author_id': metadata.author_id or 'local_user',
                'created_time': metadata.created_time,
                'updated_time': metadata.updated_time,
                'tags': metadata.tags,
                'file_path': file_path,
                'download_count': 0,
                'like_count': 0,
                'view_count': 0
            }
            
            db_data['works'].append(work_record)
            
            with open(self.works_db, 'w', encoding='utf-8') as f:
                json.dump(db_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"数据库更新失败: {e}")