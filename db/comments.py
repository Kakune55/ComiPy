import time
import db.util as util


# 查找评论
def listByBookid(id: str):
    "通过bookid查找所有评论"
    conn = util.getConn()
    c = conn.cursor()
    cursor = c.execute("SELECT * FROM Comments WHERE bookid = ? ORDER BY time desc", (id,))
    out = []
    for row in cursor:
        out.append(row)
    conn.close()
    return out


# 获取综合评分
def getScore(bookid: str):
    "获取综合评分 返回一个字典 字典有两个key like和dislike分别记录不同评论的个数"
    conn = util.getConn()
    c = conn.cursor()
    cursor = c.execute("SELECT * FROM Comments WHERE bookid = ? ", (bookid,))
    num={'like':0,'dislike':0}
    for row in cursor:
        if row[4] == "like":
            num["like"]+=1
        elif row[4] == "dislike":
            num["dislike"]+=1
    conn.close()
    return num


# 查找评论
def searchByUid(uid: str):
    "通过用户查找所有评论"
    conn = util.getConn()
    c = conn.cursor()
    cursor = c.execute("SELECT * FROM Comments WHERE from_uid = ? ORDER BY time desc", (uid,))
    out = []
    for row in cursor:
        out.append(row)
    conn.close()
    return out


# 查找评论
def searchByAll(uid: str,bookid:str):
    "通过用户和BookID查找所有评论"
    conn = util.getConn()
    c = conn.cursor()
    cursor = c.execute("SELECT * FROM Comments WHERE from_uid = ? AND bookid= ? ORDER BY time desc", (uid,bookid))
    out = []
    for row in cursor:
        out.append(row)
    conn.close()
    return out


# 在数据库中添加一个新的文件记录
def new(bookid: str, from_uid: int, score: str, content=""):
    "添加一条新评论 score字段可选值为[like,none,dislike] content字段非必填"
    conn = util.getConn()
    c = conn.cursor()
    c.execute(
        """
    INSERT INTO Comments 
    (time, bookid, from_uid, score, content) 
    VALUES 
    (?, ?, ?, ?,?);
    """,
        (int(time.time()), bookid, from_uid, score, content),
    )
    conn.commit()
    conn.close()
    return
