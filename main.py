import app_conf
import db.util
import db.file, file
from flask import *

from router.api_Img import api_Img_bp
from router.page import page_bp
from router.admin_page import admin_page_bp
from router.api_comment import comment_api_bp

app = Flask(__name__)

conf = app_conf.conf()

def appinit():
    file.init()
    db.util.init()
    file.auotLoadFile()


app.register_blueprint(api_Img_bp)
app.register_blueprint(page_bp)
app.register_blueprint(admin_page_bp)
app.register_blueprint(comment_api_bp)

if __name__ == "__main__":
    appinit()
    app.run(
        debug=conf.getboolean("server", "debug"),
        host=conf.get("server", "host"),
        port=conf.get("server", "port"),
        threaded=conf.getboolean("server", "threaded"),
    )
