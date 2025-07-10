import logging
import sys
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app=None, log_level=logging.INFO):
    """
    设置应用程序的日志记录
    """
    # 创建logs目录
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 文件处理器 - 应用日志
    file_handler = RotatingFileHandler(
        'logs/app.log', 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # 错误日志处理器
    error_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    
    # 如果是Flask应用，也配置Flask的日志
    if app:
        app.logger.addHandler(file_handler)
        app.logger.addHandler(error_handler)
        app.logger.setLevel(log_level)
    
    return logging.getLogger(__name__)

def get_logger(name):
    """获取指定名称的日志记录器"""
    return logging.getLogger(name)
