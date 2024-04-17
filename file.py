import shutil, os, zipfile, io
import db.file, app_conf
from PIL import Image

app_conf = app_conf.conf()

def init():
    paths = ("inputdir","storedir","tmpdir")
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


def thumbnail(input,size=(420,600)):
    im = Image.open(io.BytesIO(input))
    del input
    newimg = im.convert('RGB')
    im.close()
    newimg.thumbnail(size)
    output_io = io.BytesIO()
    newimg.save(output_io,format='WEBP')
    newimg.close()
    output_io.seek(0)
    return output_io

def imageToWebP(input,size=(2100,3000)):
    with Image.open(io.BytesIO(input)) as img:
        newimg = img.convert('RGB')
        img.close()
        output_io = io.BytesIO()
        newimg.thumbnail(size)
        newimg.save(output_io,format='WEBP')
        newimg.close()
        output_io.seek(0)
    return output_io
    
    
