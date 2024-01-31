from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float,
)
from extension import db


class User(db.Model):
    uid = Column(Integer, primary_key=True)
    username = Column(String(10))
    password = Column(String(10))
    tele = Column(String(20))

    @staticmethod
    def _init_db():
        rets = [
            (0, "admin", "admin", "13812341234"),
            (1, "user1", "user1", "15500000000"),
        ]
        for ret in rets:
            U = User()
            U.uid = ret[0]
            U.username = ret[1]
            U.password = ret[2]
            U.tele = ret[3]
            db.session.add(U)
        db.session.commit()


class Record(db.Model):
    timestamp = Column(DateTime, primary_key=True)
    uid = Column(Integer)
    duration = Column(Integer)
    label = Column(String(5))  # 分类
    level = Column(Integer)  # 分级
    texture_level = Column(Integer)  # 纹理
    coloration = Column(String(10))  # 着色度
    defect_num = Column(Integer)
    defect_ratio = Column(String(10))  # 缺陷面积比
    aspect_ratio = Column(String(10))  # 长宽比

    @staticmethod
    def _init_db():
        pass
