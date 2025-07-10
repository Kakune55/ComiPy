import shutil, os, zipfile, io, cv2, numpy as np
import hashlib
import time
from functools import lru_cache
from pathlib import Path
import logging

import db.file, app_conf
from utils.logger import get_logger
from utils.cache_manager import get_cache_manager, cache_image
from utils.performance_monitor import monitor_performance, timing_context

# 获取配置对象
conf = app_conf.conf()
logger = get_logger(__name__)
cache_manager = get_cache_manager()

# 内存缓存 - 存储最近访问的ZIP文件列表
_zip_cache = {}
_cache_timeout = 300  # 5分钟缓存超时


def init():
    """初始化文件目录"""
    paths = ("inputdir", "storedir", "tmpdir")
    for path in paths:
        try:
            dir_path = Path(conf.get("file", path))
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建目录: {dir_path}")
        except Exception as e:
            logger.error(f"创建目录失败 {path}: {e}")


@monitor_performance("file.get_image_files_from_zip")
def get_image_files_from_zip(zip_path: str) -> tuple:
    """
    从ZIP文件中获取图片文件列表，使用缓存提高性能
    返回: (image_files_list, cache_key)
    """
    cache_key = f"{zip_path}_{os.path.getmtime(zip_path)}"
    current_time = time.time()
    
    # 检查缓存
    if cache_key in _zip_cache:
        cache_data = _zip_cache[cache_key]
        if current_time - cache_data['timestamp'] < _cache_timeout:
            logger.debug(f"使用缓存的ZIP文件列表: {zip_path}")
            return cache_data['files'], cache_key
    
    # 读取ZIP文件
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            image_files = [
                file for file in zip_ref.namelist()
                if file.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"))
            ]
            
            # 缓存结果
            _zip_cache[cache_key] = {
                'files': image_files,
                'timestamp': current_time
            }
            
            # 清理过期缓存
            _cleanup_cache()
            
            logger.debug(f"缓存ZIP文件列表: {zip_path}, 图片数量: {len(image_files)}")
            return image_files, cache_key
            
    except Exception as e:
        logger.error(f"读取ZIP文件失败 {zip_path}: {e}")
        return [], cache_key


def _cleanup_cache():
    """清理过期缓存"""
    current_time = time.time()
    expired_keys = [
        key for key, data in _zip_cache.items()
        if current_time - data['timestamp'] > _cache_timeout
    ]
    for key in expired_keys:
        del _zip_cache[key]
    
    if expired_keys:
        logger.debug(f"清理过期缓存: {len(expired_keys)} 项")


@monitor_performance("file.autoLoadFile")
def autoLoadFile():
    """自动加载文件，优化路径处理和错误处理"""
    input_dir = Path(conf.get("file", "inputdir"))
    store_dir = Path(conf.get("file", "storedir"))
    
    if not input_dir.exists():
        logger.warning(f"输入目录不存在: {input_dir}")
        return
    
    file_list = []
    try:
        file_list = [f for f in input_dir.iterdir() if f.is_file()]
    except Exception as e:
        logger.error(f"读取输入目录失败: {e}")
        return
    
    processed_count = 0
    for file_path in file_list:
        try:
            if zipfile.is_zipfile(file_path):
                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    page_count = len([f for f in zip_ref.namelist() 
                                    if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"))])
                    if page_count > 0:
                        db.file.new(file_path.name, page_count)
                        
                        # 移动文件到存储目录
                        target_path = store_dir / file_path.name
                        shutil.move(str(file_path), str(target_path))
                        
                        logger.info(f"已添加漫画: {file_path.name}, 页数: {page_count}")
                        processed_count += 1
                    else:
                        logger.warning(f"ZIP文件中没有图片: {file_path.name}")
            else:
                logger.info(f"非ZIP文件，跳过: {file_path.name}")
        except Exception as e:
            logger.error(f"处理文件失败 {file_path.name}: {e}")
    
    logger.info(f"自动加载完成，处理了 {processed_count} 个文件")


@monitor_performance("file.readZip")
def readZip(bookid: str, index: int) -> tuple:
    """
    从ZIP文件中读取指定索引的图片
    优化：使用缓存的文件列表，改进错误处理
    返回: (image_data, filename) 或 (error_message, "")
    """
    try:
        bookinfo = db.file.searchByid(bookid)
        if not bookinfo:
            logger.warning(f"未找到书籍ID: {bookid}")
            return "Book not found", ""
        
        zip_path = Path(conf.get("file", "storedir")) / bookinfo[0][2]
        
        if not zip_path.exists():
            logger.error(f"ZIP文件不存在: {zip_path}")
            return "ZIP file not found", ""
        
        # 使用缓存获取图片文件列表
        image_files, _ = get_image_files_from_zip(str(zip_path))
        
        if not image_files:
            logger.warning(f"ZIP文件中没有图片: {zip_path}")
            return "No image files in zip", ""
        
        if int(index) >= len(image_files):
            logger.warning(f"图片索引超出范围: {index}, 总数: {len(image_files)}")
            return "Image index out of range", ""
        
        # 读取指定图片
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            image_filename = image_files[int(index)]
            image_data = zip_ref.read(image_filename)
            
            logger.debug(f"读取图片: {bookid}/{index} -> {image_filename}")
            return image_data, image_filename
            
    except zipfile.BadZipFile:
        logger.error(f"损坏的ZIP文件: {bookid}")
        return "Bad ZipFile", ""
    except Exception as e:
        logger.error(f"读取ZIP文件失败 {bookid}/{index}: {e}")
        return f"Error: {str(e)}", ""


@lru_cache(maxsize=128)
def _get_image_hash(image_data: bytes) -> str:
    """生成图片数据的哈希值用于缓存"""
    return hashlib.md5(image_data).hexdigest()


@cache_image
def thumbnail(input_data: bytes, min_size: int = 600, encode: str = "webp", quality: int = 75) -> bytes:
    """
    生成缩略图，优化编码逻辑和性能
    """
    if not input_data:
        logger.warning("输入图片数据为空")
        return input_data
    
    try:
        # 解码图片
        img = cv2.imdecode(np.frombuffer(input_data, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            logger.warning("无法解码图片数据")
            return input_data
        
        height, width = img.shape[:2]
        logger.debug(f"原始图片尺寸: {width}x{height}")
        
        # 判断是否需要缩放
        min_dimension = min(height, width)
        if min_size < min_dimension:
            # 计算新尺寸
            if height > width:
                new_width = min_size
                new_height = int(min_size * height / width)
            else:
                new_height = min_size
                new_width = int(min_size * width / height)
            
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            logger.debug(f"缩放后图片尺寸: {new_width}x{new_height}")
        
        # 编码图片
        if encode.lower() == "webp":
            success, encoded_image = cv2.imencode(
                ".webp", img, [cv2.IMWRITE_WEBP_QUALITY, quality]
            )
        elif encode.lower() in ("jpg", "jpeg"):
            success, encoded_image = cv2.imencode(
                ".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality]
            )
        elif encode.lower() == "png":
            success, encoded_image = cv2.imencode(
                ".png", img, [cv2.IMWRITE_PNG_COMPRESSION, 6]
            )
        else:
            logger.warning(f"不支持的编码格式: {encode}, 返回原始数据")
            return input_data
        
        if not success:
            logger.error(f"图片编码失败: {encode}")
            return input_data
        
        result = encoded_image.tobytes()
        logger.debug(f"图片处理完成: 原始 {len(input_data)} bytes -> 处理后 {len(result)} bytes")
        return result
        
    except Exception as e:
        logger.error(f"图片处理异常: {e}")
        return input_data


def get_zip_image_count(bookid: str) -> int:
    """
    获取ZIP文件中的图片数量，使用缓存
    """
    try:
        bookinfo = db.file.searchByid(bookid)
        if not bookinfo:
            return 0
        
        zip_path = Path(conf.get("file", "storedir")) / bookinfo[0][2]
        if not zip_path.exists():
            return 0
        
        image_files, _ = get_image_files_from_zip(str(zip_path))
        return len(image_files)
        
    except Exception as e:
        logger.error(f"获取图片数量失败 {bookid}: {e}")
        return 0
