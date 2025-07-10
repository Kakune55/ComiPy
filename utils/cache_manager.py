"""
缓存管理器 - 用于图片和数据缓存
提供内存缓存和磁盘缓存功能
"""
import os
import hashlib
import json
import time
import threading
from pathlib import Path
from typing import Optional, Dict, Any
import pickle

from utils.logger import get_logger
import app_conf

logger = get_logger(__name__)
conf = app_conf.conf()


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: Optional[str] = None, max_memory_size: int = 100):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 磁盘缓存目录
            max_memory_size: 内存缓存最大条目数
        """
        self.cache_dir = Path(cache_dir or conf.get("file", "tmpdir")) / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.memory_cache = {}
        self.max_memory_size = max_memory_size
        self.cache_access_times = {}
        self.lock = threading.RLock()
        
        # 缓存统计
        self.stats = {
            'hits': 0,
            'misses': 0,
            'memory_hits': 0,
            'disk_hits': 0
        }
        
        logger.info(f"缓存管理器初始化: 目录={self.cache_dir}, 内存限制={max_memory_size}")
    
    def _generate_key(self, *args) -> str:
        """生成缓存键"""
        key_string = "_".join(str(arg) for arg in args)
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()
    
    def _cleanup_memory_cache(self):
        """清理内存缓存，移除最久未访问的项目"""
        if len(self.memory_cache) <= self.max_memory_size:
            return
        
        # 按访问时间排序，移除最旧的项目
        sorted_items = sorted(
            self.cache_access_times.items(),
            key=lambda x: x[1]
        )
        
        # 移除最旧的20%
        remove_count = len(self.memory_cache) - self.max_memory_size + 1
        for key, _ in sorted_items[:remove_count]:
            if key in self.memory_cache:
                del self.memory_cache[key]
                del self.cache_access_times[key]
        
        logger.debug(f"清理内存缓存: 移除 {remove_count} 项")
    
    def get(self, key: str, default=None) -> Any:
        """获取缓存数据"""
        with self.lock:
            current_time = time.time()
            
            # 检查内存缓存
            if key in self.memory_cache:
                self.cache_access_times[key] = current_time
                self.stats['hits'] += 1
                self.stats['memory_hits'] += 1
                logger.debug(f"内存缓存命中: {key}")
                return self.memory_cache[key]
            
            # 检查磁盘缓存
            cache_file = self.cache_dir / f"{key}.cache"
            if cache_file.exists():
                try:
                    with open(cache_file, 'rb') as f:
                        data = pickle.load(f)
                    
                    # 将数据加载到内存缓存
                    self.memory_cache[key] = data
                    self.cache_access_times[key] = current_time
                    self._cleanup_memory_cache()
                    
                    self.stats['hits'] += 1
                    self.stats['disk_hits'] += 1
                    logger.debug(f"磁盘缓存命中: {key}")
                    return data
                except Exception as e:
                    logger.error(f"读取磁盘缓存失败 {key}: {e}")
                    # 删除损坏的缓存文件
                    try:
                        cache_file.unlink()
                    except:
                        pass
            
            self.stats['misses'] += 1
            logger.debug(f"缓存未命中: {key}")
            return default
    
    def set(self, key: str, value: Any, disk_cache: bool = True):
        """设置缓存数据"""
        with self.lock:
            current_time = time.time()
            
            # 存储到内存缓存
            self.memory_cache[key] = value
            self.cache_access_times[key] = current_time
            self._cleanup_memory_cache()
            
            # 存储到磁盘缓存
            if disk_cache:
                try:
                    cache_file = self.cache_dir / f"{key}.cache"
                    with open(cache_file, 'wb') as f:
                        pickle.dump(value, f)
                    logger.debug(f"数据已缓存: {key}")
                except Exception as e:
                    logger.error(f"写入磁盘缓存失败 {key}: {e}")
    
    def delete(self, key: str):
        """删除缓存数据"""
        with self.lock:
            # 删除内存缓存
            if key in self.memory_cache:
                del self.memory_cache[key]
                del self.cache_access_times[key]
            
            # 删除磁盘缓存
            cache_file = self.cache_dir / f"{key}.cache"
            if cache_file.exists():
                try:
                    cache_file.unlink()
                    logger.debug(f"删除缓存: {key}")
                except Exception as e:
                    logger.error(f"删除磁盘缓存失败 {key}: {e}")
    
    def clear(self):
        """清空所有缓存"""
        with self.lock:
            # 清空内存缓存
            self.memory_cache.clear()
            self.cache_access_times.clear()
            
            # 清空磁盘缓存
            try:
                for cache_file in self.cache_dir.glob("*.cache"):
                    cache_file.unlink()
                logger.info("清空所有缓存")
            except Exception as e:
                logger.error(f"清空磁盘缓存失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'total_requests': total_requests,
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'hit_rate': f"{hit_rate:.2f}%",
                'memory_hits': self.stats['memory_hits'],
                'disk_hits': self.stats['disk_hits'],
                'memory_cache_size': len(self.memory_cache),
                'disk_cache_files': len(list(self.cache_dir.glob("*.cache")))
            }
    
    def cleanup_expired(self, max_age_hours: int = 24):
        """清理过期的磁盘缓存文件"""
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            removed_count = 0
            
            for cache_file in self.cache_dir.glob("*.cache"):
                if current_time - cache_file.stat().st_mtime > max_age_seconds:
                    cache_file.unlink()
                    removed_count += 1
            
            if removed_count > 0:
                logger.info(f"清理过期缓存文件: {removed_count} 个")
                
        except Exception as e:
            logger.error(f"清理过期缓存失败: {e}")


# 全局缓存管理器实例
_cache_manager = None


def get_cache_manager() -> CacheManager:
    """获取全局缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def cache_image(func):
    """图片缓存装饰器"""
    def wrapper(*args, **kwargs):
        cache_manager = get_cache_manager()
        
        # 生成缓存键
        cache_key = cache_manager._generate_key(func.__name__, *args, *kwargs.items())
        
        # 尝试从缓存获取
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # 执行函数并缓存结果
        result = func(*args, **kwargs)
        if result:  # 只缓存有效结果
            cache_manager.set(cache_key, result)
        
        return result
    
    return wrapper
