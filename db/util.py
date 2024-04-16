import sqlite3, configparser
import app_conf

conf = app_conf.conf()


def getConn():
    return sqlite3.connect(conf.get("database", "path"))


def init():
    conn = getConn()
    c = conn.cursor()
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS Metadata  (
    num INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,
    filename TEXT NOT NULL,
    pagenumber INT NOT NULL,
    inputtime INT NOT NULL
    );
    """
    )
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS User  (
    uid INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
    );
    """
    )
    conn.commit()
    conn.close()
