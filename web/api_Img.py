from flask import *
from flask import Blueprint
import db.file , file, gc

api_Img_bp = Blueprint("api_Img_bp", __name__)


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
        data = file.thumbnail(data)
    else:
        data = file.thumbnail(data,1500)
    response = make_response(data)  # 读取文件
    del data
    response.headers.set("Content-Type", "image/Webp")
    response.headers.set("Content-Disposition", "inline", filename=filename)
    gc.collect()
    return response
