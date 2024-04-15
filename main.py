import configparser
import db.util
import db.file, file
from flask import *

from web.api_Img import api_Img_bp
from web.page import page_bp

app = Flask(__name__)

config = configparser.ConfigParser()
config.read("./conf/app.ini")


def appinit():
    file.init()
    db.util.init()
    file.auotLoadFile()


app.register_blueprint(api_Img_bp)
app.register_blueprint(page_bp)

if __name__ == "__main__":
    appinit()
    app.run(
        debug=config.get("server", "debug"),
        host=config.get("server", "host"),
        port=config.get("server", "port"),
    )
