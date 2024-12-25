import shortuuid, time
import db.util as util


# 查找文件信息
def searchByid(id: str):
    conn = util.getConn()
    c = conn.cursor()
    cursor = c.execute("SELECT * FROM Metadata WHERE id = ?", (id,))
    out = []
    for row in cursor:
        out.append(row)
    conn.close()
    return out


# 查找文件信息
def searchByname(filename: str):
    conn = util.getConn()
    c = conn.cursor()
    cursor = c.execute("SELECT * FROM Metadata WHERE filename = ?", (filename,))
    out = []
    for row in cursor:
        out.append(row)
    conn.close()
    return out


# 在数据库中添加一个新的文件记录
def new(filename: str, pagenumber:int):
    suuid = shortuuid.random(8)
    conn = util.getConn()
    c = conn.cursor()
    c.execute(
        """
    INSERT INTO Metadata 
    (id, filename, pagenumber, inputtime) 
    VALUES 
    (?, ?, ?, ?);
    """,
        (suuid, filename, pagenumber, int(time.time())),
    )
    conn.commit()
    conn.close()
    return suuid


# 获取文件元数据
def getMetadata(form: int, num: int, search:str = None):
    conn = util.getConn()
    c = conn.cursor()
    if search == None:
        cursor = c.execute(
            "SELECT * FROM Metadata ORDER BY num desc LIMIT ?, ?", (form, num)
        )
    else:
        cursor = c.execute(
            "SELECT * FROM Metadata WHERE filename LIKE ? ORDER BY num desc LIMIT ?, ?", (f"%{search}%", form, num)
        )
    out = []
    for row in cursor:
        out.append(list(row))
    conn.close()
    return out
