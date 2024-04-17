import app_conf
import db.util
import db.file, file
from flask import *

from web.api_Img import api_Img_bp
from web.page import page_bp
from web.admin_page import admin_page_bp

app = Flask(__name__)

conf = app_conf.conf()

def appinit():
    file.init()
    db.util.init()
    file.auotLoadFile()


app.register_blueprint(api_Img_bp)
app.register_blueprint(page_bp)
app.register_blueprint(admin_page_bp)

if __name__ == "__main__":
    appinit()
    app.run(
        debug=conf.getboolean("server", "debug"),
        host=conf.get("server", "host"),
        port=conf.get("server", "port"),
        threaded=conf.getboolean("server", "threaded"),
    )
