from flask import *
from flask import Blueprint
import time
import db.user
import db.file, file, app_conf

admin_page_bp = Blueprint("admin_page_bp", __name__)

conf = app_conf.conf()

# 管理页


@admin_page_bp.route("/", methods=["GET", "POST"])
def login():  # 登录页面
    if request.method == "GET":
        if request.cookies.get("islogin") is not None:
            return redirect("/overview/1")
        return render_template("login.html")
    elif request.method == "POST":
        if db.user.check(request.form["username"], request.form["password"]):
            resp = make_response(redirect("/overview/1"))
            resp.set_cookie("islogin", request.form["username"])
            resp.set_cookie("uid", str(db.user.getUid(request.form["username"])))
            return resp
        else:
            return redirect("/")