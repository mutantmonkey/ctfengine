from sqlalchemy import Column, ForeignKey, Integer, String, UnicodeText, \
        DateTime, desc
import datetime
import hashlib

import ctfengine.database


class FlagEntry(ctfengine.database.Base):
    __tablename__ = "flag_entries"
    id = Column(Integer, primary_key=True)
    handle = Column(Integer, ForeignKey('handles.id'))
    hostname = Column(UnicodeText())
    datetime = Column(DateTime(), default=datetime.datetime.now)

    def __init__(self, handle, hostname):
        self.handle = handle
        self.hostname = hostname

    def __repr__(self):
        return '<FlagEntry: {0:d}: {1}: {2}>'.format(self.handle,
                self.hostname, self.datetime)

    def serialize(self):
        return {
            'handle': self.handle,
            'hostname': self.hostname,
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
    hostname = Column(UnicodeText())
    ip = Column(String)
    flag = Column(String(128), index=True, nullable=False)
    points = Column(Integer)

    def __init__(self, hostname, ip, flag, points):
        h = hashlib.sha512()
        h.update(flag)

        self.hostname = hostname
        self.ip = ip
        self.flag = h.hexdigest()
        self.points = points

    @staticmethod
    def get(flag):
        h = hashlib.sha512()
        h.update(flag)
        return Flag.query.filter(Flag.flag == h.hexdigest()).first()

    def __repr__(self):
        return '<Flag: {0}: {1}: {2:d}>'.format(self.hostname, self.ip,
                self.points)

    def serialize(self):
        return {
            'hostname': self.handle,
            'ip': self.ip,
            'flag': self.flag,
            'points': self.points,
        }
