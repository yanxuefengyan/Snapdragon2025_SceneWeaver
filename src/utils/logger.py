"""
Logger - 日志系统配置
统一的日志管理工具
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Dict, Any


def setup_logger(config: Dict[str, Any] = None, level: int = logging.INFO):
    """
    设置全局日志配置
    
    Args:
        config: 日志配置字典
        level: 日志级别
    """
    if config is None:
        config = {}
    
    # 创建格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 清除现有处理器
    root_logger.handlers.clear()
    
    # 控制台处理器
    if config.get('console_output', True):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # 文件处理器
    log_file = config.get('file', 'scene_weaver.log')
    if log_file:
        try:
            # 确保日志目录存在
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 创建带轮转的文件处理器
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
            
        except Exception as e:
            print(f"警告: 无法创建文件日志处理器: {e}")


def get_logger(name: str) -> logging.Logger:
    """
    获取命名日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器实例
    """
    return logging.getLogger(name)


class LogMixin:
    """日志混入类，为其他类提供便捷的日志方法"""
    
    @property
    def logger(self):
        """获取类的日志记录器"""
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(
                f"{self.__class__.__module__}.{self.__class__.__name__}"
            )
        return self._logger
    
    def log_debug(self, message: str):
        """记录调试信息"""
        self.logger.debug(message)
    
    def log_info(self, message: str):
        """记录一般信息"""
        self.logger.info(message)
    
    def log_warning(self, message: str):
        """记录警告信息"""
        self.logger.warning(message)
    
    def log_error(self, message: str):
        """记录错误信息"""
        self.logger.error(message)
    
    def log_exception(self, message: str):
        """记录异常信息"""
        self.logger.exception(message)