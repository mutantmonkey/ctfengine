from sqlalchemy import Column, ForeignKey, Integer, String, UnicodeText, \
        DateTime, Unicode, Boolean, desc, func
import datetime
import hashlib
import ctfengine.config
import ctfengine.database
from ctfengine.models import Handle


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


class Flag(ctfengine.database.Base):
    __tablename__ = "flags"
    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText())
    flag = Column(String(128), index=True, unique=True, nullable=False)
    points = Column(Integer)
    machine = Column(Integer, ForeignKey('machines.id'))

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
        return '<Flag: {0}: {1:d}>'.format(self.name, self.points)

    def serialize(self):
        return {
            'name': self.name,
            'flag': self.flag,
            'points': self.points,
        }


class Machine(ctfengine.database.Base):
    __tablename__ = "machines"
    id = Column(Integer, primary_key=True)
    hostname = Column(String(255))
    dirty = Column(Boolean, default=False)

    def __init__(self, hostname):
        self.hostname = hostname

    def __repr__(self):
        return '<Machine: {0}>'.format(self.hostname)

    def serialize(self):
        return {
            'hostname': self.hostname,
            'dirty': self.dirty,
        }
