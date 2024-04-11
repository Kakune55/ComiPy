import shutil, os, configparser, zipfile, io
import db
from PIL import Image

config = configparser.ConfigParser()
config.read("./conf/app.ini")


def init():
    try:
        os.makedirs(config.get("file", "inputdir"))
        os.makedirs(config.get("file", "storedir"))
        os.makedirs(config.get("file", "tmpdir"))
    except:
        pass


def auotLoadFile():
    fileList = os.listdir(config.get("file", "inputdir"))
    for item in fileList:
        if zipfile.is_zipfile(
            config.get("file", "inputdir") + "/" + item
        ):  # 判断是否为压缩包
            with zipfile.ZipFile(
                config.get("file", "inputdir") + "/" + item, "r"
            ) as zip_ref:
                db.newFile(item, len(zip_ref.namelist()))  # 添加数据库记录 移动到存储
            shutil.move(
                config.get("file", "inputdir") + "/" + item,
                config.get("file", "storedir") + "/" + item,
            )
            print("已添加 " + item)
        else:
            print("不符合条件 " + item)


def raedZip(bookid: str, index: int):
    bookinfo = db.searchByid(bookid)
    zippath = config.get("file", "storedir") + "/" + bookinfo[0][2]

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
            return image_data, image_filename

    except zipfile.BadZipFile:  # 异常处理
        return "Bad ZipFile", ""
    except Exception as e:
        return str(e), ""


def thumbnail(input,size=(400,800)):
    im = Image.open(io.BytesIO(input))
    del input
    im = im.convert('RGB')
    im.thumbnail(size)
    output_io = io.BytesIO()
    im.save(output_io,format='WEBP')
    output_io.seek(0)
    return output_io

def imageToWebP(input):
    im = Image.open(io.BytesIO(input))
    del input
    im = im.convert('RGB')
    output_io = io.BytesIO()
    im.save(output_io,format='WEBP')
    output_io.seek(0)
    return output_io
    
    
