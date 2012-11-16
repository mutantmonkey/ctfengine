from sqlalchemy import Column, ForeignKey, Integer, String, UnicodeText, \
        DateTime, Unicode, Boolean, desc, func

import ctfengine.config
import ctfengine.database


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
