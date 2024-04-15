from flask import *
from flask import Blueprint
import configparser
import db, file

page_bp = Blueprint("page_bp", __name__)

config = configparser.ConfigParser()
config.read("./conf/app.ini")


@page_bp.route("/overview/<page>")
def overview(page):  # 概览
    page = int(page)
    if request.cookies.get("islogin") is None:
        return redirect("/")
    metaDataList = db.getMetadata((page - 1) * 20, page * 20)
    if page <= 3:
        lastPageList = range(1, page)
    else:
        lastPageList = range(page - 3, page)
    nextPageList = range(page + 1, page + 4)
    return render_template(
        "overview.html",
        list=metaDataList,
        lastPageList=lastPageList,
        pagenow=page,
        nextPageList=nextPageList,
    )


@page_bp.route("/book/<bookid>")
def book(bookid):  # 接口
    if request.cookies.get("islogin") is None:
        return abort(403)
    data = db.searchByid(bookid)
    if data == "":
        return abort(404)
    return render_template("view.html", id=bookid, index=range(1, data[0][3]))


@page_bp.route("/view/<bookid>")
def view(bookid):  # 接口
    if request.cookies.get("islogin") is None:
        return abort(403)
    return bookid


@page_bp.route("/upload", methods=["GET", "POST"])  # 文件上传
def upload_file():
    if request.method == "GET":
        return render_template("upload.html")
    uploaded_file = request.files.getlist("files[]")  # 获取上传的文件列表
    for fileitem in uploaded_file:
        if fileitem.filename != "":
            fileitem.save(config.get("file", "inputdir") + "/" + fileitem.filename)
    file.auotLoadFile()
    return redirect("/")


@page_bp.route("/", methods=["GET", "POST"])
def login():  # 登录页面
    if request.method == "GET":
        if request.cookies.get("islogin") is not None:
            return redirect("/overview/1")
        return render_template("login.html")
    elif request.method == "POST":
        if request.form["username"] == config.get("user", "username") and request.form[
            "password"
        ] == config.get("user", "password"):
            resp = make_response(redirect("/overview/1"))
            resp.set_cookie("islogin", "True")
            return resp
        else:
            return redirect("/")