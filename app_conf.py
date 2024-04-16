import configparser , os

def conf():
    conf = configparser.ConfigParser()
    if os.path.exists('./conf/app.ini'):
        conf.read('./conf/app.ini')
    else:
        conf.read('./conf/app_d.ini')
    return conf