import sqlite3, configparser
import db.util as util, app_conf

conf = app_conf.conf()


def getConn():
    return sqlite3.connect(conf.get("database", "path"))


def new(username: str, password: int):
    "新建用户"
    conn = util.getConn()
    c = conn.cursor()
    c.execute(
        """
    INSERT INTO User 
    (username, password) 
    VALUES 
    (?, ?);
    """,
        (username, password),
    )
    conn.commit()
    conn.close()


def check(username: str, password: int):
    "判断用户信息是否正确"
    conn = util.getConn()
    c = conn.cursor()
    cursor = c.execute("SELECT * FROM User WHERE username = ? AND password = ?", (username, password))
    if cursor.fetchone() is None:
        return False
    return True

def getUid(username: str):
    "判断用户名是否存在 并获取用户uid 用户不存在则返回None"
    conn = util.getConn()
    c = conn.cursor()
    cursor = c.execute("SELECT * FROM User WHERE username = ?", (username,))
    out = cursor.fetchone()
    if out is not None:
        return out[0]
    return None

def getUsername(uid:str):
    "判断Uid是否存在 并获取用户名 用户不存在则返回None"
    conn = util.getConn()
    c = conn.cursor()
    cursor = c.execute("SELECT * FROM User WHERE uid = ?", (uid,))
    out = cursor.fetchone()
    if out is not None:
        return out[1]
    return None