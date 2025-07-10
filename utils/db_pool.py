import sqlite3
import threading
from contextlib import contextmanager
from queue import Queue, Empty
import app_conf

class ConnectionPool:
    def __init__(self, database_path: str, max_connections: int = 10):
        self.database_path = database_path
        self.max_connections = max_connections
        self.pool = Queue(maxsize=max_connections)
        self.lock = threading.Lock()
        self._initialize_pool()
    
    def _initialize_pool(self):
        """初始化连接池"""
        for _ in range(self.max_connections):
            conn = sqlite3.connect(self.database_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row  # 允许按列名访问
            self.pool.put(conn)
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = None
        try:
            conn = self.pool.get(timeout=5)  # 5秒超时
            yield conn
        except Empty:
            raise Exception("无法获取数据库连接：连接池已满")
        finally:
            if conn:
                self.pool.put(conn)
    
    def close_all(self):
        """关闭所有连接"""
        while not self.pool.empty():
            try:
                conn = self.pool.get_nowait()
                conn.close()
            except Empty:
                break

# 全局连接池实例
_pool = None
_pool_lock = threading.Lock()

def get_pool():
    """获取全局连接池实例"""
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                conf = app_conf.conf()
                database_path = conf.get("database", "path")
                _pool = ConnectionPool(database_path)
    return _pool

def get_connection():
    """获取数据库连接"""
    return get_pool().get_connection()
