"""
性能监控模块
用于监控应用程序的性能指标
"""
import time
import threading
from functools import wraps
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PerformanceMetric:
    """性能指标数据类"""
    name: str
    start_time: float
    end_time: float = 0
    duration: float = 0
    memory_before: float = 0
    memory_after: float = 0
    success: bool = True
    error_message: str = ""


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.lock = threading.Lock()
        
    def start_monitoring(self, name: str) -> PerformanceMetric:
        """开始监控一个操作"""
        metric = PerformanceMetric(
            name=name,
            start_time=time.time(),
            memory_before=self.get_memory_usage()
        )
        return metric
    
    def end_monitoring(self, metric: PerformanceMetric, success: bool = True, error_message: str = ""):
        """结束监控操作"""
        metric.end_time = time.time()
        metric.duration = metric.end_time - metric.start_time
        metric.memory_after = self.get_memory_usage()
        metric.success = success
        metric.error_message = error_message
        
        with self.lock:
            self.metrics.append(metric)
            
            # 保持最近1000条记录
            if len(self.metrics) > 1000:
                self.metrics = self.metrics[-1000:]
        
        logger.debug(f"性能监控: {metric.name} - 耗时: {metric.duration:.3f}s, "
                    f"内存变化: {metric.memory_after - metric.memory_before:.2f}MB")
    
    def get_memory_usage(self) -> float:
        """获取当前内存使用量(MB)"""
        try:
            # 简单的内存使用量估算
            # 在Windows上，可以使用其他方法，这里先返回0
            return 0.0
        except:
            return 0.0
    
    def get_stats(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """获取性能统计信息"""
        with self.lock:
            filtered_metrics = self.metrics
            if operation_name:
                filtered_metrics = [m for m in self.metrics if m.name == operation_name]
            
            if not filtered_metrics:
                return {}
            
            durations = [m.duration for m in filtered_metrics if m.success]
            success_count = len([m for m in filtered_metrics if m.success])
            error_count = len([m for m in filtered_metrics if not m.success])
            
            stats = {
                'operation_name': operation_name or 'All Operations',
                'total_calls': len(filtered_metrics),
                'success_calls': success_count,
                'error_calls': error_count,
                'success_rate': f"{(success_count / len(filtered_metrics) * 100):.2f}%" if filtered_metrics else "0%",
                'avg_duration': f"{(sum(durations) / len(durations)):.3f}s" if durations else "0s",
                'min_duration': f"{min(durations):.3f}s" if durations else "0s",
                'max_duration': f"{max(durations):.3f}s" if durations else "0s",
                'current_memory': f"{self.get_memory_usage():.2f}MB"
            }
            
            return stats
    
    def get_recent_errors(self, count: int = 10) -> List[Dict[str, Any]]:
        """获取最近的错误"""
        with self.lock:
            error_metrics = [m for m in self.metrics if not m.success][-count:]
            return [
                {
                    'name': m.name,
                    'time': datetime.fromtimestamp(m.start_time).strftime('%Y-%m-%d %H:%M:%S'),
                    'duration': f"{m.duration:.3f}s",
                    'error': m.error_message
                }
                for m in error_metrics
            ]
    
    def clear_metrics(self):
        """清空监控数据"""
        with self.lock:
            self.metrics.clear()
            logger.info("清空性能监控数据")


# 全局性能监控器
_performance_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """获取全局性能监控器实例"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def monitor_performance(operation_name: Optional[str] = None):
    """性能监控装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            name = operation_name or f"{func.__module__}.{func.__name__}"
            
            metric = monitor.start_monitoring(name)
            try:
                result = func(*args, **kwargs)
                monitor.end_monitoring(metric, success=True)
                return result
            except Exception as e:
                monitor.end_monitoring(metric, success=False, error_message=str(e))
                raise
        return wrapper
    return decorator


def timing_context(operation_name: str):
    """性能监控上下文管理器"""
    class TimingContext:
        def __init__(self, name: str):
            self.name = name
            self.monitor = get_performance_monitor()
            self.metric: Optional[PerformanceMetric] = None
        
        def __enter__(self):
            self.metric = self.monitor.start_monitoring(self.name)
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.metric:
                if exc_type is None:
                    self.monitor.end_monitoring(self.metric, success=True)
                else:
                    self.monitor.end_monitoring(self.metric, success=False, error_message=str(exc_val))
    
    return TimingContext(operation_name)
