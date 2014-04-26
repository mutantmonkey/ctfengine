import datetime
import hashlib
from ctfengine import config
from ctfengine import db
from ctfengine.models import Handle


class FlagEntry(db.Model):
    __tablename__ = "flag_entries"
    id = db.Column(db.Integer, primary_key=True)
    handle = db.Column(db.Integer, db.ForeignKey('handles.id'))
    flag = db.Column(db.Integer, db.ForeignKey('flags.id'))
    datetime = db.Column(db.DateTime(), default=datetime.datetime.now)
    ip = db.Column(db.String(255))
    user_agent = db.Column(db.Unicode(255))

    def __init__(self, handle, flag, ip="", user_agent=""):
        self.handle = handle
        self.flag = flag
        self.ip = ip
        self.user_agent = user_agent

    def __repr__(self):
        return '<FlagEntry: {0:d}: {1}: {2}>'.format(self.handle,
                                                     self.flag,
                                                     self.datetime)

    def serialize(self, flag=None):
        data = {
            'handle': self.handle,
            'flag': self.flag,
            'datetime': self.datetime,
        }
        if flag:
            data.update(flag.serialize())
        return data


class Flag(db.Model):
    __tablename__ = "flags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.UnicodeText())
    flag = db.Column(db.String(128), index=True, unique=True, nullable=False)
    points = db.Column(db.Integer)
    machine = db.Column(db.Integer, db.ForeignKey('machines.id'))

    def __init__(self, name, flag, points):
        h = hashlib.sha512()
        h.update(flag + ctfengine.config.SALT)

        self.name = name
        self.flag = h.hexdigest()
        self.points = points

    @staticmethod
    def get(flag):
        h = hashlib.sha512()
        h.update(flag + config.SALT)
        return Flag.query.filter(Flag.flag == h.hexdigest()).first()

    @staticmethod
    def total_points():
        return db.session.query(db.func.sum(Flag.points)).first()[0] or 0

    def __repr__(self):
        return '<Flag: {0}: {1:d}>'.format(self.name, self.points)

    def serialize(self):
        return {
            'name': self.name,
            'points': self.points,
        }


class Machine(db.Model):
    __tablename__ = "machines"
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(255))
    dirty = db.Column(db.Boolean, default=False)

    def __init__(self, hostname):
        self.hostname = hostname

    def __repr__(self):
        return '<Machine: {0}>'.format(self.hostname)

    def serialize(self):
        return {
            'hostname': self.hostname,
            'dirty': self.dirty,
        }
