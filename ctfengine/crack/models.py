from sqlalchemy import Column, ForeignKey, Integer, String, Text, \
        UnicodeText, DateTime, Unicode, Boolean, desc, func
import base64
import datetime
import ctfengine.config
import ctfengine.database
from ctfengine.models import Handle

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


class Password(ctfengine.database.Base):
    __tablename__ = "passwords"
    id = Column(Integer, primary_key=True)
    algo = Column(String(64))
    password = Column(String, index=True, unique=True, nullable=False)
    points = Column(Integer)

    def __init__(self, algo, password, points):
        self.algo = algo
        self.password = password
        self.points = points

    @staticmethod
    def get(password):
        return Password.query.filter(Password.password == password).first()

    @staticmethod
    def total_points():
        return func.sum(Password.points)

    def __repr__(self):
        return '<Password: {0}: {1}: {2:d}>'.format(self.algo, self.password,
                self.points)

    def serialize(self):
        return {
            'algo': self.algo,
            'password': self.password,
            'points': self.points,
        }


class PasswordEntry(ctfengine.database.Base):
    __tablename__ = "password_entries"
    id = Column(Integer, primary_key=True)
    handle = Column(Integer, ForeignKey('handles.id'))
    password = Column(Integer, ForeignKey('passwords.id'))
    plaintext = Column(Text)
    datetime = Column(DateTime(), default=datetime.datetime.now)
    ip = Column(String(255))
    user_agent = Column(Unicode(255))

    def __init__(self, handle, password, plaintext, ip="", user_agent=""):
        self.handle = handle
        self.password = password
        self.ip = ip
        self.user_agent = user_agent

        # encrypt the plaintext password before storing
        key = RSA.importKey(open(ctfengine.config.ENCRYPT_KEYFILE).read())
        cipher = PKCS1_OAEP.new(key)
        self.plaintext = base64.b64encode(
                cipher.encrypt(plaintext.encode('utf-8')))

    def __repr__(self):
        return '<PasswordEntry: {0:d}: {1}: {2}>'.format(self.handle,
                self.password.password, self.datetime)

    def serialize(self):
        return {
            'handle': self.handle,
            'password': self.password,
            'datetime': str(self.datetime),
        }
