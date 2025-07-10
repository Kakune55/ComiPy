from flask import Blueprint, render_template, jsonify, request
from utils.performance_monitor import get_performance_monitor
from utils.cache_manager import get_cache_manager

performance_bp = Blueprint("performance_bp", __name__)


@performance_bp.route("/api/performance/stats")
def performance_stats():
    """获取性能统计信息"""
    if request.cookies.get("islogin") is None:
        return jsonify({"error": "Unauthorized"}), 403
    
    monitor = get_performance_monitor()
    cache_manager = get_cache_manager()
    
    operation_name = request.args.get("operation")
    
    stats = {
        "performance": monitor.get_stats(operation_name),
        "cache": cache_manager.get_stats(),
        "recent_errors": monitor.get_recent_errors(5)
    }
    
    return jsonify(stats)


@performance_bp.route("/api/performance/clear")
def clear_performance_data():
    """清空性能监控数据"""
    if request.cookies.get("islogin") is None:
        return jsonify({"error": "Unauthorized"}), 403
    
    monitor = get_performance_monitor()
    monitor.clear_metrics()
    
    return jsonify({"message": "Performance data cleared"})


@performance_bp.route("/api/cache/clear")
def clear_cache():
    """清空缓存"""
    if request.cookies.get("islogin") is None:
        return jsonify({"error": "Unauthorized"}), 403
    
    cache_manager = get_cache_manager()
    cache_manager.clear()
    
    return jsonify({"message": "Cache cleared"})


@performance_bp.route("/api/cache/cleanup")
def cleanup_cache():
    """清理过期缓存"""
    if request.cookies.get("islogin") is None:
        return jsonify({"error": "Unauthorized"}), 403
    
    cache_manager = get_cache_manager()
    cache_manager.cleanup_expired()
    
    return jsonify({"message": "Expired cache cleaned up"})
