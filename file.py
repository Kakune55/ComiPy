import shutil, os, zipfile, io, cv2, numpy as np

import db.file, app_conf

app_conf = app_conf.conf()


def init():
    paths = ("inputdir", "storedir", "tmpdir")
    for path in paths:
        try:
            os.makedirs(app_conf.get("file", path))
        except Exception as e:
            print(e)


def auotLoadFile():
    fileList = os.listdir(app_conf.get("file", "inputdir"))
    for item in fileList:
        if zipfile.is_zipfile(
            app_conf.get("file", "inputdir") + "/" + item
        ):  # 判断是否为压缩包
            with zipfile.ZipFile(
                app_conf.get("file", "inputdir") + "/" + item, "r"
            ) as zip_ref:
                db.file.new(item, len(zip_ref.namelist()))  # 添加数据库记录 移动到存储
            shutil.move(
                app_conf.get("file", "inputdir") + "/" + item,
                app_conf.get("file", "storedir") + "/" + item,
            )
            print("已添加 " + item)
        else:
            print("不符合条件 " + item)


def raedZip(bookid: str, index: int):
    bookinfo = db.file.searchByid(bookid)
    zippath = app_conf.get("file", "storedir") + "/" + bookinfo[0][2]

    try:
        # 创建一个ZipFile对象
        with zipfile.ZipFile(zippath, "r") as zip_ref:
            # 获取图片文件列表
            image_files = [
                file
                for file in zip_ref.namelist()
                if file.lower().endswith((".png", ".jpg", ".jpeg"))
            ]

            if not image_files:
                return "not imgfile in zip", ""

            if int(index) > len(image_files):
                return "404 not found", ""

            # 假设我们只提取图片文件
            image_filename = image_files[int(index)]

            # 读取图片数据
            image_data = zip_ref.read(image_filename)
            zip_ref.close()
            return image_data, image_filename

    except zipfile.BadZipFile:  # 异常处理
        return "Bad ZipFile", ""
    except Exception as e:
        return str(e), ""


def thumbnail(input, minSize: int = 600):
    img = cv2.imdecode(np.frombuffer(input, np.uint8), cv2.IMREAD_COLOR)
    height = img.shape[0]  # 图片高度
    width = img.shape[1]  # 图片宽度
    if height > width:
        newshape = (minSize, int(minSize / width * height))
    else:
        newshape = (int(minSize / height * width), minSize)
    img = cv2.resize(img, newshape)
    success, encoded_image = cv2.imencode(".webp", img, [cv2.IMWRITE_WEBP_QUALITY, 75])
    return encoded_image.tobytes()
