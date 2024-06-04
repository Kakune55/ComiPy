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
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS Comments  (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time INT NOT NULL,
    bookid TEXT NOT NULL,
    from_uid INTEGAR NOT NULL,
    score INT NOT NULL,
    content TEXT
    );
    """
    )
    c.execute(
        """
    INSERT INTO User (username, password) 
    SELECT ?, ?
    WHERE NOT EXISTS (SELECT 1 FROM User WHERE username = ?);
    """,
        (
            conf.get("user", "username"),
            conf.get("user", "password"),
            conf.get("user", "username"),
        ),
    )
    conn.commit()
    conn.close()
