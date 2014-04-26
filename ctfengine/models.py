from ctfengine import db


class Handle(db.Model):
    __tablename__ = "handles"
    id = db.Column(db.Integer, primary_key=True)
    handle = db.Column(db.UnicodeText())
    score = db.Column(db.Integer)

    def __init__(self, handle, score):
        self.handle = handle
        self.score = score

    @staticmethod
    def get(handle):
        return Handle.query.filter(Handle.handle == handle).first()

    @staticmethod
    def top_scores(lim=25):
        return Handle.query.order_by(db.desc(Handle.score)).limit(lim)

    def __repr__(self):
        return '<Handle: {0}: {1:d}>'.format(self.handle, self.score)

    def serialize(self):
        return {
            'handle': self.handle,
            'score': self.score,
        }
