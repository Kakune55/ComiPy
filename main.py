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



@app.route("/overview/<page>")
def overview(page):  # 概览
    page = int(page)
    if request.cookies.get("islogin") is None:
        return redirect("/")
    metaDataList = db.getMetadata((page - 1) * 20, page * 20)
    if page <= 3:
        lastPageList = range(1,page)
    else:
        lastPageList = range(page-3,page)
    nextPageList = range(page+1,page+4)
    return render_template("overview.html",list=metaDataList,lastPageList=lastPageList,pagenow=page,nextPageList=nextPageList)


# @app.route("/api/info") 暂时弃用
# def api():  # 接口
#     if request.cookies.get("islogin") is None:
#         return abort(403)
#     func = request.args.get("func")
#     if func == "bookname" and request.args.get("page") is not None:
#         page = int(request.args.get("page"))
#         return db.getMetadata((page - 1) * 20, page * 20)

#     return abort(400)


@app.route("/api/img/<bookid>/<index>")
def img(bookid, index):  # 图片接口
    if request.cookies.get("islogin") is None:
        return abort(403)
    if db.searchByid(bookid) == "":
        return jsonify({'message': 'No ZIP file part'}), 400
    # 设置响应类型为图片
    data, filename = file.raedZip(bookid,index)
    if isinstance(data, str):
        abort(404)
    response = make_response(data) #读取文件
    response.headers.set('Content-Type', 'image/{}'.format(filename.split('.')[-1]))
    response.headers.set('Content-Disposition', 'inline', filename=filename)
    return response


@app.route("/book/<bookid>")
def book(bookid):  # 接口
    if request.cookies.get("islogin") is None:
        return abort(403)
    return render_template("view.html",data = bookid)


@app.route("/view/<bookid>")
def view(bookid):  # 接口
    if request.cookies.get("islogin") is None:
        return abort(403)
    return bookid


@app.route('/upload', methods=["GET", "POST"]) #文件上传
def upload_file():
    if request.method == "GET":
        return render_template("upload.html")
    uploaded_file = request.files.getlist('files[]')  # 获取上传的文件列表
    for fileitem in uploaded_file:
        if fileitem.filename != '':
            fileitem.save(config.get("file", "inputdir") + "/" + fileitem.filename)
    file.auotLoadFile()
    return redirect("/")


if __name__ == "__main__":
    appinit()
    app.run(
        debug=config.get("server", "debug"),
        host=config.get("server", "host"),
        port=config.get("server", "port"),
    )
