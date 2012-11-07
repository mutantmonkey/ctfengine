from sqlalchemy import Column, ForeignKey, Integer, String, UnicodeText, \
        DateTime, Unicode, desc, func
import datetime
import hashlib

import ctfengine.config
import ctfengine.database


class FlagEntry(ctfengine.database.Base):
    __tablename__ = "flag_entries"
    id = Column(Integer, primary_key=True)
    handle = Column(Integer, ForeignKey('handles.id'))
    flag = Column(Integer, ForeignKey('flags.id'))
    datetime = Column(DateTime(), default=datetime.datetime.now)
    ip = Column(String(255))
    user_agent = Column(Unicode(255))

    def __init__(self, handle, flag, ip="", user_agent=""):
        self.handle = handle
        self.flag = flag
        self.ip = ip
        self.user_agent = user_agent

    def __repr__(self):
        return '<FlagEntry: {0:d}: {1}: {2}>'.format(self.handle,
                self.flag.name, self.datetime)

    def serialize(self):
        return {
            'handle': self.handle,
            'flag_name': self.flag.name,
            'datetime': str(self.datetime),
        }


class Handle(ctfengine.database.Base):
    __tablename__ = "handles"
    id = Column(Integer, primary_key=True)
    handle = Column(UnicodeText())
    score = Column(Integer)

    def __init__(self, handle, score):
        self.handle = handle
        self.score = score

    @staticmethod
    def get(handle):
        return Handle.query.filter(Handle.handle == handle).first()

    @staticmethod
    def topscores(lim=25):
        return Handle.query.order_by(desc(Handle.score)).limit(lim)

    def __repr__(self):
        return '<Handle: {0}: {1:d}>'.format(self.handle, self.score)

    def serialize(self):
        return {
            'handle': self.handle,
            'score': self.score,
        }


class Flag(ctfengine.database.Base):
    __tablename__ = "flags"
    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText())
    flag = Column(String(128), index=True, nullable=False)
    points = Column(Integer)

    def __init__(self, name, flag, points):
        h = hashlib.sha512()
        h.update(flag + ctfengine.config.SALT)

        self.name = name
        self.flag = h.hexdigest()
        self.points = points

    @staticmethod
    def get(flag):
        h = hashlib.sha512()
        h.update(flag + ctfengine.config.SALT)
        return Flag.query.filter(Flag.flag == h.hexdigest()).first()

    @staticmethod
    def total_points():
        return func.sum(Flag.points)

    def __repr__(self):
        return '<Flag: {0}: {2:d}>'.format(self.name, self.points)

    def serialize(self):
        return {
            'name': self.name,
            'flag': self.flag,
            'points': self.points,
        }
