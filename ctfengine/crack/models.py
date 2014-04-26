import base64
import datetime
from ctfengine import config
from ctfengine import db
from ctfengine.models import Handle

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


class Password(db.Model):
    __tablename__ = "passwords"
    id = db.Column(db.Integer, primary_key=True)
    algo = db.Column(db.String(64))
    password = db.Column(db.String, index=True, unique=True, nullable=False)
    points = db.Column(db.Integer)

    def __init__(self, algo, password, points):
        self.algo = algo
        self.password = password
        self.points = points

    @staticmethod
    def get(password):
        return Password.query.filter(Password.password == password).first()

    @staticmethod
    def total_points():
        return db.session.query(db.func.sum(Password.points)).first()[0] or 0

    def __repr__(self):
        return '<Password: {0}: {1}: {2:d}>'.format(self.algo, self.password,
                self.points)

    def serialize(self):
        return {
            'algo': self.algo,
            'password': self.password,
            'points': self.points,
        }


class PasswordEntry(db.Model):
    __tablename__ = "password_entries"
    id = db.Column(db.Integer, primary_key=True)
    handle = db.Column(db.Integer, db.ForeignKey('handles.id'))
    password = db.Column(db.Integer, db.ForeignKey('passwords.id'))
    plaintext = db.Column(db.Text)
    datetime = db.Column(db.DateTime(), default=datetime.datetime.now)
    ip = db.Column(db.String(255))
    user_agent = db.Column(db.Unicode(255))

    def __init__(self, handle, password, plaintext, ip="", user_agent=""):
        self.handle = handle
        self.password = password
        self.ip = ip
        self.user_agent = user_agent

        # encrypt the plaintext password before storing
        key = RSA.importKey(open(config.ENCRYPT_KEYFILE).read())
        cipher = PKCS1_OAEP.new(key)
        self.plaintext = base64.b64encode(
                cipher.encrypt(plaintext.encode('utf-8')))

    def __repr__(self):
        return '<PasswordEntry: {0:d}: {1}: {2}>'.format(self.handle,
                self.password, self.datetime)

    def serialize(self, pw=None):
        data = {
            'handle': self.handle,
            'password': self.password,
            'datetime': self.datetime,
        }
        if pw:
            data.update(pw.serialize())
        return data
