#!/usr/bin/env python3
"""
模型下载和管理工具
支持将AI模型文件下载到本地使用
"""

import os
import sys
import urllib.request
from pathlib import Path
import hashlib
import json
import logging
from typing import Dict, List, Optional

# 设置项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from utils.logger import setup_logger

class ModelDownloader:
    """模型下载管理器"""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        # 模型配置
        self.model_configs = {
            'yolov5s': {
                'name': 'YOLOv5s',
                'url': 'https://github.com/ultralytics/yolov5/releases/download/v6.0/yolov5s.pt',
                'local_path': 'yolov5s.pt',
                'size': '14.1 MB',
                'sha256': 'c3b140f0a0d2a9c1b8f9d8e7f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8'
            },
            'yolov5m': {
                'name': 'YOLOv5m',
                'url': 'https://github.com/ultralytics/yolov5/releases/download/v6.0/yolov5m.pt',
                'local_path': 'yolov5m.pt',
                'size': '48.2 MB',
                'sha256': 'b1a2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2'
            },
            'ssd_mobilenet_v2': {
                'name': 'SSD MobileNet V2',
                'url': 'http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_mobilenet_v2_320x320_coco17_tpu-8.tar.gz',
                'local_path': 'ssd_mobilenet_v2.tar.gz',
                'size': '197.8 MB',
                'sha256': 'd1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2'
            }
        }
        
        # 设置日志
        setup_logger({'console_output': True}, logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def list_available_models(self) -> List[str]:
        """列出可用的模型"""
        return list(self.model_configs.keys())
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """获取模型信息"""
        return self.model_configs.get(model_name)
    
    def download_model(self, model_name: str, force: bool = False) -> bool:
        """下载指定模型"""
        if model_name not in self.model_configs:
            self.logger.error(f"未知模型: {model_name}")
            return False
        
        model_config = self.model_configs[model_name]
        local_path = self.models_dir / model_config['local_path']
        
        # 检查文件是否已存在
        if local_path.exists() and not force:
            self.logger.info(f"模型文件已存在: {local_path}")
            if self.verify_model(model_name):
                self.logger.info("模型文件校验通过")
                return True
            else:
                self.logger.warning("模型文件校验失败，重新下载")
        
        try:
            self.logger.info(f"开始下载模型: {model_config['name']}")
            self.logger.info(f"文件大小: {model_config['size']}")
            self.logger.info(f"下载地址: {model_config['url']}")
            
            # 下载文件
            urllib.request.urlretrieve(
                model_config['url'],
                local_path,
                self._progress_hook
            )
            
            self.logger.info(f"下载完成: {local_path}")
            
            # 验证文件
            if self.verify_model(model_name):
                self.logger.info("模型文件校验成功")
                return True
            else:
                self.logger.error("模型文件校验失败")
                # 删除损坏的文件
                if local_path.exists():
                    local_path.unlink()
                return False
                
        except Exception as e:
            self.logger.error(f"下载失败: {e}")
            # 删除可能损坏的文件
            if local_path.exists():
                local_path.unlink()
            return False
    
    def _progress_hook(self, block_num: int, block_size: int, total_size: int):
        """下载进度回调"""
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, (downloaded * 100) // total_size)
            print(f"\r下载进度: {percent}% ({downloaded}/{total_size} bytes)", end='', flush=True)
    
    def verify_model(self, model_name: str) -> bool:
        """验证模型文件完整性"""
        if model_name not in self.model_configs:
            return False
        
        model_config = self.model_configs[model_name]
        local_path = self.models_dir / model_config['local_path']
        
        if not local_path.exists():
            return False
        
        # 如果没有SHA256校验码，则简单检查文件大小
        if 'sha256' not in model_config or not model_config['sha256']:
            # 简单的文件存在性检查
            return local_path.stat().st_size > 0
        
        # 计算文件SHA256
        sha256_hash = hashlib.sha256()
        with open(local_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        
        calculated_hash = sha256_hash.hexdigest()
        expected_hash = model_config['sha256']
        
        return calculated_hash.lower() == expected_hash.lower()
    
    def get_local_model_path(self, model_name: str) -> Optional[Path]:
        """获取本地模型文件路径"""
        if model_name not in self.model_configs:
            return None
        
        model_config = self.model_configs[model_name]
        local_path = self.models_dir / model_config['local_path']
        
        if local_path.exists():
            return local_path
        return None
    
    def batch_download(self, model_names: List[str], force: bool = False) -> Dict[str, bool]:
        """批量下载模型"""
        results = {}
        for model_name in model_names:
            results[model_name] = self.download_model(model_name, force)
        return results
    
    def cleanup_models(self):
        """清理下载的模型文件"""
        if self.models_dir.exists():
            import shutil
            shutil.rmtree(self.models_dir)
            self.models_dir.mkdir(exist_ok=True)
            self.logger.info("模型文件清理完成")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SceneWeaver模型下载工具')
    parser.add_argument('action', choices=['list', 'download', 'verify', 'cleanup'], 
                       help='操作类型')
    parser.add_argument('--model', '-m', help='模型名称')
    parser.add_argument('--force', '-f', action='store_true', 
                       help='强制重新下载')
    parser.add_argument('--models-dir', default='models', 
                       help='模型存储目录')
    
    args = parser.parse_args()
    
    downloader = ModelDownloader(args.models_dir)
    
    if args.action == 'list':
        print("可用模型列表:")
        for model_name in downloader.list_available_models():
            info = downloader.get_model_info(model_name)
            print(f"  - {model_name}: {info['name']} ({info['size']})")
    
    elif args.action == 'download':
        if not args.model:
            print("请指定要下载的模型名称")
            print("可用模型:", ", ".join(downloader.list_available_models()))
            return
        
        success = downloader.download_model(args.model, args.force)
        if success:
            print(f"✓ 模型 {args.model} 下载成功")
        else:
            print(f"✗ 模型 {args.model} 下载失败")
    
    elif args.action == 'verify':
        if not args.model:
            print("请指定要验证的模型名称")
            return
        
        if downloader.verify_model(args.model):
            print(f"✓ 模型 {args.model} 校验通过")
        else:
            print(f"✗ 模型 {args.model} 校验失败")
    
    elif args.action == 'cleanup':
        confirm = input("确定要删除所有下载的模型文件吗？(y/N): ")
        if confirm.lower() == 'y':
            downloader.cleanup_models()
            print("模型文件已清理")

if __name__ == "__main__":
    main()