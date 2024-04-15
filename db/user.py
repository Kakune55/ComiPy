import sqlite3, configparser
import db.util as util

config = configparser.ConfigParser()
config.read("./conf/app.ini")


def getConn():
    return sqlite3.connect(config.get("database", "path"))


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