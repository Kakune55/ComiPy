from flask import *
from flask import Blueprint
import time
import db.file, file , app_conf

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
        if request.form["username"] == conf.get("user", "username") and request.form[
            "password"
        ] == conf.get("user", "password"):
            resp = make_response(redirect("/overview/1"))
            resp.set_cookie("islogin", "True")
            return resp
        else:
            return redirect("/")