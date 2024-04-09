import configparser, os
import db, file
from flask import *


config = configparser.ConfigParser()
config.read("./conf/app.ini")


app = Flask(__name__)


def appinit():
    file.init()
    db.init()
    file.auotLoadFile()


@app.route("/", methods=["GET", "POST"])
def login():  # 登录页面
    if request.method == "GET":
        if request.cookies.get("islogin") is not None:
            return redirect("/overview")
        return render_template("login.html")
    elif request.method == "POST":
        if request.form["username"] == config.get("user", "username") and request.form[
            "password"
        ] == config.get("user", "password"):
            resp = make_response(redirect("/overview"))
            resp.set_cookie("islogin", "True")
            return resp
        else:
            return redirect("/")


@app.route("/overview")
def overview():  # 概览
    if request.cookies.get("islogin") is None:
        return redirect("/")
    return config.get("server", "port")


@app.route("/api/info")
def api():  # 接口
    if request.cookies.get("islogin") is None:
        return abort(403)
    func = request.args.get("func")
    if func == "bookname" and request.args.get("page") is not None:
        page = int(request.args.get("page"))
        return db.getMetadata((page - 1) * 20, page * 20)

    return abort(400)


@app.route("/api/img")
def img():  # 图片接口
    if request.cookies.get("islogin") is None:
        return abort(403)
    return "Hello World"


@app.route("/book/<bookid>")
def book(bookid):  # 接口
    if request.cookies.get("islogin") is None:
        return abort(403)
    return bookid


@app.route("/view/<bookid>")
def view(bookid):  # 接口
    if request.cookies.get("islogin") is None:
        return abort(403)
    return bookid


if __name__ == "__main__":
    appinit()
    app.run(
        debug=config.get("server", "debug"),
        host=config.get("server", "host"),
        port=config.get("server", "port"),
    )
