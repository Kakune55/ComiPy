from flask import *
from flask import Blueprint
import time
import db.comments, db.file, app_conf

comment_api_bp = Blueprint("comment_api_bp", __name__)

conf = app_conf.conf()


@comment_api_bp.route("/api/comment/upload", methods=["POST"])
def comment_api():  # 概览
    if request.cookies.get("islogin") is None:  # 验证登录状态
        return redirect("/")
    if request.form["score"] != "none" and request.form["text"].isspace():
        return "评论不能为空"
    if len(request.form["text"]) > 200:
        return "评论过长(需要小于200字)"
    if db.comments.searchByAll(request.cookies.get("uid"), request.form["bookid"]):
        return "你已经完成了评论 不可重复提交"
    db.comments.new(
        request.form["bookid"],
        request.cookies.get("uid"),
        request.form["score"],
        request.form["text"],
    )
    return redirect("/book/" + request.form["bookid"])

@comment_api_bp.route("/api/comment/remove")
def remove():  # 删除api
    if request.cookies.get("islogin") is None:  # 验证登录状态
        return abort(403)
    try:
        id = int(request.args.get("id"))
    except:
        return abort(400)
    commentInfo = db.comments.getById(id)
    if commentInfo is None:
        return abort(404)
    if int(request.cookies.get("uid")) == commentInfo[3]:
        if db.comments.remove(id):
            return "OK"
        return abort(404)
    return abort(400)
