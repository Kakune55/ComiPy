import shutil, os ,configparser
import db

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
        db.newFile(item)
        shutil.move(config.get("file", "inputdir")+"/"+item, config.get("file", "storedir")+"/"+item)
        print("已添加 "+item)
