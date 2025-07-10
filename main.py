import app_conf
import db.util
import db.file, file
from flask import Flask

from router.api_Img import api_Img_bp
from router.page import page_bp
from router.admin_page import admin_page_bp
from router.api_comment import comment_api_bp
from router.performance_api import performance_bp
from utils.logger import setup_logging
from utils.performance_monitor import get_performance_monitor

app = Flask(__name__)
conf = app_conf.conf()

def appinit():
    """应用初始化，集成日志和性能监控"""
    # 设置日志
    setup_logging(app)
    
    # 初始化文件系统和数据库
    file.init()
    db.util.init()
    file.autoLoadFile()
    
    # 启动性能监控
    monitor = get_performance_monitor()
    app.logger.info("应用初始化完成，性能监控已启动")

# 注册蓝图
app.register_blueprint(api_Img_bp)
app.register_blueprint(page_bp)
app.register_blueprint(admin_page_bp)
app.register_blueprint(comment_api_bp)
app.register_blueprint(performance_bp)

if __name__ == "__main__":
    appinit()
    app.run(
        debug=conf.getboolean("server", "debug"),
        host=conf.get("server", "host"),
        port=int(conf.get("server", "port")),
        threaded=conf.getboolean("server", "threaded"),
    )
