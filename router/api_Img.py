from flask import *
from flask import Blueprint
import db.file , file, gc , app_conf

api_Img_bp = Blueprint("api_Img_bp", __name__)

conf = app_conf.conf()
imgencode = conf.get("img", "encode")
miniSize = conf.getint("img", "miniSize")
fullSize = conf.getint("img", "fullSize")

@api_Img_bp.route("/api/img/<bookid>/<index>")
def img(bookid, index):  # 图片接口
    if request.cookies.get("islogin") is None:
        return abort(403)
    if len(db.file.searchByid(bookid)) == 0:
        return abort(404)
    # 设置响应类型为图片
    data, filename = file.raedZip(bookid, index)
    if isinstance(data, str):
        abort(404)
    if request.args.get("mini") == "yes":
        data = file.thumbnail(data,miniSize,encode=imgencode)
    else:
        data = file.thumbnail(data,fullSize,encode=imgencode)
    response = make_response(data)  # 读取文件
    del data
    response.headers.set("Content-Type",f"image/{imgencode}")
    response.headers.set("Content-Disposition", "inline", filename=filename)
    gc.collect()
    return response
