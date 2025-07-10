from flask import Blueprint, request, abort, make_response
import db.file , file, gc , app_conf
from utils.performance_monitor import timing_context

api_Img_bp = Blueprint("api_Img_bp", __name__)

conf = app_conf.conf()
imgencode = conf.get("img", "encode")
miniSize = conf.getint("img", "miniSize")
fullSize = conf.getint("img", "fullSize")

@api_Img_bp.route("/api/img/<bookid>/<index>")
def img(bookid, index):  # 图片接口
    with timing_context(f"api.img.{bookid}.{index}"):
        if request.cookies.get("islogin") is None:
            return abort(403)
        if len(db.file.searchByid(bookid)) == 0:
            return abort(404)
        
        # 读取图片数据
        data, filename = file.readZip(bookid, index)
        if isinstance(data, str):
            abort(404)
        
        # 处理图片尺寸
        if request.args.get("mini") == "yes":
            data = file.thumbnail(data, miniSize, encode=imgencode)
        else:
            data = file.thumbnail(data, fullSize, encode=imgencode)
        
        # 创建响应
        response = make_response(data)
        del data  # 及时释放内存
        
        response.headers.set("Content-Type", f"image/{imgencode}")
        response.headers.set("Content-Disposition", "inline", filename=filename)
        response.headers.set("Cache-Control", "public, max-age=3600")  # 添加缓存头
        
        gc.collect()  # 强制垃圾回收
        return response
