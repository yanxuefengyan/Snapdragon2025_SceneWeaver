"""
Performance Monitor - 性能监控器
实时监控系统性能指标
"""

import time
import psutil
import logging
from collections import deque
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    fps: float = 0.0
    frame_time: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    gpu_usage: float = 0.0
    timestamp: float = 0.0


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化性能监控器
        
        Args:
            config: 性能配置
        """
        if config is None:
            config = {}
            
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 性能统计
        self.frame_times = deque(maxlen=60)  # 存储最近60帧的时间
        self.metrics_history = deque(maxlen=300)  # 存储历史指标
        
        # 当前指标
        self.current_metrics = PerformanceMetrics()
        self.last_update_time = time.time()
        
        # 监控开关
        self.enabled = config.get('enable_profiling', False)
        self.target_fps = config.get('target_fps', 60)
        
        self.logger.info("PerformanceMonitor初始化完成")
    
    def update(self, frame_time: float):
        """
        更新性能统计
        
        Args:
            frame_time: 当前帧耗时
        """
        if not self.enabled:
            return
        
        current_time = time.time()
        
        # 更新帧时间统计
        self.frame_times.append(frame_time)
        
        # 计算FPS
        if len(self.frame_times) >= 2:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        else:
            fps = 1.0 / frame_time if frame_time > 0 else 0
        
        # 获取系统资源使用情况
        cpu_percent = psutil.cpu_percent(interval=None)
        memory_info = psutil.virtual_memory()
        
        # 更新当前指标
        self.current_metrics = PerformanceMetrics(
            fps=fps,
            frame_time=frame_time,
            cpu_usage=cpu_percent,
            memory_usage=memory_info.percent,
            timestamp=current_time
        )
        
        # 添加到历史记录
        self.metrics_history.append(self.current_metrics)
        
        # 定期输出性能报告
        if current_time - self.last_update_time >= 5.0:  # 每5秒
            self._print_performance_report()
            self.last_update_time = current_time
    
    def _print_performance_report(self):
        """打印性能报告"""
        if not self.metrics_history:
            return
        
        # 计算平均指标
        avg_fps = sum(m.fps for m in self.metrics_history) / len(self.metrics_history)
        avg_frame_time = sum(m.frame_time for m in self.metrics_history) / len(self.metrics_history)
        avg_cpu = sum(m.cpu_usage for m in self.metrics_history) / len(self.metrics_history)
        avg_memory = sum(m.memory_usage for m in self.metrics_history) / len(self.metrics_history)
        
        # 性能评估
        fps_status = "✅" if avg_fps >= self.target_fps * 0.9 else "⚠️"
        cpu_status = "✅" if avg_cpu < 80 else "⚠️"
        memory_status = "✅" if avg_memory < 80 else "⚠️"
        
        report = f"""
📊 性能报告 (最近5秒平均值)
{'='*40}
帧率: {fps_status} {avg_fps:.1f} FPS (目标: {self.target_fps})
帧时间: {avg_frame_time*1000:.2f} ms
CPU使用率: {cpu_status} {avg_cpu:.1f}%
内存使用率: {memory_status} {avg_memory:.1f}%
{'='*40}
        """
        
        self.logger.info(report)
    
    def get_current_metrics(self) -> PerformanceMetrics:
        """
        获取当前性能指标
        
        Returns:
            PerformanceMetrics: 当前指标
        """
        return self.current_metrics
    
    def get_average_metrics(self, samples: int = 60) -> PerformanceMetrics:
        """
        获取平均性能指标
        
        Args:
            samples: 采样数量
            
        Returns:
            PerformanceMetrics: 平均指标
        """
        if not self.metrics_history:
            return PerformanceMetrics()
        
        recent_metrics = list(self.metrics_history)[-samples:]
        
        return PerformanceMetrics(
            fps=sum(m.fps for m in recent_metrics) / len(recent_metrics),
            frame_time=sum(m.frame_time for m in recent_metrics) / len(recent_metrics),
            cpu_usage=sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics),
            memory_usage=sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
        )
    
    def get_performance_warnings(self) -> List[str]:
        """
        获取性能警告
        
        Returns:
            List[str]: 警告信息列表
        """
        warnings = []
        metrics = self.get_current_metrics()
        
        if metrics.fps < self.target_fps * 0.7:
            warnings.append(f"帧率过低: {metrics.fps:.1f} FPS < {self.target_fps * 0.7} FPS")
        
        if metrics.cpu_usage > 90:
            warnings.append(f"CPU使用率过高: {metrics.cpu_usage:.1f}%")
        
        if metrics.memory_usage > 90:
            warnings.append(f"内存使用率过高: {metrics.memory_usage:.1f}%")
        
        return warnings
    
    def reset_statistics(self):
        """重置统计数据"""
        self.frame_times.clear()
        self.metrics_history.clear()
        self.current_metrics = PerformanceMetrics()
        self.last_update_time = time.time()
        self.logger.info("性能统计数据已重置")
    
    def export_metrics(self, filename: str = "performance_metrics.csv"):
        """
        导出性能指标到CSV文件
        
        Args:
            filename: 输出文件名
        """
        try:
            import csv
            from pathlib import Path
            
            filepath = Path(filename)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['timestamp', 'fps', 'frame_time', 'cpu_usage', 'memory_usage']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for metric in self.metrics_history:
                    writer.writerow({
                        'timestamp': metric.timestamp,
                        'fps': metric.fps,
                        'frame_time': metric.frame_time,
                        'cpu_usage': metric.cpu_usage,
                        'memory_usage': metric.memory_usage
                    })
            
            self.logger.info(f"性能数据已导出到: {filename}")
            
        except Exception as e:
            self.logger.error(f"导出性能数据失败: {e}")
    
    def cleanup(self):
        """清理性能监控器资源"""
        if self.enabled and self.metrics_history:
            self.export_metrics()
        self.logger.info("PerformanceMonitor资源清理完成")