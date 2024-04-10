import sqlite3, configparser, shortuuid

config = configparser.ConfigParser()
config.read("./conf/app.ini")


def getConn():
    return sqlite3.connect(config.get("database", "path"))


def init():
    conn = getConn()
    c = conn.cursor()
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS Metadata  (
    num INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,
    filename TEXT NOT NULL,
    pagenumber INT NOT NULL
    );
    """
    )
    conn.commit()
    conn.close()


# 查找文件信息
def searchByid(id: str):
    conn = getConn()
    c = conn.cursor()
    cursor = c.execute("SELECT * FROM Metadata WHERE id = ?", (id,))
    out = []
    for row in cursor:
        out.append(row)
    conn.close()
    return out


# 查找文件信息
def searchByFilename(filename: str):
    conn = getConn()
    c = conn.cursor()
    cursor = c.execute("SELECT * FROM Metadata WHERE filename = ?", (filename,))
    out = []
    for row in cursor:
        out.append(row)
    conn.close()
    return out


# 在数据库中添加一个新的文件记录
def newFile(filename: str, pagenumber:int):
    suuid = shortuuid.random(8)
    conn = getConn()
    c = conn.cursor()
    c.execute(
        """
    INSERT INTO Metadata 
    (id, filename, pagenumber) 
    VALUES 
    (?, ?, ?);
    """,
        (suuid, filename, pagenumber),
    )
    conn.commit()
    conn.close()
    return suuid


# 获取文件元数据
def getMetadata(form: int, num: int):
    conn = getConn()
    c = conn.cursor()
    cursor = c.execute(
        "SELECT * FROM Metadata ORDER BY num desc LIMIT ?, ?", (form, num)
    )
    out = []
    for row in cursor:
        out.append(list(row))
    conn.close()
    return out

