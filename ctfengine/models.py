from sqlalchemy import Column, ForeignKey, Integer, UnicodeText, DateTime, desc
import datetime

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
